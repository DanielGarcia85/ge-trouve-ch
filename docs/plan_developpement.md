# Plan de développement — Ge-Trouve

Ce document liste les étapes de la phase pratique (Partie 2 Développement, puis Partie 3 Évaluation),
leur contenu et la règle transversale. C'est un **document vivant**, tenu à jour au fil
de l'avancement.

Les **sous-étapes détaillées, avec leurs commandes d'exécution**, sont ajoutées à mesure qu'on atteint
chaque étape : elles servent de mode d'emploi pour **rejouer le jalon depuis zéro**. Une étape non encore
atteinte n'est pas détaillée (règle de non-présomption) ; ses sous-étapes s'écrivent quand on
y arrive. À ce jour, les étapes **0 à 6** sont toutes détaillées et réalisées (étapes 0 à 5 = Partie 2 ; étape 6 = Partie 3, évaluation).

Le détail par décision vit dans `docs/journal_des_decisions.md`, les chiffres dans
`docs/journal_des_mesures.md`.

---

## Les étapes (0 à 6)

**Étape 0 — Environnement local** *(fait)*
Ollama et les trois modèles (Gemma 4 12B, Llama 3.1 8B, Qwen3-Embedding-0.6B), Python, `haystack-ai`
et `chroma-haystack`. Surtout : les premières mesures datées (RAM et vitesse en CPU), dont découle tout
le dimensionnement du VPS. Installé et mesuré sur les deux postes.

**Étape 1 — Pipeline pilote (permis de séjour)** *(fait)*
Premier pipeline complet, de bout en bout, sur un périmètre pilote (une vingtaine de pages `www.ge.ch`
du permis de séjour) : scraping, découpage en fragments avec métadonnées, indexation dans Chroma, et
première réponse à la question type avec ses sources, le tout mesuré. Détail des sous-étapes plus bas.

**Étape 2 — Consigne de génération** *(fait)*
La consigne (prompt système) de génération, écrite et testée. Variante V3 retenue (réponse complète et
fondée sur les extraits, citation des pages sources, orientation hors corpus), régime de production acté.
Elle remplace la consigne provisoire de l'étape 1.

**Étape 3 — Corpus complet** *(fait)*
Le corpus complet avec son script d'ingestion reproductible, dont le périmètre est aligné sur les
familles de démarches du futur jeu de questions d'évaluation.

**Étape 4 — Interface** *(fait)*
L'interface web par laquelle l'usager pose sa question.

**Étape 5 — Consolidation et déploiement** *(fait)*
Mesures consolidées, choix du palier VPS, puis déploiement conteneurisé (Docker Compose, Caddy, HTTPS)
et CI/CD (runner GitHub auto-hébergé). Système en ligne sur `ge-trouve.ch`.

**Étape 6 — Évaluation** *(Partie 3)*
L'évaluation du système selon le protocole du chapitre 7 (RAGAS, jeu de questions genevoises,
contrôle humain).

---

## Sous-étapes de l'étape 0 *(terminée)*

- **0.1 Ollama et modèles** : installer Ollama, puis tirer les trois modèles. **Commande :** `./scripts/setup/pull_modeles.ps1` (gemma4:12b, llama3.1:8b, qwen3-embedding:0.6b).
- **0.2 Python et dépendances** : le projet vit sur deux postes, donc un venv par poste (`.venvdaniel` / `.venvgarciad`) ; puis installer les paquets épinglés. **Commande :** `pip install -r requirements.txt`.
- **0.3 Relevé du poste** : machine, RAM, disque, versions (Python, Ollama, git). **Commande :** `./scripts/mesures/releve_poste.ps1`.
- **0.4 Mesures de base** : débit de génération, latence et débit d'embeddings, RAM par état. **Commandes :** `python scripts/mesures/bench_generation.py` ; `python scripts/mesures/bench_embeddings.py` ; `./scripts/mesures/releve_ram.ps1`.

---

## Sous-étapes de l'étape 1 *(terminée)*

