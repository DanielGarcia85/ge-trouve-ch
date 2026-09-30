# scripts/mesures/bench_pipeline.py

"""
Mesure du pipeline de réponse — latence et RAM
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Mesurer la latence de bout en bout du pipeline de réponse sur la question type :
une exécution à froid puis trois à chaud, médiane. Lit le détail de génération
dans la métadonnée Ollama (chargement, évaluation, jetons). Archive la réponse et
ses fragments pour le mémoire. Relève enfin la RAM du pipeline chargé (Qwen, Gemma
et Chroma résidents) via `releve_ram.ps1`. Réutilise le pipeline de `repondre`,
sans le redéfinir.

Deux modes (même sortie, directement comparables)
─────────────────────────────────────────────────
  - défaut (appel direct, mesure de type étape 4.2) : le pipeline est appelé en direct,
    la réponse arrive d'un bloc ; pas de « premier mot ».
  - `--streaming` (mesure de type étape 4.5) : le pipeline est appelé comme le fait l'app
    (avec un callback de streaming), mais en direct dans ce processus, SANS lancer Streamlit ;
    on relève en plus le temps jusqu'au premier mot (la latence PERÇUE, durée du badge).

Comparer les deux modes valide que le streaming n'ajoute pas de surcoût (même temps
total) et isole ce que l'interface apporte (le premier mot en ~1 s).

Détail des mesures Ollama
─────────────────────────
Après la synthèse habituelle, un tableau détaille passe par passe tout ce que la
métadonnée de la réponse contient : durées (`total_duration`, `load_duration`,
`prompt_eval_duration`, `eval_duration`) et nombres de jetons. Attention aux noms :
l'intégration `ollama-haystack` renomme les compteurs de jetons au format OpenAI,
`prompt_eval_count` devient `usage.prompt_tokens` et `eval_count` devient
`usage.completion_tokens` ; les durées, elles, gardent leur nom d'origine. Le
compteur `prompt_eval_cached_count`, que l'API Ollama renvoie pourtant, est perdu
en chemin (il ne fait pas partie du modèle de réponse de la bibliothèque `ollama`)
et s'affiche donc « n/d ». Les grandeurs dérivées (débits de prefill et de
génération, part du prefill, temps passé hors d'Ollama) complètent le tableau.
"""

import argparse
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))
import config  # noqa: E402
import repondre as rp  # noqa: E402

RELEVE_RAM = RACINE / "scripts" / "mesures" / "releve_ram.ps1"
ARCHIVE = config.RESULTATS_DIR / "complet" / "reponse.md"

# Rempli par le callback de streaming (mode interface) au premier mot de chaque exécution ;
# remis à None avant chaque passe. En mode sans interface, il n'y a pas de callback, il reste None.
_premier = {"t": None}


def sur_jeton(chunk):
    """Horodate le premier mot reçu du générateur (mode interface uniquement)."""
    if _premier["t"] is None and (getattr(chunk, "content", "") or ""):
        _premier["t"] = time.perf_counter()


def une_execution(pipe, question, requete_instruite):
    """
    Exécute le pipeline une fois.

    Renvoie (temps total, temps jusqu'au premier mot ou None, réponse, fragments). Le temps
    jusqu'au premier mot n'est renseigné qu'en mode interface (callback de streaming actif).
    """
    _premier["t"] = None
    debut = time.perf_counter()
    resultat = pipe.run(
        {"embedder": {"text": requete_instruite}, "prompt_builder": {"question": question}},
        include_outputs_from={"retriever"},
    )
    total = time.perf_counter() - debut
    jusqu_premier = (_premier["t"] - debut) if _premier["t"] else None
    reply = resultat["generator"]["replies"][0]
    documents = resultat["retriever"]["documents"]
    return total, jusqu_premier, reply, documents


def archiver(question, reply, documents):
    """Écrit la réponse et ses fragments dans un fichier (matière pour le mémoire)."""
    lignes = [f"# Réponse — {question}", "", "## Réponse", "", reply.text, "", "## Fragments utilisés", ""]
    for doc in documents:
        lignes.append(f"- {doc.meta.get('url')}")
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def fmt(valeur):
    """Formate une durée en secondes, ou « n/a » si non mesurée."""
    return f"{valeur:.1f} s" if valeur is not None else "n/a (sans streaming)"


# ── Lecture des mesures Ollama ────────────────────────────────────────
# Tout est lu de façon défensive : un champ absent vaut None et s'affiche « n/d »
# sans faire échouer la mesure.

def _secondes(nanosecondes):
    """Convertit une durée Ollama (nanosecondes) en secondes, ou None si absente."""
    return nanosecondes / 1e9 if isinstance(nanosecondes, (int, float)) else None


def _rapport(numerateur, denominateur):
    """Division défensive : None si une valeur manque ou si le diviseur est nul."""
    if numerateur is None or not denominateur:
        return None
    return numerateur / denominateur


