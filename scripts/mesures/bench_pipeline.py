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


if __name__ == "__main__":
    main()
