# Journal des décisions techniques — Ge-Trouve

Ce fichier consigne les décisions techniques du projet, au fur et à mesure qu'elles sont arrêtées.
Chaque entrée précise sa date, ce qu'elle tranche, ses motifs, ce qui reste ouvert, et son lien avec
le mémoire. Une décision reste valable jusqu'à révision explicite, consignée à son tour ici.

Les décisions les plus récentes sont ajoutées en haut.

---

## 2026-08-29 — Refonte complète du README

Le README est entièrement refondu, avec une nouvelle structure : présentation du projet, résultats d'évaluation, guide d'installation, déploiement, licence et citation. La licence reste MIT pour le code seul, les documents administratifs indexés demeurant la propriété de leurs ayants droit. Les décisions figées du README sont conservées : aucune émoticône, schéma d'architecture montrant l'utilisateur, le reverse proxy et la voie d'indexation hors ligne, formulation prudente sur l'absence de concurrent identifié, déclaration de l'usage de l'IA en deux énoncés (aucun service d'IA externe en production, modèle open source exécuté localement), sans pondérations ni calendrier.

---

## 2026-08-28 et 29 — Intégration du retour du directeur et rédaction finale

Jalon rédactionnel : le retour du directeur est intégré et la rédaction du mémoire est achevée. Deux nouvelles sections au chapitre 8, 8.4 « L'analyse du besoin » et 8.5 « L'existant et le positionnement », appuyées par une analyse SWOT (Figure 8.1) et une analyse PESTEL (Figure 8.2) et par douze sources « Existant » ajoutées à la bibliographie. Les liminaires et la fermeture sont écrits : conclusion (réponse à la question de recherche, leviers, limites, perspectives), introduction, résumé et remerciements. L'image filée de l'orchestre (chef et musiciens) et la parenté des candidats ont été entièrement retirées du document. Restent l'allègement des chapitres 2 et 4 et la passe finale (mise à jour des champs et des listes, bibliographie, PDF, Compilatio) avant la remise du 31 août.

---

## 2026-08-28 — Chapitre 12 rédigé : Partie 3 complète

Jalon rédactionnel : le chapitre 12 (résultats de l'évaluation) est inséré au mémoire, quatre sections et une fermeture. La section 12.1 raconte le protocole exécuté (20 questions d'auteur, 16 avec réponse et 4 hors périmètre, références bâties depuis le corpus, étanchéité totale) et consigne un constat d'honnêteté : le branchement direct Haystack-RAGAS n'a pas pu être établi avec la version retenue de la bibliothèque, RAGAS a été enveloppé par ses composants LangChain pour Ollama, et le critère d'intégration du chapitre 3 n'aura donc pas servi ; la Figure 12.1 (nouvelle) schématise ce câblage. La 12.2 présente les moyennes sur les questions avec réponse (précision 0,92, rappel 0,93 agrégé sur 15 avec la réserve Q05, fidélité 0,85, pertinence 0,71) : récupération forte, fidélité aux erreurs de fusion sans invention, pertinence tirée par la verbosité. La 12.3 traite les hors périmètre cas par cas et le garde-fou humain (cinq relectures à l'aveugle, grille controle_humain.md), dont la question 8, fidèle mais hors sujet, attrapée par l'humain seul : l'angle mort de RAGAS. La 12.4 classe les défauts sur quatre des sept points de Barnett (trois jamais apparus) et esquisse les leviers sans les développer (consigne plus courte, échantillonnage centralisé dans src/config.py, changement de modèle en une ligne relayé par le CI/CD, palier de serveur), le contrôle humain restant à conserver ; la conclusion développera. Deux annexes nouvelles : l'Annexe 4 (les 20 questions verbatim avec leurs quatre scores, la ligne Moyenne AR, la réserve Q05, les cinq verdicts humains, renvoi aux traces du dépôt) et l'Annexe 5 (calcul des quatre métriques en deux étages, illustrée par annexe_5_metriques_ragas.svg). Un seul appel de citation ajouté (fiche RAGAS existante), aucune fiche Zotero nouvelle. Restent la conclusion, l'introduction à ajuster et le résumé, côté rédaction.

---

## 2026-08-27 — Étape 6 terminée : évaluation exécutée

Protocole du chapitre 7 appliqué au pipeline de production figé (consigne V5, régime acté, top_k 5), sans aucune retouche pendant l'étape. Banc exécuté sur les 20 questions d'auteur (une passe, sans seed, poste de développement) ; notation RAGAS 0.4.3 par le juge local Llama 3.1 8B et l'encodeur Qwen3-Embedding, quatre métriques. Une vérification indépendante des 16 réponses de référence a conduit à 9 retouches mineures, appliquées avant la notation finale. Scores clés (questions avec réponse) : précision du contexte 0.92, rappel 0.93, fidélité 0.85, pertinence 0.71 ; les 4 hors périmètre se lisent séparément (un score bas y signale un refus, le comportement attendu). Écarts consignés : Q05 rappel ignoré (échec technique du juge) ; le juge sur CPU impose une notation en série (délai client du banc relevé à 1200 s au premier appel à froid). Constats : récupération forte, fidélité bonne avec des erreurs de fusion de passages voisins (pas d'invention ex nihilo), pertinence tirée vers le bas par la verbosité, aveu d'ignorance inconstant. Le contrôle humain (entrée du jour) confirme ces scores et rattrape un angle mort du juge (Q08, fidèle mais hors sujet). Détail au journal des mesures et dans `resultats/evaluation/`. Reste la rédaction du chapitre 12.

---

## 2026-08-27 — Étape 6.4 : contrôle humain

Relecture à l'aveugle de 5 réponses sur 20 (Q01, Q05, Q08, Q14, Q17), confrontées aux captures du corpus du 13.08.2026, selon les 5 critères du protocole et la grille de Barnett et al. 2024. Résultats : Q05 sans défaut ; Q01 incomplète (n° 7) avec une fusion erronée (permis Ci) ; Q08 exacte mais hors sujet, section pertinente non extraite (n° 4) ; Q14 exacte mais absence des horaires non avouée (n° 1), rien d'inventé ; Q17 (hors périmètre) sans aveu ni bonne cible (n° 1 + n° 6). Constat transversal : aucune invention ex nihilo ; les erreurs factuelles sont des fusions d'extraits voisins. Critère « bien orientée » précisé : hors périmètre uniquement. Détail dans le fichier de contrôle. Confrontation aux scores RAGAS à suivre (chapitre 12).

---

## 2026-08-25 — Chapitre 11 complet : Partie 2 rédigée en entier (jalon rédactionnel)

**Nature.** Jalon **rédactionnel** (la Partie 2 du mémoire est désormais écrite en entier), pas une décision
technique nouvelle.

**Ce qui est fait (mémoire).** Chapitre 11 achevé : la section 11.3 raconte le déploiement au grain
défendable (serveur et souveraineté, avec la nuance du modèle ouvert exécuté localement ; sécurisation ;
les quatre services du compose ; base copiée et montée ; mise en ligne sans aucun fichier de secrets ;
livraison continue par runner auto-hébergé ; incident mémoire et garde-fou « une génération à la fois » ;
latence **corrigée** : premier mot en 1,5 à 2 min pour une **nouvelle** question, l'ancien « ~1 s » identifié
comme artefact de cache). Notes de bas de page 75 (conteneur) et 76 (livraison continue et runner).
**Figure 11.1** créée et insérée (VPS suisse ; boîte Docker Compose englobant caddy, app, ollama et
ollama-pull ; base Chroma sur le disque de l'hôte montée dans app ; runner à l'intérieur ; usager et dépôt
public à l'extérieur). **Annexe 3** (captures) posée. **Annexe 2 refondue** au grain médian (tableaux de
référence conservés, un tableau de mesures par étape, gros tableaux des étapes 0 et 4 remplacés par leurs
conclusions, correctif du cache intégré, convention V0-V5 ancrée). **Harmonisation de la latence** dans tout
le document (10.4 et 10.5 en fourchettes avec « question rejouée » ; 11.2 renvoyant la mesure à la 11.3).

**Décision d'allègement.** Les mentions DDR restent comme **étiquettes de spécification** (aucun argument ne
s'y appuie plus) ; l'allègement **en volume** des chapitres 2 et 4 est **différé en fin de mémoire**, si le
temps le permet. Aucune fiche Zotero nouvelle.

**Lien avec le mémoire.** Partie 2 **rédigée en entier** ; reste la **Partie 3** (chapitre 12, sur
l'évaluation de l'étape 6).

---

## 2026-08-25 — Étape 5 exécutée : déploiement en production et CI/CD en ligne

**Ce qui est fait.** Le système est **en ligne** sur le VPS Infomaniak Serveur Cloud (6 vCPU / 18 Go,
Ubuntu 24.04 LTS, datacenter suisse, IP publique dédiée), servi en **HTTPS** sur `ge-trouve.ch`, et
**déployé automatiquement à chaque push** sur `main`. Marche à suivre reproductible détaillée dans
`docs/plan_developpement.md` (5.1 à 5.7).

**Serveur et sécurité.** Compte admin **`danielgarcia`** (sudo, clé SSH ed25519) ; login root SSH
désactivé et authentification **par clé seule** (fichier de durcissement `sshd_config.d/99-hardening.conf`) ;
**UFW** (22/80/443) et **fail2ban** (jail sshd) ; pare-feu Infomaniak (niveau manager) ouvert sur 22/80/443.
**Docker** installé depuis le dépôt officiel, avec **data-root déplacé sur `/mnt/data`** (disque de 250 Go)
pour que modèles et images ne saturent pas les 19 Go du disque système.

**Conteneurisation (`deploy/`).** `Dockerfile` (image de l'app, utilisateur non privilégié **UID 1001**
aligné sur `danielgarcia`, propriétaire de la base montée) ; `docker-compose.yml` (services **ollama**,
**ollama-pull**, **app**, **caddy** ; `restart: unless-stopped`) ; `Caddyfile` (HTTPS automatique Let's
Encrypt, redirection `www` vers l'apex) ; `.dockerignore`. Le provisionnement des modèles est **automatisé**
par un service one-shot **`ollama-pull`** (image de l'app) qui exécute `src/pull_modeles.py`, lequel lit
`config.MODELES_A_TIRER` (source **unique** des noms de modèles). Base Chroma **copiée une fois** sur `/mnt/data/chroma` (scp), montée en
**lecture-écriture** (Chroma/SQLite écrit ses fichiers WAL même pour de simples lectures).

**CI/CD.** Runner GitHub Actions **auto-hébergé** sur le VPS, sous un compte dédié **`github-runner`**
(sans sudo, groupe `docker`), en **service systemd** (`/opt/runners/ge-trouve`). Workflow
`.github/workflows/deploy.yml` : déclenché **uniquement** sur push `main` (jamais sur pull request, pour
protéger le dépôt public d'un fork malveillant), fait `git pull` dans `/srv/apps/ge-trouve-ch` puis
`docker compose up -d --build`. Approbation exigée pour les workflows de forks (Settings → Actions).

**Décisions et incidents en cours d'exécution.**
- **Suppression du mécanisme `.env`** : `config.py` lit les variables d'environnement du shell (posées par
  le compose) puis ses valeurs par défaut ; aucun secret (souveraineté), donc **aucun fichier `.env`**.
  `OLLAMA_MODEL` renommé **`OLLAMA_GENERATION_MODEL`** (symétrie avec `OLLAMA_EMBEDDING_MODEL`) ; ajout de
  `MODELES_A_TIRER` (liste unique des modèles à provisionner).
- **Incident OOM** : les deux modèles gardés résidents (`keep_alive=-1`, ≈ 11 Go) plus une génération
  concurrente ont saturé les 18 Go, le noyau (OOM killer) a tué `llama-server`, serveur injoignable.
  **Parade : `OLLAMA_NUM_PARALLEL=1`** (une génération à la fois). Constat à relier au budget mémoire du
  chapitre 4 : le palier 18 Go est **juste**.
- **Résilience** : après reboot, `restart: unless-stopped` + démon Docker systemd ont **relancé le service
  seul**, sans intervention.
- Base **copiée** (pas reconstruite) pour rester identique à la base mesurée et évaluée ; reconstruction
  documentée dans `docs/reconstruire_la_base.md`.

**Écarts avec le plan de conception (23.08).** Pas de dossier `/srv/infra` ni de groupe `deploy` (inutiles :
Caddy est un conteneur du compose, la seule donnée hôte est la base Chroma) ; transfert de la base par
**`scp`** (et non `rsync`) ; provisionnement des modèles **automatisé** (et non manuel) ; le workflow
déploie sans étape de tests Python (déploiement pur).

**Lien avec le mémoire.** Partie 2, chapitre 11 (déploiement) ; mesures de production au journal des mesures.

---

## 2026-08-23 — Étape 5 : architecture de déploiement (VPS souverain, Docker, CI/CD)

**Ce qui est arrêté.** Le système sera déployé sur un **VPS Infomaniak Serveur Cloud** (datacenter suisse),
palier de confort **6 vCPU / 18 Go de RAM** (confirmé par les mesures : Gemma + Qwen tiennent à l'aise à
18 Go), **Ubuntu 24.04 LTS**. La pile est **conteneurisée avec Docker Compose** (Ollama, application
Streamlit, reverse proxy **Caddy** pour l'HTTPS automatique) et livrée par un **pipeline GitHub Actions**
avec un **runner self-hosted sur le VPS** (compte dédié, service systemd) qui déploie sur un push `main`.
Ordre d'exécution : service vivant d'abord, pipeline ensuite. Sous-étapes détaillées dans
`docs/plan_developpement.md`.

**Motifs.**
- **Souveraineté** : tout reste sur le serveur suisse (inférence et déploiement) ; le runner self-hosted
  garde même la chaîne CI/CD dans le serveur, pas sur une infrastructure tierce.
- **Reproductibilité** : Docker Compose fige l'assemblage des briques ; un `docker compose up` relance tout.
- **Sécurité dès le départ** : UFW (22/80/443), SSH par clé seule, login root désactivé, fail2ban ; comptes
  et groupes dédiés (`docker`, `deploy`) plutôt que root. Ces mesures reprennent et devancent les
  recommandations de durcissement d'une infrastructure antérieure de l'auteur.
- **Patron éprouvé** : l'organisation des fichiers (`/srv/apps`, `/srv/infra`, `/opt/runners`) et le flux du
  runner GitHub sont repris d'un serveur existant d'un autre projet perso (adaptation : Caddy au lieu de nginx, pas de
  base PostgreSQL, la seule donnée persistante étant la base Chroma).

**Cadre à garder en tête.** Le déploiement et le CI/CD sont un **apport d'ingénierie et de vitrine** (dépôt
public, démonstration de compétences DevOps), **pas le cœur de la recherche**. Le cœur reste l'apport RAG
(assembler les briques pour combler un vide francophone et local) et son **évaluation** (Partie 3). Les
aspects techniques de déploiement restent donc **instrumentaux et proportionnés** dans le mémoire.

**Lien avec le mémoire.** Partie 2, chapitre du déploiement.

---

## 2026-08-23 — Étape 4 : interface Streamlit et révision de la consigne (V5)

**Ce qui est arrêté.** L'interface web locale (`src/app/app.py`, configuration `.streamlit/config.toml`)
est livrée. Elle appelle directement `src/repondre.py` (pipeline consommé tel quel : consigne active,
régime de production, top_k 5) et affiche la réponse au fil de l'eau avec ses liens cliquables ; les pages
sources récupérées apparaissent dans une barre latérale, vidées dès l'envoi d'un prompt puis remplies à la
réponse. Le choix de Streamlit avait été acté au chapitre 9.

**Conception.** Mise en page en trois bandes figées (en-tête « Ge-Trouve » aux couleurs genevoises, champ
de saisie et bas de page en bas, pages sources à gauche) ; seule la conversation défile. Le streaming se
fait par un simple callback qui remplit une zone mot à mot, **sans aucun JavaScript**. Un indicateur d'état
figé en haut à droite (en attente / génération en cours, clignotant / prêt) signale l'avancement, à la place
d'un indicateur au niveau du message qui se cachait derrière le champ fixe.

**Sous-décisions.**
- **Diffusion progressive (streaming) retenue.** Elle ne réduit pas le temps de calcul mais la latence
  perçue : premier mot en ~1 s à chaud, alors que la réponse complète met ~2 min à s'écrire. Contrepartie
  assumée de la souveraineté (CPU, sans GPU ni API). Chiffres au journal des mesures (2026-08-23).
- **Pas de préchargement des modèles côté application.** Les modèles restent résidents côté Ollama ; le
  maintien au chaud relève du déploiement (`keep_alive`, étape 5), pas de l'application.
- **Pas de mémoire conversationnelle.** Chaque question est traitée indépendamment (le modèle ne reçoit que
  la question courante et ses fragments) ; l'historique reste seulement affiché à l'écran. Cohérent avec le
  Naive RAG et le protocole d'évaluation par question (Partie 3).
- **Révision de la consigne : V5 (révise une décision de l'étape 2).** La liste « Sources » en fin de réponse
  (clause de V3, reprise par V4) faisait doublon avec la barre latérale ; V5 la retire, en conservant la
  reprise des liens fonctionnels dans le corps (guichet en ligne, formulaires). Décision assumée par l'auteur.
  Effet mesuré : réponses plus courtes, génération plus rapide (journal des mesures).

**Mesures.** Latence de l'interface sur les deux postes (GARCIAD référence proche du VPS, DANIELGARCIA
contraste plus rapide), deux modes (appel direct / streaming), à froid et à chaud, plus la RAM du pipeline
chargé. Tableaux et constats au journal des mesures (2026-08-23) ; captures dans `resultats/interface/`.

**Lien avec le mémoire.** Matière du chapitre 11 (interface). Argument à porter : distinguer **latence de
calcul** (inchangée) et **latence perçue** (réduite à ~1 s par le streaming).

---

## 2026-08-13 — Chapitre 10 complet : l'étape 3 racontée au mémoire

**Nature.** Jalon rédactionnel, sans décision technique nouvelle. La section 10.6 (corpus complet :
découverte, scraping, indexation) est rédigée et insérée ; le chapitre 10 est complet et fermé.

**Lien avec le mémoire.** Chapitre 10 (Partie 2), sections 10.1 à 10.6 ; Annexe 2 (mesures) à jour pour
l'étape 3.

**Ce qui est fait.** La 10.6 raconte et justifie l'étape 3 (méthode de découverte par sitemap, périmètre
cantonal, scraping responsable, préservation des liens, indexation, mesures, reprise), chiffres croisés
sur les journaux. Détail des faits et chiffres : entrée du 13.08 (clôture de l'étape 3) et journal des mesures.

**Ce qui reste ouvert.** Interface (étape 4, en cours), déploiement (étape 5), évaluation RAGAS (Partie 3),
conclusion de la Partie 1.

---

## 2026-08-13 — Clôture de l'étape 3 : corpus complet scrapé, indexé, pipeline de production

**Nature.** Clôture de l'étape 3. Le pipeline RAG tourne désormais de bout en bout sur le corpus cantonal
complet (4304 pages), plus seulement sur le pilote.

**Lien avec le mémoire.** Partie 2, section 10.6 (corpus complet et indexation).

**Ce qui est fait.**
- **Corpus scrapé.** 4304 pages sur 4322 du manifeste (ge.ch + geneve.ch) ; 18 exclusions justifiées :
  1 page supprimée (404) et 17 pages d'accès restreint (403 « Page non autorisée », non contournées).
  Scraper `src/scraping/scrape_complet.py` : robots.txt par domaine, délai 2 s, titre extrait de chaque
  page, reprise, journal résumé (`resultats/complet/journal_scraping.md`).
- **Corpus indexé.** 9651 fragments (200 mots, recouvrement 40) dans Chroma, embeddings Qwen, base de
  190,9 Mo. Indexeur `src/indexing/indexer_complet.py` : encodage par lots de pages, reconstruction propre,
  option `--reprise` (aucun doublon, IDs = empreinte du contenu). Débit 0,8 fragment/s ; mesures au journal
  des mesures (13.08).
- **Métadonnées par fragment** : `url`, `titre`, `date_capture`, `position`. Le titre est extrait de la page
  (le manifeste complet n'a qu'une colonne `url`) ; pas de `section` (elle était propre au pilote fait à la main).
- **Liens préservés.** Le texte conserve les hyperliens en absolu ; les liens vers les PDF/documents sont
  donc cités par l'assistant sans que les pages document soient scrapées. Le **contenu** des PDF n'est pas
  indexé à ce stade (à revoir seulement si l'évaluation révèle un manque).
- **Pipeline de production.** `src/repondre_pilote.py` renommé `src/repondre.py` : il ne sert plus le
  pilote mais le corpus complet (références mises à jour). Contrôle qualitatif sur la question type
  concluant (réponse fondée, sourcée, liens cités, plus complète que sur le pilote).

**Leçon d'exécution.** Un traitement long (scraping ~2,4 h, indexation ~3,3 h) sur poste Windows exige de
désactiver la mise en veille (`powercfg /change standby-timeout-ac 0`) et de suspendre OneDrive pendant
l'écriture de la base. La reprise a sauvé l'indexation après une mise en veille intempestive.

**Ce qui reste ouvert.** Interface (étape 4), déploiement (étape 5), évaluation RAGAS (Partie 3). Extension
possible du corpus (autres communes, législation `silgeneve.ch`, contenu des PDF) seulement si l'évaluation
le justifie.

**Outils.** `scrape_complet.py`, `indexer_complet.py`, `repondre.py` ; `decouvrir_sitemap.py` (manifeste).

---

## 2026-08-12 — Étape 3 : corpus cantonal (ge.ch + geneve.ch) et méthode de découverte

**Nature.** Jalon d'exécution de la Partie 2 : découverte des pages à scraper et arrêt du périmètre du
corpus. Le corpus est **cantonal genevois** : ge.ch et geneve.ch, rien d'autre.

**Lien avec le mémoire.** Partie 2, section 10.6 (corpus complet).

**Ce qui est tranché.**
- **Méthode de découverte.** Avant de scraper, on énumère les pages d'un domaine via son **sitemap**, on
  les classe par catégorie (premier segment du chemin), puis on filtre. Outil :
  `scripts/scraping/decouvrir_sitemap.py` ; raisonnement complet dans `scripts/scraping/decouverte_corpus.md`.
- **Périmètre.** Deux sources, toutes deux cantonales genevoises :
  - `ge.ch` : environ **4 072** pages (démarches et dossiers), filtre par défaut (écarter le bruit :
    documents en vrac, actualité, événements, variantes de langue). Sitemap de 27 484 pages au total.
  - `geneve.ch` : **250** pages du dossier `/demarches/`, filtre « ne garder que » (`--garder demarches`).
    Sitemap de 31 218 pages, très majoritairement institutionnel (annuaire, conseil municipal).

**Cheminement.** Le `robots.txt` de chaque domaine a été lu d'abord. ge.ch annonce son sitemap ; geneve.ch
ne l'annonce pas mais l'expose à l'emplacement standard. La répartition par catégorie a montré que « toutes
les démarches » ne sont qu'une petite part de chaque site, d'où le filtrage. Le filtre diffère selon le
rangement du site : exclusion du bruit pour ge.ch (démarches éparpillées), inclusion d'un seul dossier pour
geneve.ch (démarches regroupées).

**Ce qui reste ouvert.** Les autres communes, la législation (`silgeneve.ch`) et les assurances sociales
restent des extensions possibles, activées seulement si l'évaluation (Partie 3) révèle un manque.

**Outils.** `decouvrir_sitemap.py` (sitemap, catégories, filtre) ; `robots.txt` de chaque domaine.

---

## 2026-08-11 — Étape 2 : consigne de génération (V3 retenue) et régime de production

**Nature.** Jalon d'exécution de la Partie 2 : mise au point et choix de la consigne système de génération,
qui remplace la consigne provisoire de l'étape 1. Décision arrêtée après essais comparés.

**Lien avec le mémoire.** Partie 2 (développement), section 10.5 (consigne). Latences et ancrage vérifié
alimentent l'Annexe 2 ; détail chiffré dans `docs/journal_des_mesures.md`.

**Ce qui est tranché.**
- **Consigne retenue : V3** (`src/generation/consignes.py`, `CONSIGNE_ACTIVE`). Elle demande une réponse
  **complète et fondée sur les extraits** (conditions, délais, pièces, démarche), conserve les **noms exacts**
  (offices, formulaires, permis), **cite les pages officielles** (URL fournies avec les extraits) et, hors
  corpus, **avoue son ignorance et oriente** vers le guichet ou le site officiel, sans rien inventer. Les
  formulaires, numéros ou adresses ne sont repris que s'ils figurent dans les extraits.
- **Régime d'échantillonnage de production** (`src/repondre.py`, `OPTIONS`) : température **0.3**,
  top_p 0.95, top_k 64, `num_predict` **1024**, `num_ctx` 4096, **sans seed** (le seed reste un outil de
  comparaison des essais, pas un réglage de production).

**Cheminement.**
- Premiers essais V0/V1/V2 : la contrainte de **brièveté** (poussée par V1/V2) tronquait ou appauvrissait
  les réponses et n'était pas souhaitée. Abandon de la brièveté comme critère, au profit de la complétude
  fondée.
- Constat sur le régime : la température 1.0 « éditeur » rend Gemma bavard et lent sur CPU (mesures au
  journal). Abaissée à 0.3.
- V3 rédigée puis comparée à V0 (essais du 11.08) : V3 l'emporte sur la complétude, la citation des sources
  et l'orientation hors corpus.
- **Ancrage vérifié à la source** : les détails spécifiques de V3 (SEFRI, délai « 6 à 8 semaines », permis
  Ci, accord d'établissement, personnel académique) figurent bien dans le corpus pilote. V3 n'invente pas.

**Outils.** Jeu de 8 questions de mise au point (`src/generation/questions_mise_au_point_pilote.py` : 6 tirées du
corpus, 2 hors corpus ; distinct du jeu d'évaluation du chapitre 7, qui doit arriver vierge en Partie 3) ;
script de comparaison (`scripts/mesures/comparer_consignes.py`) archivant réponses et latences dans
`resultats/consignes/` (versionné), dans un fichier daté et étiqueté par les variantes jouées.

**Ce qui reste ouvert.**
- Latence propre du régime de production à mesurer sur DANIELGARCIA (les essais garciad throttlaient).
- La complétude de V3 ne prendra tout son sens qu'avec le **corpus complet** (étape 3) : formulaires, liens
  et contacts n'existent dans les réponses que si le corpus les contient (le pilote en est pauvre).
- Tirages de stabilité formels (sans seed) allégés : V3 déjà vérifiée, y compris son ancrage.

**Souveraineté.** Inchangée : tout local, aucun appel externe, aucune clé.

**État.** Étape 2 close. Consigne V3 active, régime de production acté. Reste le corpus complet (étape 3).

**Mise à jour (soirée du 11.08).** La latence propre du régime de production a été relevée sur DANIELGARCIA
(détail au journal des mesures) : le point « latence à mesurer » ci-dessus est clos. La section 10.5
(consigne de génération) est rédigée, insérée et vérifiée au mémoire ; l'Annexe 2 porte sa section Étape 2.
Dans la foulée, le dépôt a été réorganisé (résultats versionnés dans `resultats/` hors `data/`, chemins
centralisés, renommages `_pilote`).

---

## 2026-08-10 — Chapitre 10, première vague : pipeline pilote rédigé, palier de confort inscrit

**Nature.** Jalon rédactionnel : la première vague du chapitre 10 (Construction du pipeline RAG) est
rédigée et insérée au mémoire. Elle raconte le pilote de l'étape 1 et inscrit le dimensionnement du
serveur. Pas une nouvelle décision technique, mais la mise en mémoire de décisions déjà prises.

**Lien avec le mémoire.** Chapitre 10, sections 10.1 à 10.4. Les sections 10.5 (consigne, étape 2) et
10.6 (corpus, étape 3) ont leurs titres posés, sans contenu.

**Ce qui est inscrit.**
- 10.1 Le corpus pilote (robots.txt, note 69 ; appels Barbaresi 2026 et Garcia 2026).
- 10.2 L'indexation pilote.
- 10.3 Le pipeline de réponse (Tableau 10.1 : réglages du pilote et leurs statuts).
- 10.4 Les mesures et le palier de serveur : le **palier de confort 18 Go est désormais inscrit au
  mémoire**, le plancher 12 Go étant exclu pour le régime retenu ; la location du VPS (chapitre 11) se
  fera sur cette base.
- Annexe 2 refondue : compilation du journal des mesures (tableaux communs des postes et des modèles,
  sections Étape 0 et Étape 1), avec définition de l'empreinte (taille lue dans `ollama ps`) et de l'écart
  de pagination sur 16 Go.

**Bibliographie.** Une fiche ajoutée : trafilatura (Barbaresi, Adrien, 2026 ; moteur de `HTMLToDocument`).
Capture archivée localement (`biblio/Scraping/`, hors dépôt).

**Décisions éditoriales.** Réponse pilote citée en prose (pas d'annexe dédiée) ; pas d'appels Garcia en
10.3-10.4 (couverts par 10.1, 10.2, l'annexe et le renvoi) ; libellés « PC : DANIELGARCIA / PC : GARCIAD »
conservés en 9.4 ; adresses longues conservées dans la prose de 9.2.

**Ce qui reste ouvert.** Consigne de génération (10.5 = étape 2, en cours) ; corpus complet et ingestion
reproductible (10.6 = étape 3).

**État.** Chapitre 10 rédigé jusqu'en 10.4. Palier de confort inscrit. Étape 2 en cours.

---

## 2026-08-07 — Étape 1 : pipeline pilote (permis de séjour)

**Nature.** Jalon d'exécution : premier pipeline RAG complet, de bout en bout, sur un périmètre pilote.
Pas une décision de choix (la pile est arrêtée en Partie 1), mais sa première mise en œuvre.

**Lien avec le mémoire.** Partie 2 (développement). Les mesures alimentent l'Annexe 2 ; la réponse
archivée est citée en prose dans le mémoire. Détail chiffré : `docs/journal_des_mesures.md`.

**Ce qui est construit.**
- Manifeste versionné de 23 URL `www.ge.ch` (permis de séjour), avec vérification robots.txt
  (`scripts/scraping/verifier_robots.py`) et découverte des sous-pages (`lister_souspages_chapeau.py`).
- Scraper poli (`src/scraping/scrape_pilote.py`) : délai 2 s, agent identifiable, extraction du texte
  principal par `HTMLToDocument` (trafilatura, épinglé), un JSON par page.
- Indexation (`src/indexing/indexer_pilote.py`) : découpage 200 mots / recouvrement 40, embeddings Qwen
  sans consigne, écriture dans Chroma persistant avec métadonnées par fragment.
- Pipeline de réponse (`src/repondre.py`, assemblé en `add_component` / `connect`) : requête Qwen
  avec consigne de tâche, recherche Chroma (top_k 5), `ChatPromptBuilder` (système + utilisateur),
  `OllamaChatGenerator` sur Gemma en mode direct (`think=False`).
- Configuration partagée `src/config.py` (lecture du `.env`).

**Constats (chiffres et détail dans le journal des mesures).**
- Pipeline fonctionnel de bout en bout : réponse sourcée, en **mode direct** confirmé (`think:false`
  effectif, aucune réflexion).
- Latence utilisateur (à chaud) de l'ordre de quelques secondes ; le chargement à froid des modèles est
  un coût unique (keep-alive Ollama).
- L'empreinte mémoire du couple Gemma + Qwen **confirme le budget du chapitre 4** : tenue au palier de
  confort 18 Go ; sur GARCIAD (16 Go) elle tient tout juste. Cela **verrouille le dimensionnement du VPS**
  (palier plancher 12 Go exclu, confort 18 Go requis).
- Le contraste inter-postes de l'étape 0 se confirme sur le pipeline (garciad prépare vite, décode lentement).

**Réglages posés comme révisables.** Découpage 200 mots / recouvrement 40 ; top_k 5 ; consigne provisoire. L'extraction retire les hyperliens (trafilatura garde la prose) : la réponse est juste mais
vague, sans lien ni adresse, ces éléments n'étant pas dans le corpus. À corriger à l'étape 3.

**Ce qui reste ouvert.** Consigne réelle = étape 2 ; corpus complet et ingestion reproductible (avec
préservation des liens) = étape 3 ; interface = étape 4 ; aucun réglage Advanced (reformulation,
re-classement) sans verdict de l'évaluation.

**Souveraineté.** Tout local : scraping poli de sources publiques, inférence Ollama sur `localhost`, base
Chroma embarquée. Aucun appel externe, aucune clé.

**État.** Pipeline pilote fonctionnel et mesuré sur les deux postes (DANIELGARCIA et GARCIAD).

---

## 2026-08-06 — Chapitre 9 : spécifications, périmètre du corpus, interface et frontal

**Nature.** Chapitre de spécifications et d'architecture du prototype (rédigé côté mémoire). Il pose le
cahier des charges, arrête le périmètre du corpus, et tranche deux briques de la Partie 2 laissées
ouvertes : l'interface et le serveur frontal.

**Lien avec le mémoire.** Chapitre 9. Rédigé et inséré au docx ; cinq fiches Zotero ajoutées ; Figure 9.1
(architecture cible) ; création de l'Annexe 2 du mémoire (« Mesures datées de la partie pratique », qui
compile le journal des mesures). Date de référence des sections 9.5-9.6 : 06.08.2026. Numérotation des
annexes en chiffres (l'Annexe 1, Transformer, inchangée).

**Décision, périmètre du corpus (9.2).** Corpus **cantonal genevois** :
- **ge.ch** : le catalogue cantonal (démarches en colonne vertébrale, pages pratiques, pages publiques
  des e-démarches).
- **geneve.ch/demarches** : les démarches de la Ville de Genève.
- **silgeneve.ch** (recueil législatif) : en réserve, hors corpus initial.
- Exclusions : espaces e-démarches authentifiés, annuaires privés (search.ch), PDF en réserve
  (sous-décision de l'étape 3). Questions hors périmètre : « je ne sais pas » orienté (exigence F5). Le
  manifeste des sources opérationnalisera ce périmètre à l'étape 3.

**Décision, interface (9.5).** **Streamlit** retenu. Motifs : intégration directe au pipeline Haystack
(la page appelle la fonction de réponse, rien ne s'intercale), simplicité pour un exploitant seul,
licence Apache 2.0. **Open WebUI** écarté (moteur RAG intégré qui superposerait un second pipeline,
application de plus à administrer, licence propre imposant la marque), gardé comme repli documenté.
Renoncements assumés : pas de comptes ni d'historique natifs, montée en charge modeste.

**Décision, frontal (9.6).** **Caddy** retenu. Motifs : HTTPS automatique par défaut (certificats gérés,
ZeroSSL ou Let's Encrypt), configuration courte (Caddyfile), binaire unique sans dépendance, licence
Apache 2.0. **Nginx** écarté pour ce rôle (gestion des certificats hors de son cœur, outil externe à
entretenir), gardé comme repli documenté ; sa solidité et son ubiquité restent reconnues.

**Confrontation d'une hypothèse du chapitre 4.** En 9.4, l'hypothèse d'empreinte des embeddings est
confrontée aux mesures : le poste s'avère plus lourd que prévu. Constat acté sans rétrofit de la
Partie 1 (mesures en Annexe 2 ; chiffres au journal des mesures).

**Pièces.** Cinq captures (Streamlit, Open WebUI, Caddy, Nginx) archivées **localement** dans `biblio/`
(hors dépôt) ; cinq fiches Zotero au `.ris` (versionné) ; Figure 9.1 versionnée dans
`memoire/images/figures/`.

**Ce qui reste ouvert.** Consigne de génération = étape 2 ; corpus complet et manifeste = étape 3 ;
déploiement et palier VPS = étape 5.

**Souveraineté.** Interface et frontal locaux, open source, aucun service externe.

**État.** Chapitre 9 rédigé et inséré. Interface (Streamlit) et frontal (Caddy) arrêtés. Rien n'est déployé.

---

## 2026-08-06 — Démarrage de la Partie 2 : environnement local et premières mesures

**Nature.** Jalon d'exécution, **sans décision de choix** : mise en place de l'environnement de
développement et premiers relevés. Ouvre la Partie 2 (développement).

**Lien avec le mémoire.** Partie 2 (développement), phase amont. Les mesures datées alimenteront
l'Annexe 2 ; le détail chiffré est consigné dans `docs/journal_des_mesures.md`.

**Ce qui est fait (les deux postes).**
- Ollama installé sur les deux postes (0.32.5 sur DANIELGARCIA, 0.32.6 sur GARCIAD), inférence CPU
  (iGPU non supporté sous Windows).
- Trois modèles tirés sur chaque poste, ID identiques : `gemma4:12b`, `llama3.1:8b`, `qwen3-embedding:0.6b`.
- Environnement Python 3.13 (un venv par poste) ; dépendances Haystack épinglées dans `requirements.txt`
  (`haystack-ai` 3.0.0, `ollama-haystack` 6.8.0, `chroma-haystack` 4.4.0).
- Scripts versionnés : quatre de mesure (`scripts/mesures/` : relevé du poste, génération, embeddings,
  RAM) et un de setup (`scripts/setup/pull_modeles.ps1`, pull des trois modèles, réutilisable sur le VPS).
  `bench_generation.py` décharge chaque modèle entre deux pour tenir sur une machine à faible RAM.
- Journal des mesures rempli : deux sessions datées (DANIELGARCIA 32 Go, GARCIAD 16 Go).

**Constats (chiffres et détail dans le journal des mesures).**
- Génération et embeddings mesurés sur CPU (débits, latences et chargements à froid relevés par poste).
- L'empreinte mémoire des modèles **confirme le budget du chapitre 4** : le couple Gemma + Qwen tient au
  palier de confort 18 Go ; le palier plancher 12 Go imposerait le repli Llama. Le poste embeddings
  **dépasse l'hypothèse du chapitre 4** (0,5-1,5 Go), à réviser.
- Contraste inter-postes : GARCIAD (16 Go, DDR4) est un meilleur proxy du VPS que DANIELGARCIA (32 Go,
  DDR5), avec un débit de génération plus bas (bande passante mémoire) mais un premier jeton plus rapide
  (CPU de bureau). Sur 16 Go, Gemma tient tout juste.

**Précision technique.** Le chapitre 4 décrit le mode direct de Gemma comme une réflexion qui « s'active
et se coupe par un simple jeton de contrôle », sourcé sur la page de distribution Ollama du modèle
(Ollama 2026b) : exact au niveau du gabarit. En pratique, via l'API Ollama, la réflexion est active par
défaut et se désactive par le paramètre `think:false`. Constaté sur la question type : la réflexion active
allonge fortement la latence, le mode direct la ramène à quelques secondes. Les deux énoncés sont vrais à deux niveaux
(jeton de gabarit / paramètre d'API) ; le mémoire (Partie 1) reste tel quel, la réalité d'implémentation
sera exposée en Partie 2.

**Souveraineté.** Tout local : Ollama sur `localhost`, aucun appel externe.

**Ce qui reste ouvert.** Interface, serveur web et déploiement (briques de la Partie 2 non tranchées) ;
construction du pipeline RAG (scraping, indexation, recherche, génération) à venir.

**État.** Environnement installé et mesuré. Pipeline RAG non encore construit.

---

## 2026-08-05 — Ancrage francophone et clôture de la Partie 1 (chapitre 8)

**Nature.** Chapitre de terrain, **sans candidats ni décision** : il localise les choix des chapitres 3
à 7 sur le français administratif genevois, et **referme la Partie 1 (recherche complète)**.

**Lien avec le mémoire.** Chapitre 8 (RAG en contexte francophone), dernier chapitre de la Partie 1.

**Ce que le chapitre établit.**
- **Français administratif** : l'écart de registre entre la langue des usagers et celle des pages
  officielles est le problème central que la recherche doit absorber. Particularités genevoises (sigles
  OCPM et AFC, helvétismes comme les permis B/C).
- **Traversée du pipeline** (Tableau 8.1) : embeddings (le volet français de MTEB ne mesure pas la
  récupération, vérification confiée au protocole) ; LLM (exigence nouvelle : garder les termes officiels
  dans des réponses simples, à porter par la consigne en Partie 2) ; base vectorielle (les vecteurs n'ont
  pas de langue, le terrain entre par les métadonnées) ; évaluation (RAGAS est né en anglais, comportement
  sur copies françaises non documenté, inconnue couverte par le contrôle humain du protocole).

**Implications pour la Partie 2.** Métadonnées de corpus (source, section, date de capture) ;
consigne de génération (français simple, mais conserver les noms exacts d'offices, de formulaires et de
permis) ; jeu d'évaluation (une vingtaine de questions en plusieurs registres, dont des questions
volontairement sans réponse) ; vigilance Partie 3 (comportement des consignes anglaises de RAGAS sur des
copies françaises, à confronter au contrôle humain).

**Sources.** Réutilisations : Ciancone et al. 2024, compar:IA 2026, Swiss AI
Initiative 2025 (Apertus), Es et al. 2023. Zotero : 83 fiches.

**État du document.** Environ 30 100 mots, 15 tableaux, 12 figures, 64 notes. Partie 1 complète.

**Ce qui reste ouvert à cette date.** La Partie 1 (recherche) est terminée. Restent la conclusion, puis
toute la **Partie 2 (développement)** : interface, serveur web, déploiement, puis l'évaluation empirique
en Partie 3. La phase pratique est la prochaine étape.

**État.** Rien n'est installé (ni Ollama, ni modèle, ni pipeline, ni harnais d'évaluation).

---

## 2026-08-04 — Évaluation d'un système RAG : RAGAS

**Décision.** L'évaluation du système reposera sur **RAGAS** (bibliothèque `vibrantlabsai/ragas`,
v0.4.3, Apache-2.0, environ 1 million de téléchargements par mois). Chapitre de **méthode**, non de
comparatif : il fixe comment le système sera évalué ; les résultats iront en **Partie 3**, après le
déploiement de la Partie 2.

**Lien avec le mémoire.** Chapitre 7 (évaluation d'un système RAG). Cadre acté depuis la proposition
(article Es et al. 2023). Discipline de citation : l'article pour le cadre, la documentation datée pour
l'état courant (le jeu de métriques a beaucoup grandi depuis l'article). Date de référence des faits :
04.08.2026 (captures de la documentation).

**Décisions du chapitre.**
- **Métriques (quatuor RAG)** : context precision et context recall (récupération) ; faithfulness et
  response relevancy (génération).
- **Modèle juge** : local, d'une autre famille que le rédacteur pour écarter l'auto-jugement. Ce sera
  Llama 3.1 8B (`llama3.1:8b`, le repli du chapitre 4), servi sur la machine de développement (32 Go).
  Encodeur d'évaluation local également. Aucun compte ni clé externe, rien sur le VPS.
- **Protocole (Partie 3)** : une vingtaine de questions genevoises écrites à la main (choix assumé
  contre la génération automatique de jeux de test proposée par la bibliothèque, c'est l'apport propre
  du travail), couvrant les grandes familles de démarches, en plusieurs registres, avec des questions
  volontairement sans réponse dans le corpus ; chaque question avec sa réponse de référence et sa page
  source (exigée par le context recall). Déroulé : configuration unique des chapitres 3 à 6,
  conservation question/fragments/réponse, notation métrique par métrique sur la machine de
  développement. Lecture en tableaux par métrique et famille, sans seuil absolu.
- **Garde-fous** : contrôle humain d'au moins un quart des réponses (divergence forte = juge local plus
  grand) ; classement de chaque erreur sur les sept points de défaillance de Barnett et al. 2024.

**Limites nommées.** Taille du juge (les notes valent comme instrument de comparaison entre réglages,
pas comme vérité absolue) ; faillibilité (d'où le contrôle humain d'échantillon) ; câblage (la doc
RAGAS n'illustre que des fournisseurs en nuage ; le branchement local précis, via `llm_factory` /
`embedding_factory` et la passerelle LiteLLM, sera établi et documenté en Partie 2).

**Mise en œuvre (implémentation future).** Prévoir en Partie 3 un dossier d'évaluation (jeu de
questions, réponses de référence, scripts RAGAS) exécuté sur la machine de développement ; juge
`llama3.1:8b` via Ollama ; câblage LiteLLM à valider (l'ancienne voie `LangchainLLMWrapper` n'est plus
documentée).

**Souveraineté.** Évaluation 100 % locale, sur la machine de développement : juge et encodeur locaux,
aucun service ni clé externe.

**Archives et sources.** Captures du 04.08.2026 archivées dans `biblio/RAGAS` :
`20260804_RAGAS_Metrics.pdf`, `20260804_RAGAS_Customize_Models.pdf`, `20260804_RAGAS_GitHub.pdf`.
Zotero : 3 fiches nouvelles (2 pages web docs.ragas.io, 1 logiciel `vibrantlabsai/ragas`) ; la fiche
Es et al. 2023 existait déjà (v2 arXiv du 28.04.2025 relevée, année de fiche inchangée).

**Vigilance bibliographique.** L'organisation GitHub a été renommée (`explodinggradients` devenu
`vibrantlabsai` ; les captures font foi). L'API de configuration du juge a changé (`llm_factory` et
`embedding_factory` avec LiteLLM ; l'ancienne voie `LangchainLLMWrapper` n'est plus documentée). Méthode
consolidée : bloc de vérification des appels de citation, chaque affirmation confrontée mot à mot à sa
pièce avant insertion.

**Ce qui reste ouvert à cette date.** La Partie 1 est complète (pile RAG et méthode d'évaluation).
Restent le chapitre 8 (RAG en contexte francophone) et la conclusion, puis les briques de la Partie 2
(interface, serveur web, déploiement).

**État.** Décision documentée. Rien n'est installé (ni Ollama, ni modèle, ni pipeline, ni harnais
d'évaluation).

---

## 2026-08-02 — Base vectorielle : Chroma

**Décision.** La base vectorielle retenue est **Chroma** (base embarquée, cœur en Rust, licence
Apache 2.0), via l'intégration Haystack officielle `chroma-haystack` (`ChromaDocumentStore` et son
retriever). Repli documenté : **Qdrant** (serveur dédié, Apache 2.0, Rust ; intégration officielle
cosignée deepset/Qdrant, réglages HNSW exposés), pour le scénario où il faudrait plus (charge,
filtrage, échelle) ; l'interchangeabilité des magasins Haystack rend la bascule simple.

**Lien avec le mémoire.** Chapitre 6 (choix de la base vectorielle). Décision du 02.08.2026 ; date de
référence unique des faits (captures et fiches) : 01.08.2026.

**Particularité méthodologique.** Premier chapitre de choix où la **performance ne figure pas dans les
critères**. Justification sourcée : la force brute balaie 1 million de vecteurs en 94 ms sur un fil
(Malkov et Yashunin 2016) ; la recherche non exhaustive ne devient la pierre angulaire qu'au-delà
d'environ 10 000 vecteurs, et la contrainte mémoire disparaît quand la base tient plusieurs fois en RAM
(Douze et al. 2024). Le corpus Ge-Trouve (milliers à dizaines de milliers de fragments) est sous ces
seuils : recherche exacte suffisante, index approximatif non requis. Les sept critères retenus sont
donc d'exploitation : intégration Haystack, mode de service, persistance/sauvegarde, filtrage par
métadonnées, empreinte d'exploitation, licence, maturité.

**Candidats comparés (état au 01.08.2026).**
- **Chroma** (retenu) : dépôt 2022, Apache 2.0, cœur Rust ; embarquée, mode serveur optionnel, stockage
  local intégré ; filtrage par métadonnées à la recherche.
- **Qdrant** (repli) : dépôt 2020, Apache 2.0, Rust ; serveur dédié, persistance gérée, filtrage par
  charge utile (payload) ; mode local d'essai ; `hnsw_config` (m, ef_construct) exposé dans l'intégration.
- **Faiss** (battu) : Meta, dépôt 2017, MIT, C++ ; bibliothèque sans serveur ; intégration Haystack via
  index `.faiss` + métadonnées `.json`, positionnée petits et moyens corpus ; filtrage à la charge de
  la couche du dessus. Reste au projet comme référence algorithmique (son article fonde l'argument
  d'échelle du chapitre).

**Motifs.**
1. Mode de service : base embarquée, vit dans le processus de l'application, aucun serveur séparé à
   installer, surveiller ou mettre à jour.
2. Filtrage par métadonnées natif, appliqué au moment de la recherche (source, date, section des pages
   ge.ch), sans code sur mesure.
3. Éventail de recherche documenté au-delà du vecteur dense (recherche lexicale et plein texte
   intégrées), réserve d'évolution.

Inconvénients nommés : jeunesse (dépôt créé en 2022, le plus court historique du trio). En cas de
dépassement du cadre, la réponse est la bascule vers Qdrant, pas la torsion de Chroma.

**Mise en œuvre (implémentation future).** Pipeline Haystack 2.x + `chroma-haystack` ;
`ChromaDocumentStore` en mode persistant local sur le VPS, retriever Chroma pour la recherche dense.
Schéma d'indexation avec métadonnées par fragment (url de la page, section, date de capture) pour le
filtrage. Pas d'index approximatif requis à l'échelle du corpus, aucun réglage HNSW a priori. Repli :
`QdrantDocumentStore` (mêmes interfaces Haystack) si la charge, le filtrage ou le volume l'exigeaient.
Mesures prévues en Partie 2 : consommations mémoire réelles et latences de recherche sur le serveur,
corpus réel compté.

**Souveraineté.** Base locale, embarquée dans l'application. Aucune donnée ni document ne part vers un
service externe à l'exécution.

**Archives et sources.** Relevés du 01.08.2026 archivés dans `biblio/BaseVectorielle` : 8 captures
datées (Chroma Docs et GitHub, Qdrant Documentation et GitHub, Faiss GitHub, intégrations Haystack
Chroma / Qdrant / Faiss), 2 PDF arXiv, 2 résumés de la série (Malkov et Yashunin 2016, « Le graphe à
étages » ; Douze et al. 2024, « La boîte à outils »). Zotero : 10 fiches nouvelles (2 arXiv, type GEN ;
3 dépôts, type Logiciel : Chroma, Qdrant, Meta AI ; 5 pages web : 2 documentations et 3 intégrations
deepset), consultées le 01.08.2026.

**Ce qui reste ouvert à cette date.** La pile RAG est complète (framework, LLM, embeddings et base
vectorielle tous arrêtés). Restent l'évaluation (chapitre 7, RAGAS pressenti) et les briques de la
Partie 2 (interface, serveur web, déploiement). Le code doit rester paramétrable.

**État.** Décision documentée. Rien n'est installé (ni Ollama, ni modèle, ni pipeline).

---

## 2026-07-21 — Modèle d'embeddings : Qwen3-Embedding-0.6B

**Décision.** Le modèle d'embeddings retenu est **Qwen3-Embedding-0.6B** (Alibaba, équipe Qwen,
juin 2025), servi en local via Ollama (paquet `qwen3-embedding:0.6b`, 639 Mo). Repli documenté :
**BGE-M3** (BAAI, février 2024), même mécanique de repli qu'au chapitre 4 : sur le papier, activé
seulement si les mesures de la partie pratique contredisent le choix.

**Lien avec le mémoire.** Chapitre 5 (choix des embeddings). Décision prise le 21.07.2026, sur la base
d'un relevé du classement MTEB daté du 20.07.2026 (date de référence unique du chapitre, comme le
16.07.2026 pour le chapitre 4).

**Candidats comparés (7 critères : récupération sur MTEB relevé et daté ; français ; empreinte mémoire
du paquet Ollama ; dimension des vecteurs ; longueur de contexte ; licence et accès ; maturité).**
- **Qwen3-Embedding-0.6B** (retenu) : Apache 2.0, 596 M paramètres, vecteurs 1 024 réglables (MRL),
  contexte 32 768, Ollama officiel 639 Mo ; consignes de tâche ajoutées à la requête, jamais aux documents.
- **BGE-M3** (repli) : MIT, 568 M paramètres, vecteurs 1 024 fixes, contexte 8 192, Ollama officiel
  1,2 Go ; article relu par les pairs (Findings ACL 2024), paquet le plus téléchargé (5,2 M), seul
  candidat mesuré par le volet français en 2024. Trois fonctions de recherche (dense, lexicale,
  multi-vecteurs), mais seule la dense serait servie : règle posée en 5.2, tous les scores lus sur la
  fonction dense.
- **EmbeddingGemma 300m** (écarté) : Google DeepMind, 09/2025, conditions d'utilisation Gemma avec
  acceptation préalable au téléchargement, 308 M paramètres, vecteurs 768 réglables jusqu'à 128,
  contexte 2 048 (le plus court), Ollama officiel 622 Mo, quantification préparée à l'entraînement (QAT).

**Motifs.**
1. Qualité mesurée : premier des trois candidats en récupération sur MTEB(Multilingual, v2), confirmé
   par trois sources convergentes (rapport Alibaba, Zhang et al. 2025 ; rapport Google, Vera et al.
   2025 ; relevé indépendant du 20.07.2026). Scores en récupération : 64,65 (rang général 18) contre
   62,49 (rang 29) pour EmbeddingGemma et 54,59 (rang 49) pour bge-m3.
2. Dossier : source primaire dédiée (rapport arXiv 2506.05176), licence Apache 2.0 sans barrière
   d'accès, paquet Ollama officiel léger, vecteurs à taille réglable (MRL) et consignes de tâche
   documentées par l'éditeur.
3. Marge : contexte de 32 768 jetons, le plus long du trio, qui laisse le découpage des pages libre.

**Français.** Le volet français du classement, MTEB(fra, v1), existe et contient les trois candidats,
mais aucun n'y est mesuré en récupération au 20.07.2026 (seule la classification de paires est
renseignée : 67,52 / 61,99 / 59,18, même ordre que le multilingue). La décision s'est donc prise sur
le multilingue ; la qualité en français sera vérifiée en Partie 3, sur le système complet construit
avec le seul modèle retenu, via RAGAS sur les questions genevoises. Aucun test comparatif des trois
embedders n'est prévu : un seul modèle est monté, comme pour le LLM et le framework.

**Mise en œuvre (implémentation future).** Pipeline Haystack 2.x + Ollama, dimension par défaut 1 024
(MRL disponible si l'arbitrage stockage/qualité l'exige, sous-décision à trancher en pratique).
Consignes de tâche côté requête uniquement, au format documenté par Qwen ; documents encodés sans
consigne. Contexte 32 768 jetons : le découpage des pages ge.ch n'est pas contraint. Mesures prévues
en Partie 2 avant mise en service : latence d'encodage sous CPU (embedder issu d'un LLM contre encodeur
classique) et débit d'indexation.

**Souveraineté.** Inférence 100 % locale via Ollama. Aucune donnée ni document ne part vers un service
externe à l'exécution.

**Archives et sources.** Relevé du 20.07.2026 archivé dans `biblio/Embeddings` (captures PDF et exports
CSV des vues MTEB Multilingual v2 et fra v1). Pas d'annexe dans le mémoire (convention identique au
relevé compar:IA du chapitre 4 : citation datée dans le texte, exports archivés au dépôt). Zotero :
deux fiches pour le relevé (MTEB 2026a multilingue, MTEB 2026b française, consultées le 20.07.2026),
plus 6 fiches arXiv (Muennighoff 2022, Ciancone 2024, Enevoldsen 2025, Chen 2024, Zhang 2025, Vera
2025), 3 cartes Hugging Face (BAAI 2024, Qwen Team 2025, Google 2025) et 3 fiches Ollama (bge-m3,
embeddinggemma, qwen3-embedding).

**Ce qui reste ouvert à cette date.** Base vectorielle (ChromaDB pressentie, chapitre 6). Le code doit rester
paramétrable pour échanger ce maillon sans réécriture.

**État.** Décision documentée. Rien n'est installé (ni Ollama, ni modèle, ni pipeline).

---

## 2026-07-16 — Modèle de langage (LLM) : Gemma 4 12B Instruct

**Décision.** Le modèle de langage retenu est **Gemma 4 12B Instruct**, servi en local via Ollama.
Le choix du modèle et celui du palier serveur sont **liés** : c'est une décision conjointe.

**Lien avec le mémoire.** Chapitre 4 (choix du LLM).

**Modèle et service.**
- Paquet Ollama : `gemma4:12b` (quantisation Q4_K_M, 7,6 Go, contexte 256K, licence Apache 2.0).
- Régime de service : mode direct. La réflexion (*thinking*) est **désactivée** via le jeton de contrôle
  documenté par l'éditeur.
- Repli documenté (si le palier plancher est retenu) : Llama 3.1 8B Instruct (`llama3.1:8b`, Q4_K_M, 4,9 Go).

**Serveur de production.** Infomaniak Serveur Cloud. Palier de confort : 6 CPU / 18 Go de RAM. Palier
plancher : 4 CPU / 12 Go, retenu comme scénario de repli. Rien n'est souscrit à ce stade ; souscription
prévue en août.

**Budget mémoire (hypothèses à confronter aux mesures réelles).**
- Postes fixes ≈ 6 Go : OS ~1,5 ; embeddings 0,5-1,5 ; base vectorielle <0,5 ; application ~1 ; réserve ~1,5.
- Enveloppe modèle : 5-6 Go au palier plancher, 10-11 Go au palier de confort.

**Souveraineté.** Inférence 100 % locale via Ollama (`http://localhost:11434`). Aucune donnée ni
document ne part vers un service externe à l'exécution.

**Archives et sources.** Date de référence unique du chapitre : 16.07.2026 (modèles, cartes et
classements évoluant chaque semaine, une date fixe rend la comparaison honnête). Relevé de qualité :
classement compar:IA (comparateur d'IA conversationnelles, comparia.beta.gouv.fr/ranking), consulté le
17.07.2026 ; exports archivés au dépôt, pas d'annexe dans le mémoire (citation datée dans le texte,
convention reprise au chapitre 5). Cinq candidats comparés : Llama 3.1 8B Instruct (Meta, 07/2024),
Apertus 8B Instruct (Swiss AI, 09/2025), Ministral 3 8B Instruct (Mistral AI, 12/2025), Qwen 3.5 9B
Instruct (Alibaba, 03/2026) et Gemma 4 12B Instruct (Google DeepMind, 06/2026) ; principaux écartés
pour l'enveloppe mémoire : GLM-5.2 (744 milliards de paramètres), gpt-oss, Lucie-7B. Zotero : cartes
Hugging Face et rapports techniques des candidats (consultés le 16.07.2026), pages de la bibliothèque
Ollama (`llama3.1`, `ministral-3`, `qwen3.5`, `gemma4`, consultées les 17-18.07.2026) et le relevé
compar:IA.

**Ce qui reste ouvert à cette date.** Embeddings (chapitre 5) et base vectorielle (ChromaDB pressentie, chapitre 6)
non tranchés. Le code doit rester paramétrable pour échanger ces maillons sans réécriture.

**État.** Décision documentée. Rien n'est installé (ni Ollama, ni modèle, ni pipeline).

> **Précision (06.08.2026).** Vérifié en Partie 2 : via l'API Ollama, la réflexion est active par défaut
> et se désactive par le paramètre `think:false`. La mention d'un « jeton de contrôle » (ici et au
> chapitre 4) décrit le niveau gabarit du modèle ; le commutateur côté API est `think:false`. Voir
> l'entrée du 06.08.2026.

