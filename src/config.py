# src/config.py

"""
Configuration du projet — lecture du fichier .env
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Charger les variables du fichier `.env` (à la racine du dépôt) et les exposer
comme constantes, avec des valeurs par défaut. Point unique de configuration,
réutilisé par le scraping, l'indexation et le pipeline de réponse. N'introduit
aucune dépendance externe (analyse minimale du `.env`).

Format `.env` attendu
─────────────────────
  - une ligne `CLE=valeur` par variable ;
  - lignes vides et lignes commençant par `#` ignorées.

Priorité : variable d'environnement du shell, puis `.env`, puis valeur par défaut.
"""

import os
from pathlib import Path

# Racine du dépôt : le parent de src/ (ce fichier est src/config.py).
RACINE = Path(__file__).resolve().parent.parent
FICHIER_ENV = RACINE / ".env"


def _charger_env(chemin):
    """Lit un fichier `.env` et renvoie un dictionnaire clé/valeur (analyse simple)."""
    valeurs = {}
    if not chemin.exists():
        return valeurs
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        valeurs[cle.strip()] = valeur.strip()
    return valeurs


_env = _charger_env(FICHIER_ENV)


def _lire(cle, defaut):
    """Renvoie la variable du shell si définie, sinon celle du `.env`, sinon le défaut."""
    return os.environ.get(cle) or _env.get(cle, defaut)


OLLAMA_BASE_URL = _lire("OLLAMA_BASE_URL", "http://localhost:11434")  # serveur Ollama local (inférence)
OLLAMA_MODEL = _lire("OLLAMA_MODEL", "gemma4:12b")  # LLM rédacteur servi par Ollama
CHROMA_PERSIST_DIR = _lire("CHROMA_PERSIST_DIR", "./data/chroma")  # base vectorielle Chroma (persistante)
DATA_DIR = _lire("DATA_DIR", "./data")  # corpus brut scrapé (non versionné)
RESULTATS_DIR = RACINE / "resultats"  # nos artefacts versionnés (chemin fixe dans le dépôt, non configurable)
