# src/indexing/indexer_pilote.py

"""
Indexation pilote — fragments, embeddings, Chroma
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Lire les pages scrapées (un JSON par page sous DATA_DIR/pages/pilote/), les
découper en fragments (Annexe 2 : 200 mots, recouvrement 40), les encoder avec
Qwen (documents sans consigne) et les écrire dans une base Chroma persistante,
chaque fragment portant ses métadonnées (url, titre, section,
date_capture, position). Reconstruction propre : la collection est vidée avant
écriture, pour éviter que les fragments s'accumulent d'un run à l'autre. Relève les
mesures d'indexation. Ne fait ni la recherche ni la génération (étape 1.5).

Liens
─────
Le texte scrapé conserve les hyperliens (`[libellé](url)`). Le contenu **embarqué**
(embeddings) est nettoyé de ses URL, réduit au libellé, pour ne pas polluer la
recherche avec les mots-clés des slugs. La version avec liens est conservée dans la
métadonnée `texte_liens`, montrée au modèle à la génération.

Choix
─────
Les composants Haystack (DocumentSplitter, OllamaDocumentEmbedder) sont appelés
explicitement, un par un, pour pouvoir ajouter le champ `position` entre le
découpage et l'embedding et pour relever les mesures simplement.
"""

import dataclasses
import json
import re
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
TAILLE_FRAGMENT = 200      # mots par fragment (Annexe 2)
RECOUVREMENT = 40          # mots de recouvrement (Annexe 2)

DOSSIER_PAGES = Path(config.DATA_DIR) / "pages" / "pilote"
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
                    "date_capture": donnees["date_capture"],
                },
            )
        )
    return documents


def nettoyer_liens(texte):
    """Réduit les liens markdown `[libellé](url)` à leur seul libellé (pour l'embedding)."""
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texte)


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
    fragments_propres = []
    for fragment in fragments:
        fragment.meta["position"] = fragment.meta.get("split_id", 0)
        fragment.meta.pop("_split_overlap", None)
        fragment.meta["texte_liens"] = fragment.content  # version avec liens, pour la génération
        # Contenu embarqué nettoyé de ses URL ; nouveau Document (on ne mute pas l'instance du splitter).
        fragments_propres.append(dataclasses.replace(fragment, content=nettoyer_liens(fragment.content)))
    fragments = fragments_propres

    embedder = OllamaDocumentEmbedder(model=MODELE_EMBEDDINGS, url=config.OLLAMA_BASE_URL)
    if hasattr(embedder, "warm_up"):
        embedder.warm_up()
    fragments = embedder.run(documents=fragments)["documents"]

    store = ChromaDocumentStore(persist_path=str(CHROMA_DIR))
    # Reconstruction propre : vider la collection d'abord. Sinon les fragments s'accumulent d'un run à
    # l'autre (les IDs = hash du contenu changent quand le texte change, donc OVERWRITE ne remplace pas
    # les anciens) : la base gonfle de doublons et le retrieval perd en diversité.
    anciens = store.filter_documents()
    if anciens:
        store.delete_documents([doc.id for doc in anciens])
    ecrits = store.write_documents(fragments, policy=DuplicatePolicy.OVERWRITE)
    duree = time.perf_counter() - debut

    dimension = len(fragments[0].embedding) if fragments and fragments[0].embedding else 0
    taille_mo = taille_dossier(CHROMA_DIR) / (1024 * 1024)
    total = store.count_documents()  # doit égaler `ecrits` après une reconstruction propre

    print(f"\nPages indexées         : {len(pages)}")
    print(f"Fragments écrits        : {ecrits}")
    print(f"Fragments dans la base  : {total}")
    print(f"Durée totale            : {duree:.1f} s")
    print(f"Débit                   : {ecrits / duree:.1f} fragments/s")
    print(f"Taille base Chroma      : {taille_mo:.1f} Mo")
    print(f"Dimension des vecteurs  : {dimension}")


if __name__ == "__main__":
    main()
