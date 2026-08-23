# deploy/Dockerfile
#
# Image de l'application Ge-Trouve (interface Streamlit + pipeline RAG)
# ─────────────────────────────────────────────────────────────────────────────
#
# Responsabilité
# ──────────────
# Construire une image autonome qui sert l'interface web (src/app/app.py) en
# s'appuyant sur le pipeline de réponse (src/repondre.py). L'image contient le
# code et ses dépendances Python, rien d'autre : NI les modèles (servis par le
# conteneur « ollama »), NI la base Chroma (montée en volume au démarrage). Elle
# ne fait aucune indexation ni aucun scraping.
#
# Contexte de build : la racine du dépôt (voir docker-compose.yml).

FROM python:3.13-slim
#variante « slim » (Debian minimal, sans outils superflus)

# Pas de fichiers .pyc, sortie non tamponnée (les logs remontent en direct).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances d'abord (couche mise en cache tant que requirements.txt ne change pas).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code de l'application et configuration de l'interface.
COPY src/ ./src/
COPY .streamlit/ ./.streamlit/

# Exécution sous un utilisateur non privilégié (l'app n'a besoin d'aucun droit root).
RUN useradd --create-home --uid 10001 appuser
USER appuser

# Port interne de Streamlit (atteint uniquement par Caddy, jamais publié sur l'hôte).
EXPOSE 8501

# Interface web : écoute sur toutes les interfaces du conteneur, sans ouverture de
# navigateur ni invite (mode « headless »). La config du thème est lue depuis .streamlit/.
CMD ["streamlit", "run", "src/app/app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
