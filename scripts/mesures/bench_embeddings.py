# scripts/mesures/bench_embeddings.py

"""
Mesure des embeddings — latence et débit via Haystack + Ollama
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Mesurer, via Haystack (OllamaTextEmbedder / OllamaDocumentEmbedder) et le modèle
qwen3-embedding:0.6b : la latence d'encodage d'une requête (médiane sur 10) et le
débit d'indexation sur un lot de 100 documents (docs/s, dimension des vecteurs).
Sert aussi de premier test de l'intégration Haystack-Ollama. N'écrit rien :
imprime les résultats à coller dans le journal des mesures.

Deux relevés, clairement séparés
────────────────────────────────
  1. *Mesures Haystack* (celles de toujours, inchangées) : ce sont les seules qui
     reflètent le coût réel tel que le pipeline le subit.
  2. *Relevé complémentaire par appel direct à `/api/embed`* : les embedders
     Haystack renvoient une métadonnée réduite au seul nom du modèle
     (`{"model": ...}`) et jettent tout ce qu'Ollama mesure. Pour ne pas perdre
     ces chiffres, la requête seule est rejouée en appel direct (bibliothèque
     standard, aucune dépendance nouvelle), ce qui donne `total_duration`,
     `load_duration` et `prompt_eval_count`. L'API d'embeddings ne génère rien :
     `eval_count` et `eval_duration` n'existent pas et valent « n/d ».

Ce second relevé s'exécute APRÈS le premier, pour ne rien changer aux mesures
Haystack : le modèle est déchargé juste avant, afin d'obtenir une vraie passe à
froid (et donc un `load_duration` réel, jamais mesuré jusqu'ici).
"""

import json
import os
import statistics
import time
import urllib.request
from pathlib import Path

from haystack import Document
from haystack_integrations.components.embedders.ollama import (
    OllamaDocumentEmbedder,
    OllamaTextEmbedder,
)

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODELE = "qwen3-embedding:0.6b"
PHRASE = "Où déposer ma demande de permis de séjour ?"
FICHIER = Path(__file__).parent / "paragraphes_bench.txt"
TAILLE_LOT = 100


def charger_paragraphes():
    """Charge les paragraphes du fichier (séparés par une ligne vide)."""
    texte = FICHIER.read_text(encoding="utf-8")
    return [p.strip() for p in texte.split("\n\n") if p.strip()]


def latence_requete(embedder):
    """Médiane de la latence d'encodage de la phrase-exemple sur 10 essais."""
    latences = []
    for _ in range(10):
        debut = time.perf_counter()
        embedder.run(text=PHRASE)
        latences.append(time.perf_counter() - debut)
    return statistics.median(latences)


def debit_indexation(paragraphes):
    """Débit d'encodage d'un lot de 100 documents (cyclage des paragraphes)."""
    documents = [Document(content=paragraphes[i % len(paragraphes)]) for i in range(TAILLE_LOT)]
    embedder = OllamaDocumentEmbedder(model=MODELE, url=OLLAMA_URL)
    debut = time.perf_counter()
    resultat = embedder.run(documents=documents)
    duree = time.perf_counter() - debut
    docs = resultat["documents"]
    dimension = len(docs[0].embedding) if docs and docs[0].embedding else 0
    return duree, TAILLE_LOT / duree, dimension


# ── Relevé complémentaire : appel direct à /api/embed ─────────────────
# Les embedders Haystack ne transmettent pas les mesures d'Ollama (leur méta se
# réduit au nom du modèle) ; on interroge donc l'API directement, en bibliothèque
# standard. Tout est lu de façon défensive : un champ absent vaut None et
# s'affiche « n/d » sans faire échouer la mesure.

NB_PASSES_CHAUD = 3  # même convention que les autres bancs : 1 passe à froid, 3 à chaud


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


