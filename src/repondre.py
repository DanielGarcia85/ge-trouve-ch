# src/repondre.py

"""
Pipeline de réponse — recherche puis génération
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Répondre à une question en langage naturel à partir de la base Chroma :
encoder la requête (Qwen, avec la consigne de tâche), récupérer les fragments
les plus proches (Chroma), assembler un prompt (message système + extraits +
question) et générer la réponse avec Gemma en mode direct. Point d'entrée en
ligne de commande. Ne construit pas l'index.

Asymétrie des embeddings
────────────────────────
Les documents ont été indexés sans consigne ; la requête, elle, est préfixée par
la consigne de tâche Qwen (`Instruct: ... \\nQuery:...`), comme documenté par
l'éditeur.

Mode direct
───────────
`OllamaChatGenerator` reçoit `think=False` (réflexion désactivée), transmis à
Ollama par l'intégration (chat_generator.py, ligne 554).
"""

import sys
from pathlib import Path

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

# Accès au module de configuration partagé (src/config.py).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
from generation.consignes import CONSIGNE_ACTIVE  # noqa: E402

# ── Constantes ────────────────────────────────────────────────────────
TOP_K = 5
TACHE = "Given a web search query, retrieve relevant passages that answer the query"
# Régime de production acté à la clôture de l'étape 2 : température basse (réponses fondées et
# quasi stables), échantillonnage recommandé par l'éditeur (top_p/top_k), plafond large pour ne
# pas tronquer les réponses complètes. Pas de seed en production (outil de comparaison seulement).
OPTIONS = {"temperature": 0.3, "top_p": 0.95, "top_k": 64, "num_predict": 1024, "num_ctx": 4096}
TIMEOUT_GENERATION = 300  # secondes ; marge pour le chargement à froid du modèle et une génération longue
QUESTION_DEFAUT = "Où déposer ma demande de permis de séjour ?"

# Message utilisateur : chaque extrait précédé de son URL, puis la question. On montre au
# modèle la version avec liens (`texte_liens`) ; le `content` embarqué, lui, est nettoyé des URL.
GABARIT_UTILISATEUR = (
    "Extraits :\n"
    "{% for doc in documents %}"
    "[{{ doc.meta.url }}]\n{{ doc.meta.get('texte_liens') or doc.content }}\n\n"
    "{% endfor %}"
    "Question : {{ question }}"
)


def construire_pipeline(consigne=None, options=None, streaming_callback=None):
    """
    Assemble le pipeline explicite : embedder, retriever, prompt, générateur.

    `consigne` et `options` servent à essayer des variantes (étape 2) ; par défaut,
    la consigne active et les options de référence. `streaming_callback`, s'il est fourni,
    est transmis au générateur pour émettre la réponse jeton par jeton (affichage progressif
    de l'interface) ; sans lui, le comportement est inchangé.
    """
    consigne = consigne or CONSIGNE_ACTIVE
    options = options or OPTIONS
    store = ChromaDocumentStore(persist_path=str(Path(config.CHROMA_PERSIST_DIR)))
    gabarit = [
        ChatMessage.from_system(consigne),
        ChatMessage.from_user(GABARIT_UTILISATEUR),
    ]
    pipe = Pipeline()
    pipe.add_component("embedder", OllamaTextEmbedder(model=config.OLLAMA_EMBEDDING_MODEL, url=config.OLLAMA_BASE_URL))
    pipe.add_component("retriever", ChromaEmbeddingRetriever(document_store=store, top_k=TOP_K))
    pipe.add_component(
        "prompt_builder",
        ChatPromptBuilder(template=gabarit, required_variables=["documents", "question"]),
    )
    pipe.add_component(
        "generator",
        OllamaChatGenerator(
            model=config.OLLAMA_GENERATION_MODEL, url=config.OLLAMA_BASE_URL, think=False,
            timeout=TIMEOUT_GENERATION, generation_kwargs=options,
            streaming_callback=streaming_callback,
        ),
    )
    pipe.connect("embedder.embedding", "retriever.query_embedding")
    pipe.connect("retriever.documents", "prompt_builder.documents")
    pipe.connect("prompt_builder.prompt", "generator.messages")
    return pipe


def main():
    """Répond à la question passée en argument (ou à la question type par défaut)."""
    question = " ".join(sys.argv[1:]).strip() or QUESTION_DEFAUT
    pipe = construire_pipeline()

    # La requête est préfixée par la consigne de tâche ; la question brute sert au prompt.
    requete_instruite = f"Instruct: {TACHE}\nQuery:{question}"
    resultat = pipe.run(
        {"embedder": {"text": requete_instruite}, "prompt_builder": {"question": question}},
        include_outputs_from={"retriever"},
    )

    reponse = resultat["generator"]["replies"][0]
    fragments = resultat["retriever"]["documents"]

    print(f"Question : {question}\n")
    print("Réponse :")
    print(reponse.text)
    print(f"\nFragments utilisés ({len(fragments)}) :")
    for doc in fragments:
        debut = " ".join(doc.content.split()[:15])
        print(f"  - {doc.meta.get('url')}\n    {debut}…")

    # Vérification permanente du mode direct : la réflexion doit rester vide (think=False).
    print(
        f"\n[contrôle mode direct] think=False passé au générateur ; "
        f"réflexion dans la réponse (doit être vide) : {reponse.reasoning!r}"
    )


if __name__ == "__main__":
    main()
