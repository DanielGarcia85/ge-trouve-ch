# src/indexing/indexer_complet.py

"""
Indexation du corpus complet — fragments, embeddings, Chroma
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Lire les pages du corpus complet (un JSON par page sous DATA_DIR/pages/complet/),
les découper en fragments (200 mots, recouvrement 40), les encoder avec Qwen
(documents sans consigne) et les écrire dans la base Chroma de production, chaque
fragment portant ses métadonnées (url, titre, date_capture, position). Encode et
écrit par lots, avec progression, pour borner la mémoire et suivre un long traitement.
Reconstruction propre : la collection est vidée avant écriture. Relève les mesures.
Ne fait ni la recherche ni la génération.

Liens
─────
Le texte conserve les hyperliens (`[libellé](url)`). Le contenu embarqué (embeddings)
est nettoyé de ses URL, réduit au libellé, pour ne pas polluer la recherche. La version
avec liens est conservée dans la métadonnée `texte_liens`, montrée au modèle à la génération.

Différences avec l'indexeur pilote
──────────────────────────────────
  - lit le corpus complet (DATA_DIR/pages/complet/) au lieu du pilote ;
  - pas de métadonnée « section » (le corpus complet n'en porte pas) ;
  - encodage et écriture par lots de pages, avec progression et estimation du temps restant ;
  - option --limite pour mesurer le débit sur un échantillon, dans une base de test à part ;
  - option --reprise pour continuer une indexation interrompue sans tout refaire.

Reprise
───────
Un lot est une tranche de pages : tous les fragments d'une page sont encodés et écrits
ensemble, donc une page est soit entièrement indexée, soit pas du tout. En cas
d'interruption, `--reprise` relit les URL déjà présentes dans la base et saute les pages
correspondantes (les IDs Chroma sont des empreintes du contenu : ré-indexer n'introduit
aucun doublon). Un lancement normal, lui, reconstruit la base à neuf.

Usage
─────
  python src/indexing/indexer_complet.py               (indexe tout le corpus, base de production)
  python src/indexing/indexer_complet.py --reprise     (reprend après une interruption)
  python src/indexing/indexer_complet.py --limite 50   (mesure sur 50 pages, base de test à part)
"""

import argparse
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
TAILLE_FRAGMENT = 200      # mots par fragment
RECOUVREMENT = 40          # mots de recouvrement
PAGES_PAR_LOT = 50         # pages encodées et écrites par lot (progression + reprise page par page)

DOSSIER_PAGES = Path(config.DATA_DIR) / "pages" / "complet"
CHROMA_DIR = Path(config.CHROMA_PERSIST_DIR)


