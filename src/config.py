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
# Modèles à provisionner sur le serveur Ollama (tirés une fois par le service ollama-pull) ;
# ajouter un modèle à tirer = une ligne ici, sans toucher au script de pull.
MODELES_A_TIRER = (OLLAMA_GENERATION_MODEL, OLLAMA_EMBEDDING_MODEL)
CHROMA_PERSIST_DIR = _lire("CHROMA_PERSIST_DIR", "./data/chroma")  # base vectorielle Chroma (persistante)
DATA_DIR = _lire("DATA_DIR", "./data")  # corpus brut scrapé (non versionné)
RESULTATS_DIR = RACINE / "resultats"  # nos artefacts versionnés (chemin fixe dans le dépôt, non configurable)

# ── Réglages du pipeline de réponse ───────────────────────────────────
# Lus par src/repondre.py. Les scalaires se surchargent par variable d'environnement
# (le banc d'évaluation relève par exemple le délai d'attente pour le chargement à froid).
TOP_K = int(_lire("TOP_K", "5"))  # fragments récupérés par la recherche
TIMEOUT_GENERATION = int(_lire("TIMEOUT_GENERATION", "300"))  # délai client de génération, en secondes
# Régime d'échantillonnage de production (acté à l'étape 2) : température basse (réponses fondées et
# quasi stables), échantillonnage recommandé par l'éditeur (top_p/top_k), plafond large pour ne pas
# tronquer les réponses. Pas de seed en production (le seed reste un outil de comparaison des essais).
OPTIONS_GENERATION = {"temperature": 0.3, "top_p": 0.95, "top_k": 64, "num_predict": 1024, "num_ctx": 4096}
