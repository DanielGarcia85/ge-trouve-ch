# Plan de développement — Ge-Trouve

Ce document liste les étapes de la phase pratique (Partie 2 Développement, puis Partie 3 Évaluation),
leur contenu et la règle transversale. C'est un **document vivant**, tenu à jour au fil
de l'avancement.

Les **sous-étapes détaillées, avec leurs commandes d'exécution**, sont ajoutées à mesure qu'on atteint
chaque étape : elles servent de mode d'emploi pour **rejouer le jalon depuis zéro**. Une étape non encore
atteinte n'est pas détaillée (règle de non-présomption) ; ses sous-étapes s'écrivent quand on
y arrive. À ce jour, les étapes **0 à 3** sont détaillées plus bas (l'étape 3 est en cours, son ossature
prévisionnelle est posée ci-dessous).

Le détail par décision vit dans `docs/decisions/journal-des-decisions.md`, les chiffres dans
`docs/mesures/journal-des-mesures.md`.

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

**Étape 3 — Corpus complet**
Le corpus complet avec son script d'ingestion reproductible, dont le périmètre est aligné sur les
familles de démarches du futur jeu de questions d'évaluation.

**Étape 4 — Interface**
L'interface web par laquelle l'usager pose sa question.

**Étape 5 — Consolidation et déploiement**
Mesures consolidées, choix du palier VPS, puis déploiement.

**Étape 6 — Évaluation** *(Partie 3)*
L'évaluation du système selon le protocole du chapitre 7 (RAGAS, jeu de questions genevoises,
contrôle humain).

---

## Sous-étapes de l'étape 0

- **0.1 Ollama et modèles** : installer Ollama, puis tirer les trois modèles. **Commande :** `.\scripts\setup\pull_modeles.ps1` (gemma4:12b, llama3.1:8b, qwen3-embedding:0.6b).
- **0.2 Python et dépendances** : le projet vit sur deux postes, donc un venv par poste (`.venvdaniel` / `.venvgarciad`) ; puis installer les paquets épinglés. **Commande :** `pip install -r requirements.txt`.
- **0.3 Relevé du poste** : machine, RAM, disque, versions (Python, Ollama, git). **Commande :** `.\scripts\mesures\releve_poste.ps1`.
- **0.4 Mesures de base** : débit de génération, latence et débit d'embeddings, RAM par état. **Commandes :** `python scripts\mesures\bench_generation.py` ; `python scripts\mesures\bench_embeddings.py` ; `.\scripts\mesures\releve_ram.ps1`.

---

## Sous-étapes de l'étape 1

- **1.1 État des lieux** *(lecture seule)* : dépôt propre, venv et imports, modèles Ollama, `.env`, disque.
- **1.2 Manifeste et robots** : `manifeste_sources_pilote.csv` versionné, vérification `robots.txt`, verdict consigné. **Commandes :** `python scripts\scraping\verifier_robots.py` (contrôle robots) ; `python scripts\scraping\lister_souspages_chapeau.py` (découverte des sous-pages, appoint).
- **1.3 Scraper** : téléchargement poli des pages du manifeste vers `data/pilote/pages/` (un JSON par page), journal dans `resultats/pilote/`. **Commande :** `python src\scraping\scrape_pilote.py`.
- **1.4 Indexation** : découpage, embeddings Qwen, écriture dans Chroma avec métadonnées par fragment. **Commande :** `python src\indexing\indexer_pilote.py`.
- **1.5 Pipeline de réponse** : recherche (embedder requête + retriever Chroma) puis génération (Gemma, mode direct). **Commande :** `python src\repondre_pilote.py "Où déposer ma demande de permis de séjour ?"`.
- **1.6 Exécution et mesures** : latence de bout en bout, RAM du pipeline chargé, réponse archivée dans `resultats/pilote/`. **Commande :** `python scripts\mesures\bench_pipeline.py`.
- **1.7 Clôture** : entrée au journal des décisions, mise à jour du README.