def _poster(chemin, corps):
    """Envoie un POST JSON à Ollama et retourne la réponse décodée."""
    requete = urllib.request.Request(
        OLLAMA_URL + chemin,
        data=json.dumps(corps).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(requete) as reponse:
        return json.loads(reponse.read())


def decharger():
    """
    Décharge le modèle d'embeddings de la mémoire (keep_alive 0).
    Appelé uniquement après les mesures Haystack, pour que la première passe du
    relevé direct soit réellement à froid et livre un `load_duration` mesuré.
    """
    _poster("/api/embed", {"model": MODELE, "input": "", "keep_alive": 0})


def encoder_direct():
    """Encode la phrase-exemple par appel direct et retourne ses mesures."""
    debut = time.perf_counter()
    reponse = _poster("/api/embed", {"model": MODELE, "input": PHRASE})
    total_chrono = time.perf_counter() - debut
    total = _secondes(reponse.get("total_duration"))
    prefill = _secondes(reponse.get("prompt_eval_duration"))
    # L'API d'embeddings ne génère pas de texte : les champs eval_* sont normalement absents.
    generation = _secondes(reponse.get("eval_duration"))
    jetons_prompt = reponse.get("prompt_eval_count")
    part = _rapport(prefill, total)
    return {
        "total_duration": total,
        "load_duration": _secondes(reponse.get("load_duration")),
        "prompt_eval_count": jetons_prompt,
        "prompt_eval_duration": prefill,
        "eval_count": reponse.get("eval_count"),
        "eval_duration": generation,
        # Ollama ne chronomètre pas séparément le prefill sur /api/embed : l'appel entier EST
        # l'encodage. Le débit est donc rapporté à `total_duration`, et non à une durée de
        # prefill qui n'existe pas ici ; l'en-tête de colonne le dit.
        "debit_encodage": _rapport(jetons_prompt, total),
        "debit_prefill": _rapport(jetons_prompt, prefill),
        "debit_generation": _rapport(reponse.get("eval_count"), generation),
        "part_prefill": None if part is None else part * 100,
        "hors_ollama": None if total is None else total_chrono - total,
        "total_chrono": total_chrono,
    }, {cle: valeur for cle, valeur in reponse.items() if cle != "embeddings"}


# Colonnes du tableau détaillé, dans l'ordre d'affichage.
ENTETES = (
    "total_duration (s)", "load_duration (s)", "prompt_eval_count",
    "prompt_eval_duration (s)", "eval_count", "eval_duration (s)",
    "Débit encodage (jetons/s, sur total_duration)", "Débit prefill (jetons/s)",
    "Débit génération (jetons/s)", "Part prefill (%)",
    "Hors Ollama (s)", "Total chrono (s)",
)


def ligne_detaillee(passe, m):
    """Met en forme une passe en ligne de tableau Markdown."""
    cellules = [
        _nb(m["total_duration"]), _nb(m["load_duration"]), _ent(m["prompt_eval_count"]),
        _nb(m["prompt_eval_duration"]), _ent(m["eval_count"]), _nb(m["eval_duration"]),
        _nb(m["debit_encodage"], 1), _nb(m["debit_prefill"], 1),
        _nb(m["debit_generation"], 1), _nb(m["part_prefill"], 1),
        _nb(m["hors_ollama"]), _nb(m["total_chrono"]),
    ]
    return f"| {passe} | " + " | ".join(cellules) + " |"


def mediane_des_passes(passes):
    """Médiane, champ par champ, d'une série de passes (les jetons restent entiers)."""
    entiers = ("prompt_eval_count", "eval_count")
    milieu = {}
    for cle in passes[0]:
        valeur = _mediane([p[cle] for p in passes])
        milieu[cle] = int(valeur) if (valeur is not None and cle in entiers) else valeur
    return milieu


def releve_direct():
    """
    Rejoue la requête seule en appel direct : 1 passe à froid, puis 3 à chaud.

    Retourne la liste (libellé de passe, mesures) et la réponse brute de la
    dernière passe, vecteurs exclus.
    """
    decharger()  # garantit une vraie passe à froid, sans toucher aux mesures Haystack déjà prises
    mesures_froid, _ = encoder_direct()
    passes = [("à froid", mesures_froid)]
    brut = {}
    for numero in range(1, NB_PASSES_CHAUD + 1):
        mesures, brut = encoder_direct()
        passes.append((f"à chaud {numero}", mesures))
    passes.append(("**médiane à chaud**", mediane_des_passes([m for _, m in passes[1:]])))
    return passes, brut


def main():
    text_embedder = OllamaTextEmbedder(model=MODELE, url=OLLAMA_URL)
    latence = latence_requete(text_embedder)
    paragraphes = charger_paragraphes()
    duree, debit, dimension = debit_indexation(paragraphes)

    print(f"Paragraphes sources        : {len(paragraphes)} (cycles a {TAILLE_LOT})")
    print(f"Latence encodage requete   : {latence * 1000:.0f} ms (mediane sur 10)")
    print(f"Debit indexation (100 docs): {debit:.1f} docs/s (duree totale {duree:.1f} s)")
    print(f"Dimension des vecteurs     : {dimension}")

    # ── Relevé complémentaire, hors Haystack ──────────────────────────
    # Les mesures ci-dessus restent la référence ; celles qui suivent viennent
    # d'appels directs à /api/embed, la seule voie qui expose les chiffres d'Ollama.
    passes, brut = releve_direct()
    print("\nRelevé complémentaire par appel direct à /api/embed (requête seule)")
    print("Les embedders Haystack n'exposent que le nom du modèle : ces mesures sont")
    print("relevées hors du pipeline, après les mesures Haystack, modèle déchargé au départ.\n")
    print("| Passe | " + " | ".join(ENTETES) + " |")
    print("|---" * (len(ENTETES) + 1) + "|")
    for passe, mesures in passes:
        print(ligne_detaillee(passe, mesures))

    # La réponse brute de la dernière passe (vecteurs exclus), pour la traçabilité du relevé.
    print("\nMétadonnées brutes de la dernière passe (réponse /api/embed, vecteurs exclus) :")
    print(repr(brut))


if __name__ == "__main__":
    main()
