# src/config.py

"""
Configuration du projet — variables d'environnement et valeurs par défaut
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Exposer les paramètres du projet (URL d'Ollama, modèles, chemins) comme
constantes, avec des valeurs par défaut qui sont celles de production. Point
unique de configuration, réutilisé par le scraping, l'indexation et le pipeline
de réponse. N'introduit aucune dépendance externe.

Priorité de lecture
───────────────────
Variable d'environnement du shell (par exemple fournie par docker-compose en
production), sinon valeur par défaut. Aucun fichier `.env` : le projet ne
manipule aucun secret (contrainte de souveraineté), les valeurs par défaut
suffisent en local et les rares surcharges (URL, chemins dans le conteneur)
passent par l'environnement.
"""

import os
from pathlib import Path

# Racine du dépôt : le parent de src/ (ce fichier est src/config.py).
RACINE = Path(__file__).resolve().parent.parent


def _lire(cle, defaut):
    """Renvoie la variable d'environnement du shell si définie, sinon le défaut."""
    return os.environ.get(cle, defaut)


OLLAMA_BASE_URL = _lire("OLLAMA_BASE_URL", "http://localhost:11434")  # serveur Ollama local (inférence)
OLLAMA_GENERATION_MODEL = _lire("OLLAMA_GENERATION_MODEL", "gemma4:12b")  # LLM rédacteur servi par Ollama
OLLAMA_EMBEDDING_MODEL = _lire("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:0.6b")  # modèle d'embeddings servi par Ollama
CHROMA_PERSIST_DIR = _lire("CHROMA_PERSIST_DIR", "./data/chroma")  # base vectorielle Chroma (persistante)
DATA_DIR = _lire("DATA_DIR", "./data")  # corpus brut scrapé (non versionné)
RESULTATS_DIR = RACINE / "resultats"  # nos artefacts versionnés (chemin fixe dans le dépôt, non configurable)
