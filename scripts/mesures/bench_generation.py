# scripts/mesures/bench_generation.py

"""
Mesure de génération LLM — débits et latences via Ollama
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Mesurer, sur l'API locale Ollama (/api/chat), la vitesse de génération des deux
modèles de langage (gemma4:12b, llama3.1:8b) : latence du premier jeton, débit
en jetons/s, durée de chargement à froid. Bibliothèque standard uniquement.
N'écrit rien : imprime des lignes de tableau à coller dans le journal des
mesures. Ne teste pas la qualité des réponses (température 0).

Imprime deux tableaux. Le premier est le tableau de synthèse historique (une ligne
par modèle), inchangé. Le second détaille, passe par passe, toutes les mesures que
le bloc final du flux (done=true) contient : `total_duration`, `load_duration`,
`prompt_eval_count`, `prompt_eval_cached_count`, `prompt_eval_duration`,
`eval_count`, `eval_duration` ; s'y ajoutent les grandeurs dérivées (débit de
prefill, débit de génération, part du prefill dans la durée totale). Un champ
absent vaut « n/d » et n'interrompt jamais la mesure.

Prefill et génération
─────────────────────
Ollama sépare les deux temps : le prefill (lecture du prompt, `prompt_eval_*`)
et la génération (écriture de la réponse, `eval_*`). Les distinguer montre
lequel des deux domine la latence ressentie.
"""

import json
import os
import statistics
import time
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODELES = ["gemma4:12b", "llama3.1:8b"]
OPTIONS = {"temperature": 0, "seed": 42, "num_predict": 256, "num_ctx": 4096}

# Consigne courte, sans jeton <|think|> (mode direct, cf. chapitre 4).
SYSTEME = (
    "Tu es un assistant administratif pour les démarches du canton de Genève. "
    "Réponds de façon simple et factuelle, en français, à partir du contexte fourni."
)

# Contexte factice rédigé pour la mesure, jamais scrapé.
CONTEXTE = (
    "Contexte : les demandes de permis de séjour pour les personnes étrangères "
    "s'adressent à l'office cantonal de la population et des migrations. Le dossier "
    "comprend un formulaire de demande, une pièce d'identité valable, un justificatif "
    "de domicile et, selon la situation, un contrat de travail ou une attestation "
    "d'inscription. Le dépôt se fait au guichet de l'office, sur rendez-vous, ou par "
    "voie postale à l'adresse indiquée sur le formulaire. Une taxe est perçue au dépôt. "
    "Pour un renouvellement, la demande se dépose avant l'échéance du permis en cours. "
    "La commune de domicile peut orienter l'usager vers le service compétent."
)
QUESTION = "Où déposer ma demande de permis de séjour ?"


# ── Lecture des mesures Ollama ────────────────────────────────────────
# Les champs renvoyés varient d'une version d'Ollama à l'autre : tout est lu de
# façon défensive, un champ absent vaut None et s'affiche « n/d » sans faire
# échouer la mesure.

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


def mesures_detaillees(bloc, total_chrono, latence_premier):
    """
    Extrait du bloc final d'Ollama toutes ses mesures, et en dérive les débits.

    `bloc` est le dernier objet JSON du flux (celui qui porte done=true) ; ses
    durées sont en nanosecondes et sont ramenées ici en secondes.
    """
    total = _secondes(bloc.get("total_duration"))
    prefill = _secondes(bloc.get("prompt_eval_duration"))
    generation = _secondes(bloc.get("eval_duration"))
    jetons_prompt = bloc.get("prompt_eval_count")
    jetons_reponse = bloc.get("eval_count")
    part = _rapport(prefill, total)
    return {
        "total_duration": total,
        "load_duration": _secondes(bloc.get("load_duration")),
        "prompt_eval_count": jetons_prompt,
        "prompt_eval_cached_count": bloc.get("prompt_eval_cached_count"),
        "prompt_eval_duration": prefill,
        "eval_count": jetons_reponse,
        "eval_duration": generation,
        "debit_prefill": _rapport(jetons_prompt, prefill),
        "debit_generation": _rapport(jetons_reponse, generation),
        "part_prefill": None if part is None else part * 100,
        "premier_mot": latence_premier,
        "total_chrono": total_chrono,
    }


# Colonnes du tableau détaillé, dans l'ordre d'affichage.
ENTETES = (
    "total_duration (s)", "load_duration (s)", "prompt_eval_count", "dont en cache",
    "prompt_eval_duration (s)", "eval_count", "eval_duration (s)",
    "Débit prefill (jetons/s)", "Débit génération (jetons/s)", "Part prefill (%)",
    "1er jeton chrono (s)", "Total chrono (s)",
)