def _nb(valeur, decimales=2):
    """Formate un nombre à N décimales, « n/d » s'il n'a pas été mesuré."""
    return "n/d" if valeur is None else f"{valeur:.{decimales}f}"


def _ent(valeur):
    """Formate un entier, « n/d » s'il n'a pas été mesuré."""
    return "n/d" if valeur is None else str(valeur)


def _mediane(valeurs):
    """Médiane des valeurs réellement mesurées, en ignorant les manquantes."""
    mesurees = [v for v in valeurs if v is not None]
    return statistics.median(mesurees) if mesurees else None


def _jetons(meta, cle_ollama, cle_usage):
    """
    Lit un compteur de jetons, quel que soit le nom sous lequel il est exposé.

    L'intégration `ollama-haystack` déplace `eval_count` et `prompt_eval_count`
    sous `usage` (noms OpenAI). On regarde donc les deux formes plutôt que de
    présumer de celle que la version installée emploie.
    """
    valeur = meta.get(cle_ollama)
    if valeur is None:
        valeur = (meta.get("usage") or {}).get(cle_usage)
    return valeur if isinstance(valeur, int) else None


def mesures_detaillees(meta, total_chrono, jusqu_premier):
    """
    Extrait de la métadonnée Ollama toutes ses mesures, et en dérive les débits.

    `total_chrono` est la durée chronométrée par le script pour toute la passe ;
    la différence avec `total_duration` mesure ce qui se passe hors d'Ollama
    (encodage de la requête, recherche Chroma, surcoût Haystack).
    """
    total = _secondes(meta.get("total_duration"))
    prefill = _secondes(meta.get("prompt_eval_duration"))
    generation = _secondes(meta.get("eval_duration"))
    jetons_prompt = _jetons(meta, "prompt_eval_count", "prompt_tokens")
    jetons_reponse = _jetons(meta, "eval_count", "completion_tokens")
    part = _rapport(prefill, total)
    return {
        "total_duration": total,
        "load_duration": _secondes(meta.get("load_duration")),
        "prompt_eval_count": jetons_prompt,
        "prompt_eval_cached_count": meta.get("prompt_eval_cached_count"),
        "prompt_eval_duration": prefill,
        "eval_count": jetons_reponse,
        "eval_duration": generation,
        "debit_prefill": _rapport(jetons_prompt, prefill),
        "debit_generation": _rapport(jetons_reponse, generation),
        "part_prefill": None if part is None else part * 100,
        "hors_ollama": None if total is None else total_chrono - total,
        "premier_mot": jusqu_premier,
        "total_chrono": total_chrono,
    }


# Colonnes du tableau détaillé, dans l'ordre d'affichage.
ENTETES = (
    "total_duration (s)", "load_duration (s)", "prompt_eval_count", "dont en cache",
    "prompt_eval_duration (s)", "eval_count", "eval_duration (s)",
    "Débit prefill (jetons/s)", "Débit génération (jetons/s)", "Part prefill (%)",
    "Hors Ollama (s)", "1er mot chrono (s)", "Total chrono (s)",
)


def ligne_detaillee(passe, m):
    """Met en forme une passe en ligne de tableau Markdown."""
    cellules = [
        _nb(m["total_duration"]), _nb(m["load_duration"]),
        _ent(m["prompt_eval_count"]), _ent(m["prompt_eval_cached_count"]),
        _nb(m["prompt_eval_duration"]), _ent(m["eval_count"]), _nb(m["eval_duration"]),
        _nb(m["debit_prefill"], 1), _nb(m["debit_generation"], 1), _nb(m["part_prefill"], 1),
        _nb(m["hors_ollama"]), _nb(m["premier_mot"]), _nb(m["total_chrono"]),
    ]
    return f"| {passe} | " + " | ".join(cellules) + " |"


def mediane_des_passes(passes):
    """Médiane, champ par champ, d'une série de passes (les jetons restent entiers)."""
    entiers = ("prompt_eval_count", "prompt_eval_cached_count", "eval_count")
    milieu = {}
    for cle in passes[0]:
        valeur = _mediane([p[cle] for p in passes])
        milieu[cle] = int(valeur) if (valeur is not None and cle in entiers) else valeur
    return milieu