- **1.1 État des lieux** *(lecture seule)* : dépôt propre, venv et imports, modèles Ollama, `.env`, disque.
- **1.2 Manifeste et robots** : `src/scraping/manifeste_sources_pilote.csv` versionné, vérification `robots.txt`, verdict consigné. **Commandes :** `python scripts/scraping/verifier_robots.py` (contrôle robots) ; `python scripts/scraping/lister_souspages_chapeau.py` (découverte des sous-pages, appoint).
- **1.3 Scraper** : téléchargement poli des pages du manifeste vers `data/pages/pilote/` (un JSON par page), journal dans `resultats/pilote/`. **Commande :** `python src/scraping/scrape_pilote.py`.
- **1.4 Indexation** : découpage, embeddings Qwen, écriture dans Chroma avec métadonnées par fragment. **Commande :** `python src/indexing/indexer_pilote.py`.
- **1.5 Pipeline de réponse** : recherche (embedder requête + retriever Chroma) puis génération (Gemma, mode direct). **Commande :** `python src/repondre.py "Où déposer ma demande de permis de séjour ?"`.
- **1.6 Exécution et mesures** : latence de bout en bout, RAM du pipeline chargé, réponse archivée dans `resultats/pilote/`. **Commande :** `python scripts/mesures/bench_pipeline.py`.
- **1.7 Clôture** : entrée au journal des décisions, mise à jour du README.

---

## Sous-étapes de l'étape 2 *(terminée)*