---

## 2026-07-14 — Framework d'orchestration RAG : Haystack 2.x

**Décision.** Le framework d'orchestration du pipeline RAG est **Haystack 2.x**.

**Lien avec le mémoire.** Décision actée en **section 3.4** (choix du framework RAG).

**Motifs.**
- Pipelines explicites, composant par composant : le câblage reste visible et défendable, ce qui sert
  directement l'objectif de transparence du travail.
- Licence Apache-2.0 (gouvernance ouverte).
- Intégrations Ollama et Chroma maintenues par l'éditeur (deepset).

**Mise en œuvre.**
- Paquets : `haystack-ai` (cœur 2.x), `ollama-haystack`, `chroma-haystack`.
- Versions **épinglées** dans `requirements.txt` dès la première installation. 
- Composants de référence : `OllamaTextEmbedder` / `OllamaDocumentEmbedder`, `OllamaGenerator` ou
  `OllamaChatGenerator`, `ChromaDocumentStore`, `ChromaEmbeddingRetriever`, `PromptBuilder`.
- Pipelines assemblés explicitement (`add_component` / `connect`), sans raccourci masquant le flux.

**Souveraineté.** Inférence 100 % locale via Ollama (`http://localhost:11434`). Aucune donnée ni
document ne part vers un service externe à l'exécution. Toute bibliothèque qui exigerait une clé d'API
externe sera exclue.