def main():
    """Mesure la latence (1 à froid, 3 à chaud), archive la réponse, relève la RAM."""
    parseur = argparse.ArgumentParser(description="Mesure de latence du pipeline de réponse.")
    parseur.add_argument(
        "--streaming", action="store_true",
        help="Appelle le pipeline en streaming (comme l'app, sans lancer Streamlit) ; "
             "ajoute le temps jusqu'au premier mot.",
    )
    args = parseur.parse_args()

    mode = "streaming (comme l'app)" if args.streaming else "appel direct"
    callback = sur_jeton if args.streaming else None
    pipe = rp.construire_pipeline(streaming_callback=callback)
    question = rp.QUESTION_DEFAUT
    requete_instruite = f"Instruct: {rp.TACHE}\nQuery:{question}"

    print(f"Mesure du pipeline — mode {mode} (1 à froid, 3 à chaud)...")
    froid = une_execution(pipe, question, requete_instruite)
    chauds = [une_execution(pipe, question, requete_instruite) for _ in range(3)]

    totaux_chaud = [c[0] for c in chauds]
    total_chaud = statistics.median(totaux_chaud)
    premiers_chaud = [c[1] for c in chauds if c[1] is not None]
    reply, documents = chauds[-1][2], chauds[-1][3]

    meta = reply.meta
    eval_s = meta.get("eval_duration", 0) / 1e9
    jetons = meta.get("usage", {}).get("completion_tokens", 0)
    charge_froid_s = froid[2].meta.get("load_duration", 0) / 1e9
    reste_chaud = max(total_chaud - eval_s, 0.0)

    print(f"\nQuestion : {question}\n")
    print("À froid (chargement des modèles inclus)")
    print(f"  temps jusqu'au premier mot : {fmt(froid[1])}")
    print(f"  temps total                : {fmt(froid[0])} pour {froid[2].meta.get('usage', {}).get('completion_tokens', 0)} jetons")
    print(f"  chargement de Gemma        : {charge_froid_s:.1f} s")

    detail_premier = " / ".join(fmt(c[1]) for c in chauds)
    detail_total = " / ".join(f"{c[0]:.1f}" for c in chauds)
    print("\nÀ chaud (modèles résidents, cas de la production sur VPS)")
    if premiers_chaud:
        print(f"  temps jusqu'au premier mot (3 passes / médiane) : {detail_premier}  ->  {fmt(statistics.median(premiers_chaud))}")
    else:
        print(f"  temps jusqu'au premier mot (3 passes / médiane) : {detail_premier}")
    print(f"  temps total (3 passes / médiane)                : {detail_total} s  ->  {total_chaud:.1f} s")
    print(f"  dont génération (eval Ollama)                   : {eval_s:.1f} s pour {jetons} jetons")
    print(f"  encodage requête + recherche (reste)            : ~{reste_chaud:.1f} s")

    # ── Tableau détaillé : toutes les mesures d'Ollama, passe par passe ───
    # Lecture du tableau : sur une question rejouée, Ollama réutilise le cache de prefill.
    # `prompt_eval_duration` s'effondre alors d'une passe à l'autre (le prompt n'est plus
    # relu, seulement rechargé), ce qui fait grimper artificiellement le débit de prefill des
    # passes à chaud. Selon la version d'Ollama, `prompt_eval_count` peut lui aussi tomber à
    # la seule part non mise en cache ; sur la version mesurée ici il reste complet, et c'est
    # `prompt_eval_cached_count` qui porte la part servie par le cache (mais l'intégration
    # Haystack ne le transmet pas : voir l'entête). Dans tous les cas, seule la passe à froid,
    # ou une question nouvelle, donne un temps de prefill représentatif d'un vrai premier appel.
    detail = [("à froid", mesures_detaillees(froid[2].meta, froid[0], froid[1]))]
    for numero, passe in enumerate(chauds, start=1):
        detail.append((f"à chaud {numero}", mesures_detaillees(passe[2].meta, passe[0], passe[1])))
    detail.append(("**médiane à chaud**", mediane_des_passes([m for _, m in detail[1:]])))

    print("\nDétail par passe (mesures brutes d'Ollama et grandeurs dérivées)")
    print("Sur une question rejouée, Ollama réutilise le cache de prefill : prompt_eval_duration")
    print("s'effondre et le débit de prefill à chaud n'a plus de sens physique. Seule la passe à")
    print("froid, ou une question nouvelle, donne un temps de prefill représentatif.\n")
    print("| Passe | " + " | ".join(ENTETES) + " |")
    print("|---" * (len(ENTETES) + 1) + "|")
    for passe, mesures in detail:
        print(ligne_detaillee(passe, mesures))

    archiver(question, reply, documents)
    print(f"\nRéponse archivée : {ARCHIVE}")

    print("\n=== RAM du pipeline chargé (Qwen + Gemma + Chroma résidents) ===")
    if RELEVE_RAM.exists() and shutil.which("powershell"):
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RELEVE_RAM)]
        )
    else:
        print("  (relevé RAM PowerShell indisponible ici ; sur le VPS Linux, relever avec "
              "`free -h` et `docker compose exec ollama ollama ps`)")

    # La métadonnée brute de la dernière passe, pour la traçabilité du relevé.
    print("\nMétadonnées brutes de la dernière passe (reply.meta) :")
    print(repr(meta))


if __name__ == "__main__":
    main()
