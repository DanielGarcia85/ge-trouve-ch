# Ge-Trouve

> **Assistant conversationnel RAG en français pour l'accessibilité aux démarches administratives du canton de Genève**

[![Statut](https://img.shields.io/badge/statut-en%20d%C3%A9veloppement-orange)]()
[![Licence](https://img.shields.io/badge/licence-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-3.13-brightgreen)]()

---

## À propos

**Ge-Trouve** est un projet de Travail de Bachelor mené à la HEG-Genève (filière Informatique de gestion, module 66-62). Il consiste à concevoir, développer et évaluer un assistant conversationnel utilisant la technique du **Retrieval-Augmented Generation (RAG)** pour rendre les démarches administratives du canton de Genève plus accessibles aux citoyens.

L'idée centrale : un citoyen pose une question en langage naturel, par exemple *« Où déposer ma demande de permis de séjour ? »*, et obtient une réponse claire, fiable et sourcée, construite à partir des documents officiels publiés par l'État de Genève.

Le service sera accessible à terme sur le domaine [**ge-trouve.ch**](https://ge-trouve.ch).

### Titre du travail

> *ge-trouve.ch : Conception, développement et évaluation d'un assistant conversationnel RAG en français pour l'accessibilité aux démarches administratives du canton de Genève*

### Question de recherche

> *Dans quelle mesure un système RAG appliqué à des documents administratifs en français produit-il des réponses fiables et pertinentes pour des utilisateurs non-experts ?*

### Apport original

Ce travail propose une évaluation concrète du RAG sur un cas réel : des documents administratifs en français, dans un contexte local genevois. Cette contribution n'existe pas encore dans la littérature scientifique, qui s'est jusqu'ici concentrée sur l'anglais et les corpus généralistes.

Le positionnement est renforcé par le contexte institutionnel suisse :

- la Confédération **structure activement l'usage de l'IA** dans son administration : [stratégie, lignes directrices sur l'IA générative et Réseau de compétences (CNAI)](https://www.bk.admin.ch/fr/intelligence-artificielle), avec une banque de données des projets ;
- **plusieurs chatbots fédéraux sont expérimentés ou déployés**, dont un projet du **SECO explicitement fondé sur le RAG** ; plus de soixante projets IA étaient recensés à fin mai 2024 ([Chavanne, *ICTjournal*, 2024](https://www.ictjournal.ch/articles/2024-10-17/cinq-chatbots-de-ladministration-federale)) ;
- le canton de Genève [**encadre l'usage de l'IA générative** pour ses collaborateurs](https://www.ge.ch/document/intelligence-artificielle-generative-dans-fonction-publique-etat-geneve-pose-cadre) depuis novembre 2024 ;
- l'État de Genève a publié sa [**stratégie de souveraineté numérique**](https://www.ge.ch/document/geneve-developpe-sa-strategie-matiere-souverainete-numerique) le 7 juillet 2026.

Pourtant, **aucun assistant conversationnel destiné aux citoyens genevois n'a pu être identifié à ce jour**. Ge-Trouve vise précisément à combler ce vide.

---

## Souveraineté des données

Le système est conçu pour fonctionner **entièrement en local**, sur un VPS hébergé en Suisse.

En production et pendant l'inférence :

- aucune donnée utilisateur ni document ne sort du serveur ;
- aucun appel n'est fait à une API externe (OpenAI, Anthropic, etc.) ;
- toute la chaîne (interface, framework RAG, embeddings, base vectorielle, LLM) tourne sur la machine.

Cette exigence est centrale pour un service public, et se trouve alignée sur la stratégie cantonale de souveraineté numérique.

---

## Architecture cible

```
            UTILISATEUR (navigateur)
                     │ HTTPS
┌────────────────────▼────────────────────────────────────┐
│                VPS suisse (Ubuntu Server)                │
│                                                          │
│   Reverse proxy (ex. Nginx / Caddy)                      │
│              ↓                                           │
│   Interface web  ──►  Framework RAG (orchestration)      │
│                          │                │              │
│                 1. recherche          2. génération      │
│                          ▼                ▼              │
│                 ┌─────────────────┐  ┌──────────────┐    │
│                 │ Embeddings +    │  │  LLM local   │    │
│                 │ base vectorielle│  │ (via Ollama) │    │
│                 └────────▲────────┘  └──────────────┘    │
│                          │                               │
│   INDEXATION (hors ligne, en amont) :                    │
│   sources officielles → scraping → chunking →            │
│   embeddings → base vectorielle                          │
└──────────────────────────────────────────────────────────┘
```

### Le pipeline RAG

1. **Indexation** : aspiration des sources officielles, découpage en fragments (*chunking*), calcul des *embeddings*, stockage dans la base vectorielle.
2. **Recherche** : la question de l'utilisateur est vectorisée, puis les fragments les plus proches sont récupérés.
3. **Génération** : un prompt combinant la consigne, les fragments retenus et la question est soumis au LLM local, qui produit une réponse sourcée.

**Positionnement retenu** : un *Naive RAG* solide comme socle. Les optimisations *Advanced* (réécriture de requête, *re-ranking*) ne seront introduites que si l'évaluation le justifie. Le *Modular RAG* reste hors périmètre et sera présenté comme piste d'évolution.

---

## Stack technique

> Les choix technologiques sont **étudiés, comparés et tranchés chapitre par chapitre** dans le mémoire. Les composants encore ouverts restent des **pistes envisagées**, données à titre indicatif ; ceux qui sont arrêtés sont signalés comme tels.

| Composant | Choix / pistes envisagées | Tranché au |
|---|---|---|
| **Langage** | Python 3.13 | *(socle du projet)* |
| **Framework RAG** | **Haystack 2.x** (arrêté) | Chapitre 3 |
| **LLM** | **Gemma 4 12B Instruct** (arrêté), servi en local via Ollama | Chapitre 4 |
| **Embeddings** | modèles multilingues (ex. BGE-M3, etc.) | Chapitre 5 |
| **Base vectorielle** | ChromaDB, Qdrant, FAISS, etc. | Chapitre 6 |
| **Évaluation** | RAGAS, etc. | Chapitre 7 |
| **Interface** | Streamlit, Open WebUI, etc. | Partie 2 |
| **Serveur web** | Nginx, Caddy, etc. | Partie 2 |
| **Déploiement** | VPS Linux suisse (ex. Infomaniak), Ubuntu Server LTS | Partie 2 |

---

## Sources de données

Les documents indexés proviennent **exclusivement de sources publiques officielles**. Le cœur du corpus :

- [`ge.ch`](https://www.ge.ch) : portail officiel de l'État de Genève (démarches, offices, prestations) ;
- [`silgeneve.ch`](https://silgeneve.ch) : législation genevoise, les textes que les démarches citent ;
- [`ch.ch`](https://www.ch.ch) : portail officiel Confédération-cantons-communes dédié aux démarches ;
- [`sem.admin.ch`](https://www.sem.admin.ch) : Secrétariat d'État aux migrations (les permis de séjour relèvent d'une compétence partagée fédérale/cantonale) ;
- [`geneve.ch`](https://www.geneve.ch) et sites communaux : de nombreuses démarches passent par la commune de domicile.

D'autres sources institutionnelles pourront être évaluées, et le périmètre étendu si le besoin s'en fait sentir (Feuille d'avis officielle, assurances sociales, aide sociale, etc.).

Le périmètre exact du corpus sera arrêté en **Partie 2**, via un **manifeste des sources** (URL et date de capture). L'aspiration des contenus est réalisée par un script Python dédié, qui **respecte les conditions d'utilisation de chaque site**.

Le corpus lui-même (`data/`) **n'est pas versionné** : Git n'est pas adapté aux données volumineuses et évolutives. La reproductibilité est assurée en versionnant le **pipeline de scraping** et le manifeste des sources, plutôt que les fichiers bruts.

---

## Structure du dépôt

```
ge-trouve-ch/
├── README.md                       ← Présentation du projet (ce fichier)
├── memoire/                        ← Mémoire de Bachelor
│   ├── TB_Ge-Trouve_DanielGarcia.docx
│   ├── bibliographie/              ← Export Zotero (.ris)
│   └── images/
│       ├── figures/                ← Figures du corps du mémoire (SVG)
│       ├── annexes/                ← Figures d'annexe (SVG)
│       └── backups/                ← Figures de secours pour la soutenance
├── docs/                           ← Documentation technique
│   ├── architecture.md
│   ├── decisions/                  ← Choix techniques argumentés
│   ├── notes_rdv/                  ← Notes des rendez-vous avec le directeur
│   └── heg/                        ← Directives officielles HEG
├── src/                            ← Code source Python
│   ├── scraping/                   ← Aspiration des sources officielles
│   ├── indexing/                   ← Chunking et embeddings
│   ├── retrieval/                  ← Recherche dans la base vectorielle
│   ├── generation/                 ← Appel au LLM local
│   └── app/                        ← Interface web
├── tests/                          ← Tests sur un jeu de questions types
├── evaluation/                     ← Scripts et résultats RAGAS
├── data/                           ← Documents scrapés (non versionné)
├── .env.example                    ← Modèle de configuration
├── requirements.txt                ← Dépendances Python
└── .gitignore
```

---

## Plan du mémoire

Le travail s'articule en trois parties : la **recherche** (revue de littérature et arbitrage des choix techniques), le **développement** (spécifications, pipeline RAG, interface, déploiement) et l'**évaluation** (tests RAGAS, analyse des erreurs, conclusions).

| Chapitre | Sujet |
|---|---|
| **2** | Comprendre le RAG (du Transformer aux limites des LLM, origine, pipeline, Naive/Advanced/Modular) |
| **3** | Choix du framework RAG |
| **4** | Choix du LLM |
| **5** | Choix des embeddings |
| **6** | Choix de la base vectorielle |
| **7** | Évaluation d'un système RAG |
| **8** | Le RAG en contexte francophone |

---

## Bibliographie

La revue de littérature s'appuie sur un ensemble de sources gérées sous Zotero et exportées dans `memoire/bibliographie/` (fichier `.ris`), qui **fait foi** et **s'enrichit au fil du travail**. Les prépublications arXiv sont citées à l'année de leur **première version** (v1), avec leur DOI.

Parmi les travaux fondateurs mobilisés : [**Vaswani et al. (2017)**](https://arxiv.org/abs/1706.03762) pour le Transformer, [**Lewis et al. (2020)**](https://arxiv.org/abs/2005.11401) pour l'architecture RAG, [**Gao et al. (2023)**](https://arxiv.org/abs/2312.10997) pour la synthèse du domaine.

**Articles complémentaires :**

- [**Papadopoulos et al. (2025)**](https://www.frontiersin.org/journals/political-science/articles/10.3389/fpos.2025.1601440/full), *Frontiers in Political Science* : le RAG apparaît comme l'architecture la plus équilibrée pour les chatbots de service public.
- [**Chavanne (2024)**](https://www.ictjournal.ch/articles/2024-10-17/cinq-chatbots-de-ladministration-federale), *ICTjournal* : panorama de cinq chatbots fédéraux, dont un projet du SECO fondé sur le RAG.

**Sources institutionnelles :**

- [**État de Genève (21.11.2024)**](https://www.ge.ch/document/intelligence-artificielle-generative-dans-fonction-publique-etat-geneve-pose-cadre) : l'intelligence artificielle générative dans la fonction publique, l'État de Genève pose un cadre.
- [**État de Genève (07.07.2026)**](https://www.ge.ch/document/geneve-developpe-sa-strategie-matiere-souverainete-numerique) : Genève développe sa stratégie en matière de souveraineté numérique.
- [**Chancellerie fédérale**](https://www.bk.admin.ch/fr/intelligence-artificielle) : intelligence artificielle dans l'administration fédérale (stratégie, lignes directrices, Réseau de compétences CNAI).

---

## Auteur

**Daniel Garcia**
Étudiant en Informatique de gestion, HEG-Genève
Travail de Bachelor 2026

**Directeur de mémoire :** Frédéric Mencier

---

## Déclaration concernant l'usage de l'IA

Conformément aux directives de la HEG, l'usage d'outils d'intelligence artificielle est déclaré explicitement.

**Claude (Anthropic)** a été utilisé comme assistant à la rédaction et au développement : formulation de phrases, correction grammaticale, reformulation, mise en forme, aide au code. **Le contenu, les idées et les choix intellectuels restent entièrement ceux de l'auteur.**

Conformément à la contrainte de souveraineté du projet, l'application en production ne fait appel à **aucun service d'IA externe** (API tierces telles que Claude ou ChatGPT) : elle repose sur un **modèle de langage open source exécuté localement** sur le serveur. Claude n'intervient que comme outil de développement et de rédaction du mémoire, jamais comme composant de l'application livrée.

---

## Licence

Ce projet est publié sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

Les documents administratifs indexés restent la propriété de leurs ayants droit respectifs (État de Genève et institutions associées). Seul le code de l'application est couvert par la licence MIT.

---

## Liens utiles

- **Site du projet** : [ge-trouve.ch](https://ge-trouve.ch) *(en cours de déploiement)*
- **HEG-Genève** : [hesge.ch/heg](https://www.hesge.ch/heg)
- **État de Genève** : [ge.ch](https://www.ge.ch)
