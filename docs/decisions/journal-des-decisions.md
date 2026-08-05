# Journal des décisions techniques — Ge-Trouve

Ce fichier consigne les décisions techniques du projet, au fur et à mesure qu'elles sont arrêtées.
Chaque entrée précise sa date, ce qu'elle tranche, ses motifs, ce qui reste ouvert, et son lien avec
le mémoire. Une décision reste valable jusqu'à révision explicite, consignée à son tour ici.

Les décisions les plus récentes sont ajoutées en haut.

---

## 2026-08-05 — Ancrage francophone et clôture de la Partie 1 (chapitre 8)

**Nature.** Chapitre de terrain, **sans candidats ni décision** : il localise les choix des chapitres 3
à 7 sur le français administratif genevois, et **referme la Partie 1 (recherche complète)**.

**Lien avec le mémoire.** Chapitre 8 (RAG en contexte francophone), dernier chapitre de la Partie 1.

**Ce que le chapitre établit.**
- **Français administratif** : l'écart de registre entre la langue des usagers et celle des pages
  officielles est le problème central que la recherche doit absorber. Particularités genevoises (sigles
  OCPM et AFC, helvétismes comme les permis B/C, mélange des niveaux fédéral et cantonal dans le corpus,
  d'où l'importance du filtrage par métadonnées du chapitre 6).
- **Traversée du pipeline** (Tableau 8.1) : embeddings (le volet français de MTEB ne mesure pas la
  récupération, vérification confiée au protocole) ; LLM (exigence nouvelle : garder les termes officiels
  dans des réponses simples, à porter par la consigne en Partie 2) ; base vectorielle (les vecteurs n'ont
  pas de langue, le terrain entre par les métadonnées) ; évaluation (RAGAS est né en anglais, comportement
  sur copies françaises non documenté, inconnue couverte par le contrôle humain du protocole).

**Implications pour la Partie 2.** Métadonnées de corpus (source, section, niveau fédéral/cantonal) ;
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
externe sera exclut.

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
