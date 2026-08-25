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
"""

import os
import statistics
import time
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


def main():
    text_embedder = OllamaTextEmbedder(model=MODELE, url=OLLAMA_URL)
    latence = latence_requete(text_embedder)
    paragraphes = charger_paragraphes()
    duree, debit, dimension = debit_indexation(paragraphes)

    print(f"Paragraphes sources        : {len(paragraphes)} (cycles a {TAILLE_LOT})")
    print(f"Latence encodage requete   : {latence * 1000:.0f} ms (mediane sur 10)")
    print(f"Debit indexation (100 docs): {debit:.1f} docs/s (duree totale {duree:.1f} s)")
    print(f"Dimension des vecteurs     : {dimension}")


if __name__ == "__main__":
    main()