- **2.1 État des lieux** *(lecture seule)* : dépôt propre, venv et Ollama, index pilote en place.
- **2.2 Cadrage exécutable** : consigne externalisée dans un fichier versionné ; jeu de 8 questions de mise au point (6 tirées du corpus pilote, 2 hors corpus) ; script de comparaison (réponses et latences archivées dans `resultats/consignes/`, versionné). *(Fichiers créés : `src/generation/consignes.py`, `src/generation/questions_mise_au_point_pilote.py`, `scripts/mesures/comparer_consignes.py`.)*
- **2.3 Variantes de consigne** : V0 (témoin, la provisoire), V1 (structurée), V2 (V1 plus l'ignorance avouée et l'orientation), puis **V3 retenue** (complète et fondée, cite les pages sources, oriente hors corpus, contacts seulement s'ils figurent dans les extraits, sans rien inventer).
- **2.4 Essais** : variantes jouées sur les 8 questions (clés dans `A_ESSAYER`), régime modéré (température basse ; le régime « éditeur » s'est révélé trop bavard et lent sur CPU), seed fixé pour comparer à conditions égales ; grille de lecture, puis **arbitrage manuel** de la variante retenue. **Commande :** `python scripts/mesures/comparer_consignes.py` (écrit un fichier daté `comparaison_consignes_<variantes>_<date>.md`).
- **2.5 Clôture** : consigne V3 intégrée (`CONSIGNE_ACTIVE`) et régime de production acté (`OPTIONS`) ; session au journal des mesures ; entrée au journal des décisions ; rédaction de la section 10.5 du mémoire.

---

## Sous-étapes de l'étape 3 *(terminée)*

Le corpus est **cantonal** :
`ge.ch` et `geneve.ch`. La législation (`silgeneve.ch`), les autres communes et les assurances sociales
restent des extensions ouvertes, activées seulement si l'évaluation révèle un manque.

- **3.1 État des lieux** *(lecture seule)* : dépôt propre, venv, Ollama et les trois modèles, index pilote présent.
- **3.2 Liens préservés (verrou, validé d'abord sur le pilote)** : adapter l'extraction pour conserver les hyperliens dans le texte ; re-scraper et ré-indexer le pilote ; vérifier que la réponse peut citer le lien du guichet en ligne. GO avant d'élargir. **Commandes :** `python src/scraping/scrape_pilote.py` (re-scrape) ; `python src/indexing/indexer_pilote.py` (ré-indexation).
- **3.3 Manifeste du corpus** : liste des pages `ge.ch` (catalogue des démarches, pages pratiques, e-démarches publiques) et `geneve.ch` (dossier `/demarches/`), dans un `manifeste_sources.csv` complet (le manifeste pilote reste en l'état). **Commande :** `python scripts/scraping/decouvrir_sitemap.py <url_sitemap> [--garder demarches] [--sortie src/scraping/manifeste_sources.csv]` (un passage par domaine : ge.ch en mode par défaut, geneve.ch avec `--garder demarches`) ; méthode dans `scripts/scraping/decouverte_corpus.md`.
- **3.4 Scraping complet** : `robots.txt` vérifié par domaine (refus = arrêt, aucun contournement), délai ≥ 2 s, titre extrait de chaque page, reprise (page déjà scrapée sautée), journal résumé. **Commande :** `python src/scraping/scrape_complet.py`.
- **3.5 Indexation complète et mesures** : reconstruction propre, encodage par lots avec reprise, métadonnées par fragment (`url`, `titre`, `date_capture`, `position`) ; **liens vers les PDF/documents conservés** (le contenu des PDF n'est pas indexé à ce stade, à revoir si l'évaluation le justifie) ; contrôle qualitatif (réponse type avec lien) ; mesures au journal. **Commandes :** `python src/indexing/indexer_complet.py` ; `python src/indexing/indexer_complet.py --reprise` (après interruption).
- **3.6 Clôture** : entrée au journal des décisions (corpus arrêté et volumes, préservation des liens, PDF en liens) ; renommage `repondre_pilote.py` → `repondre.py` ; plan et documentation à jour ; rédaction de la section 10.6.

---

## Sous-étapes de l'étape 4 *(terminée)*

L'interface **Streamlit** (arrêtée en 9.5) qui appelle directement `src/repondre.py` et affiche la réponse
avec ses pages sources. Une pièce d'assemblage locale, pas un maillon RAG : la structure du pipeline est
consommée telle quelle (régime de production, top_k 5). La consigne a été révisée à l'étape 4 (**V5**,
retrait de la liste « Sources » redondante avec la barre latérale ; voir journal des décisions).

- **4.1 État des lieux** *(lecture seule)* : dépôt propre, venv, Ollama et modèles, base complète présente (`data/chroma/`, 9651 fragments), `src/repondre.py` opérationnel.
- **4.2 Mesure préalable** : latence de bout en bout sur le corpus complet (question type, régime de production ; une passe à froid puis trois à chaud, médiane), sur les deux postes. Session datée au journal des mesures. **Commande :** `python scripts/mesures/bench_pipeline.py`.
- **4.3 Dépendance** : `streamlit` épinglé dans `requirements.txt` (installé depuis PyPI après GO). **Commande :** `pip install streamlit`.
- **4.4 Application** : page de conversation Streamlit (`src/app/app.py`, config `.streamlit/config.toml`) appelant `repondre.py` (titre, champ de question, réponse en markdown avec liens cliquables, pages sources en barre latérale). Réponse **diffusée en continu** (streaming, retenu) avec **indicateur d'état** ; préchargement des modèles **écarté** (reporté à l'étape 5, via `keep_alive`) ; consigne **révisée en V5**. **Commande :** `streamlit run src/app/app.py`.
- **4.5 Exécution, captures et mesures** : test sur la question type et une question hors corpus ; captures dans `resultats/interface/` (matière du chapitre 11) ; mesures d'expérience (temps jusqu'au premier mot, temps total) sur les deux postes, au journal. **Commandes :** `python scripts/mesures/bench_pipeline.py` (appel direct) ; `python scripts/mesures/bench_pipeline.py --streaming` (comme l'app, valide l'absence de surcoût du streaming).
- **4.6 Clôture** : entrée au journal des décisions (structure retenue, streaming retenu et préchargement reporté, indicateur d'état, consigne V5, mesures) ; plan et documentation à jour.

---

## Sous-étapes de l'étape 5 *(terminée)*

Déploiement du système sur un VPS Infomaniak (Serveur Cloud, 6 vCPU / 18 Go, Ubuntu 24.04 LTS, datacenter
suisse), conteneurisé avec Docker Compose (services Ollama, application Streamlit, reverse proxy Caddy) et
livré par un pipeline GitHub Actions avec un runner self-hosted sur le VPS. Principe : rendre le service
vivant d'abord (5.1 à 5.4), brancher le pipeline ensuite (5.5 et 5.6). L'organisation des fichiers et le
patron du runner reprennent une infrastructure existante d'un autre projet, en adaptant
nginx en Caddy et sans base PostgreSQL (la seule donnée persistante est la base Chroma, régénérable).

Les commandes ci-dessous sont **celles réellement exécutées** sur le VPS Infomaniak Serveur Cloud
(6 vCPU / 18 Go, Ubuntu 24.04 LTS), pour qu'un tiers puisse reproduire l'installation de zéro. Détail
des décisions et des incidents au journal des décisions (entrée du 25.08).

- **5.1 Préparation et sécurisation du serveur** *(terminée)* : mise à jour puis reboot ; compte admin
  `danielgarcia` (sudo, clé SSH ed25519) ; **durcissement SSH** (clé seule, root désactivé) ; **UFW** ;
  **fail2ban** ; **Docker** avec son stockage déplacé sur le disque de données `/mnt/data`. **Commandes :**
  `sudo apt update && sudo apt upgrade -y && sudo reboot` ;
  `sudo adduser danielgarcia && sudo usermod -aG sudo danielgarcia` (+ clé publique dans
  `~danielgarcia/.ssh/authorized_keys`) ;
  fichier `/etc/ssh/sshd_config.d/99-hardening.conf` (`PermitRootLogin no`, `PasswordAuthentication no`,
  `PubkeyAuthentication yes`) puis `sudo sshd -t && sudo systemctl reload ssh` ;
  `sudo ufw allow 22,80,443/tcp && sudo ufw enable` ;
  `sudo apt install -y fail2ban` + jail `sshd` dans `/etc/fail2ban/jail.local` ;
  Docker : `curl -fsSL https://get.docker.com | sudo sh`, data-root sur `/mnt/data/docker`
  (`/etc/docker/daemon.json`), `sudo usermod -aG docker danielgarcia`.
  À compléter côté **manager Infomaniak** : ouvrir 22, 80 et 443 au pare-feu de l'hébergeur.
  Contenus utiles : `/etc/docker/daemon.json` = `{ "data-root": "/mnt/data/docker" }` ; jail fail2ban
  `[sshd]` avec `enabled = true`, `maxretry = 5`, `findtime = 10m`, `bantime = 1h`. Préalable : le disque
  de données de 250 Go est fourni et monté sur `/mnt/data` par Infomaniak au provisionnement.

- **5.2 Conteneurisation** *(terminée)* : dossier `deploy/` versionné : `Dockerfile` (image de l'app,
  `python:3.13-slim`, utilisateur non privilégié UID 1001), `docker-compose.yml` (services **ollama**,
  **ollama-pull**, **app**, **caddy** ; volumes nommés pour les modèles et les certificats ; base Chroma en
  montage lié ; réseau interne ; `restart: unless-stopped`), `Caddyfile`, `.dockerignore`. Dépôt cloné sur
  le VPS dans `/srv/apps/ge-trouve-ch`. **Commandes :**
  `sudo mkdir -p /srv/apps && sudo chown $USER:$USER /srv/apps` ;
  `git clone https://github.com/DanielGarcia85/ge-trouve-ch.git` ;
  `cd deploy && docker compose config && docker compose build`.

- **5.3 Modèles et base vectorielle** *(terminée)* : les modèles sont tirés **automatiquement** par le
  service one-shot `ollama-pull` (qui lit `config.MODELES_A_TIRER`), pas à la main ; la base Chroma (non
  versionnée) est **copiée une fois** du poste de dev vers `/mnt/data/chroma`, montée en lecture-écriture.
  **Commandes :** `sudo mkdir -p /mnt/data/chroma && sudo chown danielgarcia:danielgarcia /mnt/data/chroma` ;
  depuis le poste de dev, `scp -r data/chroma/* danielgarcia@<ip>:/mnt/data/chroma/` ;
  `docker compose up -d ollama-pull` (tire Gemma et Qwen) puis `docker compose up -d --build app`.

- **5.4 Domaine, proxy et HTTPS** *(terminée)* : enregistrements DNS **A** `ge-trouve.ch` et
  `www.ge-trouve.ch` vers l'IP du VPS (zone DNS Infomaniak) ; Caddy obtient seul les certificats (challenge
  HTTP sur le port 80) et redirige `www` vers l'apex ; l'app n'est jamais joignable directement (seul Caddy
  publie 80/443). **Service en ligne.** **Commande :** `docker compose up -d` (démarre Caddy).

