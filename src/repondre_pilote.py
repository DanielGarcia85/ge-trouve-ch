# src/repondre_pilote.py

"""
Pipeline de réponse pilote — recherche puis génération
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Répondre à une question en langage naturel à partir de la base Chroma pilote :
encoder la requête (Qwen, avec la consigne de tâche), récupérer les fragments
les plus proches (Chroma), assembler un prompt (message système + extraits +
question) et générer la réponse avec Gemma en mode direct. Point d'entrée en
ligne de commande. Ne construit pas l'index (étape 1.4).

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

# ── Constantes ────────────────────────────────────────────────────────
MODELE_EMBEDDINGS = "qwen3-embedding:0.6b"
TOP_K = 5
TACHE = "Given a web search query, retrieve relevant passages that answer the query"
OPTIONS = {"temperature": 0, "seed": 42, "num_predict": 512, "num_ctx": 4096}
QUESTION_DEFAUT = "Où déposer ma demande de permis de séjour ?"

# Contrôle temporaire prouvant le mode direct ; à passer à False ensuite.
CONTROLE_MODE_DIRECT = True

# Consigne provisoire (annexe C), remplacée à l'étape 2.
CONSIGNE_SYSTEME = (
    "Tu es Ge-Trouve, un assistant pour les démarches administratives du canton de Genève. "
    "Réponds en français simple, uniquement à partir des extraits fournis. Conserve les noms "
    "exacts des offices, des formulaires et des permis. Si les extraits ne permettent pas de "
    "répondre, dis-le clairement."
)

# Message utilisateur : chaque extrait précédé de son URL, puis la question.
GABARIT_UTILISATEUR = (
    "Extraits :\n"
    "{% for doc in documents %}"
    "[{{ doc.meta.url }}]\n{{ doc.content }}\n\n"
    "{% endfor %}"
    "Question : {{ question }}"
)


def construire_pipeline():
    """Assemble le pipeline explicite : embedder, retriever, prompt, générateur."""
    store = ChromaDocumentStore(persist_path=str(Path(config.CHROMA_PERSIST_DIR)))
    gabarit = [
        ChatMessage.from_system(CONSIGNE_SYSTEME),
        ChatMessage.from_user(GABARIT_UTILISATEUR),
    ]
    pipe = Pipeline()
    pipe.add_component("embedder", OllamaTextEmbedder(model=MODELE_EMBEDDINGS, url=config.OLLAMA_BASE_URL))
    pipe.add_component("retriever", ChromaEmbeddingRetriever(document_store=store, top_k=TOP_K))
    pipe.add_component(
        "prompt_builder",
        ChatPromptBuilder(template=gabarit, required_variables=["documents", "question"]),
    )
    pipe.add_component(
        "generator",
        OllamaChatGenerator(
            model=config.OLLAMA_MODEL, url=config.OLLAMA_BASE_URL, think=False, generation_kwargs=OPTIONS
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

    if CONTROLE_MODE_DIRECT:
        print(
            f"\n[contrôle mode direct] think=False passé au générateur ; "
            f"réflexion dans la réponse (doit être vide) : {reponse.reasoning!r}"
        )


if __name__ == "__main__":
    main()