def ligne_detaillee(modele, passe, m):
    """Met en forme une passe en ligne de tableau Markdown."""
    cellules = [
        _nb(m["total_duration"]), _nb(m["load_duration"]),
        _ent(m["prompt_eval_count"]), _ent(m["prompt_eval_cached_count"]),
        _nb(m["prompt_eval_duration"]), _ent(m["eval_count"]), _nb(m["eval_duration"]),
        _nb(m["debit_prefill"], 1), _nb(m["debit_generation"], 1), _nb(m["part_prefill"], 1),
        _nb(m["premier_mot"]), _nb(m["total_chrono"]),
    ]
    return f"| `{modele}` | {passe} | " + " | ".join(cellules) + " |"


def mediane_des_passes(passes):
    """Médiane, champ par champ, d'une série de passes (les jetons restent entiers)."""
    entiers = ("prompt_eval_count", "prompt_eval_cached_count", "eval_count")
    milieu = {}
    for cle in passes[0]:
        valeur = _mediane([p[cle] for p in passes])
        milieu[cle] = int(valeur) if (valeur is not None and cle in entiers) else valeur
    return milieu


def generer(modele):
    """Lance une génération en flux et retourne les métriques de la requête."""
    corps = {
        "model": modele,
        "messages": [
            {"role": "system", "content": SYSTEME},
            {"role": "user", "content": CONTEXTE + "\n\n" + QUESTION},
        ],
        "stream": True,
        "think": False,  # mode direct : réflexion désactivée (chapitre 4)
        "options": OPTIONS,
    }
    requete = urllib.request.Request(
        OLLAMA_URL + "/api/chat",
        data=json.dumps(corps).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    debut = time.perf_counter()
    latence_premier = None
    dernier = {}
    with urllib.request.urlopen(requete) as reponse:
        for ligne in reponse:
            if not ligne.strip():
                continue
            bloc = json.loads(ligne)
            if latence_premier is None and bloc.get("message", {}).get("content"):
                latence_premier = time.perf_counter() - debut
            if bloc.get("done"):
                dernier = bloc
    total_chrono = time.perf_counter() - debut
    jetons = dernier.get("eval_count", 0)
    duree_eval = dernier.get("eval_duration", 0) / 1e9
    return {
        "latence": latence_premier or 0.0,
        "jetons": jetons,
        "debit": jetons / duree_eval if duree_eval else 0.0,
        "chargement": dernier.get("load_duration", 0) / 1e9,
        # Relevé complet de la même passe : mesures brutes d'Ollama et dérivées.
        "detail": mesures_detaillees(dernier, total_chrono, latence_premier),
        "brut": dernier,
    }


def decharger(modele):
    """
    Décharge un modèle de la mémoire (keep_alive 0).
    Évite de cumuler deux LLM en RAM entre deux modèles, ce qui saturerait une
    machine à faible mémoire (le poste à 16 Go partirait en swap et fausserait
    les mesures). Sans effet visible sur une machine large.
    """
    corps = {"model": modele, "keep_alive": 0}
    requete = urllib.request.Request(
        OLLAMA_URL + "/api/generate",
        data=json.dumps(corps).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(requete) as reponse:
        reponse.read()


def main():
    """Pour chaque modèle : 1 exécution à froid puis 3 à chaud, médiane des 3."""
    print("| Modele | Chargement a froid (s) | Latence 1er jeton (s) | Debit (jetons/s) | Jetons |")
    print("|---|---|---|---|---|")
    detail = []  # (modèle, libellé de passe, mesures) pour le tableau détaillé
    dernier_brut = {}
    for modele in MODELES:
        froid = generer(modele)
        chauds = [generer(modele) for _ in range(3)]
        latence = statistics.median(c["latence"] for c in chauds)
        debit = statistics.median(c["debit"] for c in chauds)
        jetons = int(statistics.median(c["jetons"] for c in chauds))
        print(f"| {modele} | {froid['chargement']:.2f} | {latence:.2f} | {debit:.1f} | {jetons} |")
        detail.append((modele, "à froid", froid["detail"]))
        for numero, passe in enumerate(chauds, start=1):
            detail.append((modele, f"à chaud {numero}", passe["detail"]))
        detail.append((modele, "**médiane à chaud**", mediane_des_passes([c["detail"] for c in chauds])))
        dernier_brut = chauds[-1]["brut"]
        decharger(modele)  # libère la RAM avant le modèle suivant (poste à faible mémoire)

    # ── Tableau détaillé : toutes les mesures d'Ollama, passe par passe ───
    print("\nDétail par passe (mesures brutes d'Ollama et grandeurs dérivées)\n")
    print("| Modèle | Passe | " + " | ".join(ENTETES) + " |")
    print("|---" * (len(ENTETES) + 2) + "|")
    for modele, passe, mesures in detail:
        print(ligne_detaillee(modele, passe, mesures))

    # Le bloc final brut de la dernière passe, pour la traçabilité du relevé.
    print("\nMétadonnées brutes de la dernière passe (bloc done=true) :")
    print(repr({cle: valeur for cle, valeur in dernier_brut.items() if cle != "message"}))


if __name__ == "__main__":
    main()