- **5.5 Runner GitHub self-hosted** *(terminée)* : compte de service dédié `github-runner` (sans sudo,
  groupe `docker`), runner installé dans `/opt/runners/ge-trouve` et exécuté en **service systemd**.
  **Commandes :** `sudo useradd -m -s /bin/bash github-runner && sudo usermod -aG docker github-runner` ;
  `sudo chown -R github-runner:github-runner /srv/apps/ge-trouve-ch` ;
  en tant que `github-runner` : téléchargement du runner (commandes et `<jeton>` fournis par GitHub → Settings → Actions → Runners → « New self-hosted runner », image Linux x64) + `./config.sh --url <dépôt> --token <jeton> --name ge-trouve-vps --unattended` ;
  en tant que `danielgarcia` : `sudo ./svc.sh install github-runner && sudo ./svc.sh start`.

- **5.6 Pipeline CI/CD** *(terminée)* : `.github/workflows/deploy.yml`, déclenché **uniquement** sur push
  `main` (jamais sur pull request, pour protéger le dépôt public) : `git pull --ff-only` dans
  `/srv/apps/ge-trouve-ch` puis `docker compose up -d --build`. Approbation exigée pour les workflows de
  forks (Settings → Actions → General). **Déploiement automatisé et validé.**

- **5.7 Mesures de production et clôture** *(terminée)* : mesures sur le VPS réel (débits de prefill et de
  génération, incident OOM, RAM) au journal des mesures ; garde-fou `OLLAMA_NUM_PARALLEL=1` ajouté après
  l'OOM ; guide de reconstruction de la base (`docs/reconstruire_la_base.md`) ; entrée d'exécution au
  journal des décisions (25.08) ; **chapitre 11 rédigé** (Partie 2 complète).