# ── Utilitaires ───────────────────────────────────────────────────────
def charger_pages(limite=None):
    """Charge les pages du corpus complet (un JSON par page) en Documents Haystack."""
    documents = []
    fichiers = sorted(DOSSIER_PAGES.glob("*.json"))
    if limite:
        fichiers = fichiers[:limite]
    for fichier in fichiers:
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
        documents.append(
            Document(
                content=donnees["texte"],
                meta={
                    "url": donnees["url"],
                    "titre": donnees["titre"],
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


def preparer_fragments(splitter, pages):
    """Découpe un lot de pages en fragments, ajoute position/texte_liens et nettoie le contenu embarqué."""
    fragments = splitter.run(documents=pages)["documents"]
    prepares = []
    for fragment in fragments:
        fragment.meta["position"] = fragment.meta.get("split_id", 0)
        fragment.meta.pop("_split_overlap", None)  # liste rejetée par Chroma
        fragment.meta["texte_liens"] = fragment.content  # version avec liens, pour la génération
        # Nouveau Document au contenu nettoyé (on ne mute pas l'instance du splitter).
        prepares.append(dataclasses.replace(fragment, content=nettoyer_liens(fragment.content)))
    return prepares


# ── Point d'entrée ────────────────────────────────────────────────────
def main():
    """Encode et écrit les fragments par lots de pages ; reprise possible ; relève les mesures."""
    analyseur = argparse.ArgumentParser(description="Indexation du corpus complet dans Chroma.")
    analyseur.add_argument(
        "--limite",
        type=int,
        help="n'indexer que les N premières pages, dans une base de test à part (mesure du débit)",
    )
    analyseur.add_argument(
        "--reprise",
        action="store_true",
        help="reprendre une indexation interrompue : ne pas vider la base, sauter les pages déjà indexées",
    )
    args = analyseur.parse_args()

    # En mode --limite, on écrit dans une base de test pour ne pas toucher la production.
    chroma_dir = CHROMA_DIR if not args.limite else CHROMA_DIR.parent / "chroma_test"

    pages = charger_pages(args.limite)
    if not pages:
        print(f"Aucune page trouvée dans {DOSSIER_PAGES}. Lancer d'abord le scraper.")
        sys.exit(1)

    splitter = DocumentSplitter(
        split_by="word", split_length=TAILLE_FRAGMENT, split_overlap=RECOUVREMENT
    )
    if hasattr(splitter, "warm_up"):
        splitter.warm_up()
    embedder = OllamaDocumentEmbedder(model=config.OLLAMA_EMBEDDING_MODEL, url=config.OLLAMA_BASE_URL)
    if hasattr(embedder, "warm_up"):
        embedder.warm_up()
    store = ChromaDocumentStore(persist_path=str(chroma_dir))

    if args.reprise:
        faites = {doc.meta.get("url") for doc in store.filter_documents()}
        pages = [page for page in pages if page.meta["url"] not in faites]
        print(f"Reprise : {len(faites)} URL déjà indexées, {len(pages)} pages restantes.")
    else:
        # Reconstruction propre : vider la collection avant écriture (sinon accumulation de doublons).
        anciens = store.filter_documents()
        if anciens:
            store.delete_documents([doc.id for doc in anciens])
        print(f"{len(pages)} pages à indexer (reconstruction propre).")

    if not pages:
        print(f"Rien à faire : tout est déjà indexé ({store.count_documents()} fragments).")
        return

    total_pages = len(pages)
    ecrits = 0
    dimension = 0
    debut = time.perf_counter()
    for depart in range(0, total_pages, PAGES_PAR_LOT):
        lot_pages = pages[depart : depart + PAGES_PAR_LOT]
        fragments = preparer_fragments(splitter, lot_pages)
        fragments = embedder.run(documents=fragments)["documents"]
        store.write_documents(fragments, policy=DuplicatePolicy.OVERWRITE)
        ecrits += len(fragments)
        if not dimension and fragments and fragments[0].embedding:
            dimension = len(fragments[0].embedding)
        pages_faites = min(depart + PAGES_PAR_LOT, total_pages)
        ecoule = time.perf_counter() - debut
        debit = ecrits / ecoule if ecoule else 0
        # Temps restant estimé d'après le débit courant et le nombre de fragments par page observé.
        reste = ((total_pages - pages_faites) * (ecrits / pages_faites)) / debit if debit else 0
        print(
            f"  {pages_faites}/{total_pages} pages  |  {ecrits} frag  |  {debit:.1f} frag/s  "
            f"|  écoulé {ecoule / 60:.1f} min  |  reste ~{reste / 60:.1f} min"
        )

    duree = time.perf_counter() - debut
    taille_mo = taille_dossier(chroma_dir) / (1024 * 1024)
    total = store.count_documents()

    print(f"\nPages traitées (cette exécution) : {total_pages}")
    print(f"Fragments écrits (cette exécution): {ecrits}")
    print(f"Fragments dans la base (total)   : {total}")
    print(f"Durée totale                     : {duree:.1f} s ({duree / 60:.1f} min)")
    print(f"Débit                            : {ecrits / duree:.1f} fragments/s")
    print(f"Taille base Chroma               : {taille_mo:.1f} Mo")
    print(f"Dimension des vecteurs           : {dimension}")
    print(f"Base                             : {chroma_dir}")
    if args.limite:
        print("\n(mode --limite : base de test, la production n'a pas été touchée.)")


if __name__ == "__main__":
    main()
