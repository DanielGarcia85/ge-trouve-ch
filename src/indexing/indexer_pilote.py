# src/indexing/indexer_pilote.py

"""
Indexation pilote — fragments, embeddings, Chroma
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Lire les pages scrapées (un JSON par page sous DATA_DIR/pilote/pages/), les
découper en fragments (annexe B : 200 mots, recouvrement 40), les encoder avec
Qwen (documents sans consigne) et les écrire dans une base Chroma persistante,
chaque fragment portant ses métadonnées (url, titre, section, niveau,
date_capture, position). Relève les mesures d'indexation. Ne fait ni la
recherche ni la génération (étape 1.5).

Choix
─────
Les composants Haystack (DocumentSplitter, OllamaDocumentEmbedder) sont appelés
explicitement, un par un, pour pouvoir ajouter le champ `position` entre le
découpage et l'embedding et pour relever les mesures simplement.
"""

import json
import sys
import time
from pathlib import Path

from haystack import Document
from haystack.components.preprocessors import DocumentSplitter
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

# Accès au module de configuration partagé (src/config.py).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

# ── Constantes ────────────────────────────────────────────────────────
MODELE_EMBEDDINGS = "qwen3-embedding:0.6b"
TAILLE_FRAGMENT = 200      # mots par fragment (annexe B)
RECOUVREMENT = 40          # mots de recouvrement (annexe B)

DOSSIER_PAGES = Path(config.DATA_DIR) / "pilote" / "pages"
CHROMA_DIR = Path(config.CHROMA_PERSIST_DIR)


# ── Utilitaires ───────────────────────────────────────────────────────
def charger_pages():
    """Charge les pages scrapées (un JSON par page) en Documents Haystack."""
    documents = []
    for fichier in sorted(DOSSIER_PAGES.glob("*.json")):
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
        documents.append(
            Document(
                content=donnees["texte"],
                meta={
                    "url": donnees["url"],
                    "titre": donnees["titre"],
                    "section": donnees["section"],
                    "niveau": donnees["niveau"],
                    "date_capture": donnees["date_capture"],
                },
            )
        )
    return documents


def taille_dossier(chemin):
    """Taille totale (octets) des fichiers d'un dossier, récursivement."""
    if not chemin.exists():
        return 0
    return sum(f.stat().st_size for f in chemin.rglob("*") if f.is_file())


# ── Point d'entrée ────────────────────────────────────────────────────
def main():
    """Découpe, encode et écrit les fragments dans Chroma ; relève les mesures."""
    pages = charger_pages()
    if not pages:
        print(f"Aucune page trouvée dans {DOSSIER_PAGES}. Lancer d'abord le scraper.")
        sys.exit(1)
    print(f"{len(pages)} pages chargées.")

    splitter = DocumentSplitter(
        split_by="word", split_length=TAILLE_FRAGMENT, split_overlap=RECOUVREMENT
    )
    if hasattr(splitter, "warm_up"):
        splitter.warm_up()

    debut = time.perf_counter()
    fragments = splitter.run(documents=pages)["documents"]
    # `position` : index du fragment dans sa page (fourni par le splitter).
    # `_split_overlap` est une liste (non scalaire) que Chroma rejette : on la retire.
    for fragment in fragments:
        fragment.meta["position"] = fragment.meta.get("split_id", 0)
        fragment.meta.pop("_split_overlap", None)

    embedder = OllamaDocumentEmbedder(model=MODELE_EMBEDDINGS, url=config.OLLAMA_BASE_URL)
    if hasattr(embedder, "warm_up"):
        embedder.warm_up()
    fragments = embedder.run(documents=fragments)["documents"]

    store = ChromaDocumentStore(persist_path=str(CHROMA_DIR))
    ecrits = store.write_documents(fragments, policy=DuplicatePolicy.OVERWRITE)
    duree = time.perf_counter() - debut

    dimension = len(fragments[0].embedding) if fragments and fragments[0].embedding else 0
    taille_mo = taille_dossier(CHROMA_DIR) / (1024 * 1024)

    print(f"\nPages indexées         : {len(pages)}")
    print(f"Fragments écrits        : {ecrits}")
    print(f"Durée totale            : {duree:.1f} s")
    print(f"Débit                   : {ecrits / duree:.1f} fragments/s")
    print(f"Taille base Chroma      : {taille_mo:.1f} Mo")
    print(f"Dimension des vecteurs  : {dimension}")


if __name__ == "__main__":
    main()