---

## Sous-étapes de l'étape 6 — Évaluation (Partie 3) *(terminée)*

Le système évalué est le **pipeline de production figé** (consigne V5, régime acté, top_k 5) : aucune
retouche pendant l'étape. Le jeu de questions est **d'auteur** (20 questions genevoises) et doit rester
**étanche** : jamais exécuté avant le run officiel, aucun recouvrement avec les 8 questions de mise au point.

- **6.1 Jeu d'évaluation** — fichier de données `evaluation/jeu_evaluation.py` : les 20 questions et leurs
  réponses de référence (champs `id`, `question`, `registre`, `collectivite`, `theme`, `type`,
  `reponse_reference`, `pages_sources`). Les références sont rédigées **à la main depuis le corpus brut**
  (`data/pages/complet/`), jamais via le système, et validées avant toute exécution. **Produit :** le jeu
  figé, entrée de toutes les sous-étapes suivantes.
- **6.2 Outillage** — trois scripts dans `evaluation/` : `executer_banc.py` (le banc), `calculer_ragas.py`
  (la notation), `verifier_cablage.py` (test de câblage du juge sur un échantillon bidon, à lancer une fois
  avant le run). Dépendances d'évaluation à part, hors production : `evaluation/requirements-evaluation.txt`
  (RAGAS 0.4.3 + pile LangChain 0.3.x), installées sur le poste de dev par
  `pip install -r evaluation/requirements-evaluation.txt`.
- **6.3 Run officiel** — sur le poste de développement au repos, OneDrive suspendu, dans cet ordre :
  1. `python evaluation/executer_banc.py` : pose les 20 questions au pipeline figé (une passe, sans seed) et
     **produit** une trace par question dans `resultats/evaluation/traces/` (`q01.json`…`q20.json` : question,
     réponse, fragments + URL, latence) plus `run_info.json`.
  2. `python evaluation/calculer_ragas.py` : lit les traces, calcule les 4 métriques (juge `llama3.1:8b`
     température 0, encodeur `qwen3-embedding:0.6b`, en série) et **produit** `resultats/evaluation/scores/`
     (`scores_par_question.json` et `scores_agreges.json`).
  Scores consignés au journal des mesures ; une seule passe, aucune relance sélective.
- **6.4 Contrôle humain** — fichier `resultats/evaluation/controle_humain.md` : grille sur **un quart** des
  réponses (5 sur 20, tirées au hasard), remplie **à la main et à l'aveugle** (avant de voir les scores
  RAGAS) ; verdicts sur les 5 critères et classement des défauts sur les 7 points de Barnett (Tableau 7.1).
- **6.5 Clôture** — entrées aux journaux (décisions et mesures), plan et documentation à jour, commits, et
  synthèse des résultats pour la rédaction du chapitre 12.

**Réalisé (27.08.2026).** Les cinq sous-étapes sont exécutées. Le contrôle humain (6.4) a porté sur
**5 réponses**, soit un quart du jeu, conforme au chapitre 7.4. Une **vérification indépendante des
références** a précédé la notation finale (9 retouches mineures). Scores au journal des mesures, incidents au
journal des décisions (entrée « Étape 6 terminée »). Restent la **rédaction du chapitre 12** et les
**commits**.

---

## Règle transversale

Chaque jalon technique produit **dans la foulée** sa section rédigée du mémoire, ses mesures datées et
son commit. On ne prend pas d'avance de code sur la rédaction.