---

## Sous-étapes de l'étape 2

- **2.1 État des lieux** *(lecture seule)* : dépôt propre, venv et Ollama, index pilote en place.
- **2.2 Cadrage exécutable** : consigne externalisée dans un fichier versionné ; jeu de 8 questions de mise au point (6 tirées du corpus pilote, 2 hors corpus) ; script de comparaison (réponses et latences archivées dans `resultats/consignes/`, versionné). *(Fichiers créés : `src/generation/consignes.py`, `src/generation/questions_mise_au_point_pilote.py`, `scripts/mesures/comparer_consignes.py`.)*
- **2.3 Variantes de consigne** : V0 (témoin, la provisoire), V1 (structurée), V2 (V1 plus l'ignorance avouée et l'orientation), puis **V3 retenue** (complète et fondée, cite les pages sources, oriente hors corpus, contacts seulement s'ils figurent dans les extraits, sans rien inventer).
- **2.4 Essais** : variantes jouées sur les 8 questions (clés dans `A_ESSAYER`), régime modéré (température basse ; le régime « éditeur » s'est révélé trop bavard et lent sur CPU), seed fixé pour comparer à conditions égales ; grille de lecture, puis **arbitrage manuel** de la variante retenue. **Commande :** `python scripts\mesures\comparer_consignes.py` (écrit un fichier daté `comparaison_consignes_<variantes>_<date>.md`).
- **2.5 Clôture** : consigne V3 intégrée (`CONSIGNE_ACTIVE`) et régime de production acté (`OPTIONS`) ; session au journal des mesures ; entrée au journal des décisions ; rédaction de la section 10.5 du mémoire.

---

## Sous-étapes de l'étape 3 *(en cours)*

Ossature prévisionnelle ; les commandes s'ajoutent à mesure de l'exécution. Sources du cœur : `ge.ch`,
`getax.ch`, `geneve.ch`, `ch.ch`, `sem.admin.ch`. `silgeneve.ch` est un candidat, décidé au contrôle
`robots.txt` ; les autres communes et les assurances sociales restent des extensions ouvertes.

- **3.1 État des lieux** *(lecture seule)* : dépôt propre, venv, Ollama et les trois modèles, index pilote présent.
- **3.2 Liens préservés (verrou, validé d'abord sur le pilote)** : adapter l'extraction pour conserver les hyperliens dans le texte ; re-scraper et ré-indexer le pilote ; vérifier que la réponse peut citer le lien du guichet en ligne. GO avant d'élargir.
- **3.3 Manifeste cantonal (C1)** : liste des pages `ge.ch` (catalogue des démarches, pages pratiques, e-démarches publiques), `getax.ch` et `geneve.ch`, dans un `manifeste_sources.csv` complet (le manifeste pilote reste en l'état) ; niveau `cantonal`.
- **3.4 Manifeste fédéral (C2)** : pages `ch.ch` et `sem.admin.ch` sur les thématiques de C1 ; niveau `federal`.
- **3.5 Scraping complet** : `robots.txt` vérifié par domaine (refus = arrêt, aucun contournement), délai ≥ 2 s, journal d'exécution, échecs consignés. Scraper dédié (`scrape_complet.py`).
- **3.6 Indexation complète et mesures** : reconstruction idempotente, métadonnées complètes (niveau) ; **PDF indexés** (texte extrait à l'ingestion, lien officiel conservé, fichier non stocké) ; contrôles qualitatifs (réponse type avec lien, question à versant fédéral, démonstration de recherche filtrée par niveau) ; mesures au journal.
- **3.7 Clôture** : entrée au journal des décisions (manifeste arrêté et volumes, préservation des liens, PDF, C3 conditionnel) ; plan et documentation à jour ; rédaction de la section 10.6.

---

## Règle transversale

Chaque jalon technique produit **dans la foulée** sa section rédigée du mémoire, ses mesures datées et
son commit. On ne prend pas d'avance de code sur la rédaction.
