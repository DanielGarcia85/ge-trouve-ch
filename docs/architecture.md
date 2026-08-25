# Architecture technique — Ge-Trouve

Documentation technique du système : comment il est bâti et pourquoi. Elle vise le développeur ou le
mainteneur. Le détail chiffré
et l'historique des décisions vivent dans `docs/journal_des_decisions.md` et `docs/journal_des_mesures.md` ;
la marche à suivre de déploiement dans `docs/plan_developpement.md`.

**Principe directeur : la souveraineté.** Tout tourne en local sur un VPS suisse, en CPU, sans GPU ni appel
à une API externe. Aucune donnée utilisateur ni document ne sort du serveur. Cette contrainte gouverne
chacun des choix ci-dessous.

## 1. Vue d'ensemble

Le système est un assistant conversationnel **RAG** (Retrieval-Augmented Generation) : il répond à une
question en s'appuyant sur des fragments de documents administratifs genevois récupérés par similarité,
plutôt que sur la seule mémoire du modèle.

Deux temps :
- **Indexation (hors ligne, en amont)** : les pages officielles sont aspirées, découpées en fragments,
  encodées en vecteurs, rangées dans une base vectorielle.
- **Réponse (en ligne, à chaque question)** : la question est encodée, les fragments les plus proches sont
  récupérés, puis un modèle de langage rédige une réponse sourcée à partir de ces fragments.

```
INDEXATION (hors ligne)                         RÉPONSE (en ligne)
  ge.ch / geneve.ch                               question de l'usager
        │ scraping                                       │ encodage (Qwen)
        ▼                                                ▼
  pages (JSON)                                    vecteur de la requête
        │ découpage + embeddings (Qwen)                  │ recherche de similarité
        ▼                                                ▼
  base vectorielle Chroma  ─────────────────────▶  top-K fragments
                                                         │ prompt (consigne + fragments + question)
                                                         ▼
                                                  génération (Gemma) ──▶ réponse sourcée
```

Topologie déployée (conteneurs Docker) :

```
Internet ──80/443──▶ caddy (HTTPS) ──▶ app (Streamlit) ──▶ ollama (Gemma + Qwen)
                                             │
                                             └──▶ base Chroma (montée depuis /mnt/data)
```

## 2. Composants et rôles

| Composant | Rôle | Note |
|---|---|---|
| **Haystack** (`haystack-ai`) | orchestration : assemble le pipeline composant par composant | pipelines explicites |
| **Ollama** | serveur d'inférence local (CPU), sert les modèles | 100 % local, `http://ollama:11434` en conteneur |
| **Gemma 4 12B** (`gemma4:12b`) | LLM rédacteur, génère la réponse | Q4_K_M, mode direct (`think=False`) |
| **Qwen3-Embedding-0.6B** (`qwen3-embedding:0.6b`) | embeddings : vectorise questions et fragments | dimension 1024 |
| **Chroma** | base vectorielle embarquée : stocke et retrouve les fragments | mode persistant local |
| **Streamlit** | interface web (page de conversation) | appelle directement le pipeline |
| **Caddy** | reverse proxy, HTTPS automatique | seul service exposé à Internet |

## 3. Flux d'une requête

Orchestré par `src/repondre.py`, exposé par `src/app/app.py`.

1. L'usager pose sa question dans l'interface Streamlit.
2. La question est encodée par Qwen. Asymétrie assumée : la **requête** est préfixée par la consigne de
   tâche Qwen (`Instruct: …\nQuery:…`), tandis que les **documents** ont été indexés sans consigne.
3. Le retriever Chroma renvoie les **top-K fragments** les plus proches (K = 5), avec leurs métadonnées
   (url, titre, date de capture).
4. Le `ChatPromptBuilder` assemble le prompt : message **système** = la consigne de génération (variante V5),
   message **utilisateur** = les extraits (chacun précédé de son URL) puis la question.