**Ce qui reste ouvert à cette date.**
- **LLM** : chapitre 4 en cours. Mistral 7B via Ollama sert de modèle de travail provisoire pour le
  développement, ce n'est pas le choix final.
- **Embeddings** : chapitre 5, non traité.
- **Base vectorielle** : ChromaDB pressentie, décision au chapitre 6.

Le code doit rester paramétrable pour échanger ces maillons sans réécriture.

**Environnement.** Développement local Windows (Ryzen 7 7840HS, 32 Go de RAM, CPU uniquement, pas de
GPU supporté par Ollama ici). Cible de production : VPS Infomaniak Ubuntu, environ 12 Go de RAM.
Viser la sobriété à chaque choix.

> **Mise à jour (supersession partielle).** Les maillons listés ci-dessus comme ouverts ont depuis été
> tranchés : LLM le 16.07.2026 (Gemma 4 12B Instruct), embeddings le 21.07.2026 (Qwen3-Embedding-0.6B).
> Le palier serveur retenu est 6 CPU / 18 Go de RAM (confort), non les ~12 Go évoqués ici. Voir les
> entrées du 16.07 et du 21.07 ci-dessus.

> **Précision (06.08.2026).** À l'installation, `requirements.txt` épingle `haystack-ai` **3.0.0**, la
> version courante. Le chapitre 3 avait tranché sur la ligne 2.x (v2.31 alors, transition 3.0 annoncée) ;
> la 3.0 conserve l'architecture à pipelines explicites (composants, `add_component` / `connect`),
> vérifiée par l'import des composants de référence. Aucune décision changée, simple montée de version
> majeure prise à l'installation.