5. Gemma génère en **mode direct** (réflexion désactivée), au régime de production (température 0.3,
   top_p 0.95, top_k 64, `num_predict` 1024, `num_ctx` 4096, sans seed).
6. La réponse s'affiche **en streaming** (mot à mot) ; les pages sources apparaissent en barre latérale.

Chaque question est **indépendante** : aucune mémoire conversationnelle n'est envoyée au modèle.

## 4. Indexation (hors ligne)

Traitement en amont, rejouable (voir `docs/reconstruire_la_base.md`) :

1. **Découverte** : les URL du corpus cantonal (`ge.ch`, `geneve.ch`) sont listées via les sitemaps
   (`scripts/scraping/decouvrir_sitemap.py`), dans un manifeste versionné (`src/scraping/manifeste_sources.csv`).
2. **Scraping** (`src/scraping/scrape_complet.py`) : téléchargement poli (robots.txt respecté, délai),
   extraction du contenu (trafilatura) en conservant les hyperliens, un JSON par page.
3. **Indexation** (`src/indexing/indexer_complet.py`) : découpage en fragments (200 mots, recouvrement 40),
   encodage Qwen, écriture dans Chroma avec métadonnées par fragment.

Le corpus brut et la base (`data/`) ne sont **pas versionnés** (régénérables via ce pipeline) ; en
production, la base est **copiée** telle quelle sur le VPS.

## 5. Déploiement

Conteneurisé avec **Docker Compose** (`deploy/docker-compose.yml`), sur un VPS Infomaniak Serveur Cloud
(AMD EPYC-Genoa, 6 vCPU / 18 Go, Ubuntu 24.04, datacenter suisse). Quatre services :

- **ollama** : sert les modèles ; gardés résidents (`OLLAMA_KEEP_ALIVE=-1`), une génération à la fois
  (`OLLAMA_NUM_PARALLEL=1`, garde-fou mémoire) ;
- **ollama-pull** : service one-shot qui tire au démarrage les modèles déclarés par `config.py` ;
- **app** : l'image de l'application (Streamlit + pipeline), exécutée par un utilisateur non privilégié ;
- **caddy** : HTTPS automatique (Let's Encrypt), redirection `www` vers l'apex, seul à publier 80 et 443.

La base Chroma est montée depuis l'hôte (`/mnt/data/chroma`) ; modèles et certificats vivent dans des
volumes nommés. **Sécurité** : SSH par clé seule (root désactivé), UFW, fail2ban, stockage Docker sur le
disque de données. **Livraison continue** : un runner GitHub auto-hébergé déploie sur push (changements de
code ou de config uniquement). Détail et retours d'expérience (incident OOM, résilience, latence) :
`docs/journal_des_decisions.md` (entrées des 23 et 25.08) et `docs/journal_des_mesures.md`.

## 6. Organisation du code

```
src/
  config.py            source unique de configuration (URL Ollama, modèles, chemins)
  repondre.py          pipeline de réponse (recherche + génération)
  pull_modeles.py      provisionnement des modèles (lit config.MODELES_A_TIRER)
  scraping/            aspiration des sources officielles
  indexing/            découpage, embeddings, indexation
  generation/          consigne système et jeu de mise au point
  app/                 interface Streamlit
scripts/               utilitaires hors pipeline (mesures, découverte, setup)
deploy/                conteneurisation (Dockerfile, docker-compose.yml, Caddyfile)
.github/workflows/     livraison continue (deploy.yml)
```

`config.py` est la **source unique** des paramètres : il lit les variables d'environnement du shell (posées
par docker-compose en production), sinon ses valeurs par défaut. **Aucun fichier `.env`** (aucun secret à
cacher, contrainte de souveraineté).

## 7. Renvois

- Décisions techniques datées : `docs/journal_des_decisions.md`
- Mesures (RAM, latence, débits) : `docs/journal_des_mesures.md`
- Marche à suivre de déploiement : `docs/plan_developpement.md`
- Régénération du corpus et de la base : `docs/reconstruire_la_base.md`
