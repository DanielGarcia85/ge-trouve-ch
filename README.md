# ge-trouve.ch

> **Assistant conversationnel RAG en français pour l'accessibilité aux démarches administratives du canton de Genève**

[![Statut](https://img.shields.io/badge/statut-en%20d%C3%A9veloppement-orange)]()
[![Licence](https://img.shields.io/badge/licence-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-3.13-brightgreen)]()

---

## 📖 À propos

**ge-trouve.ch** est un projet de Travail de Bachelor mené à la HEG-Genève (filière Informatique de gestion). Il consiste à concevoir, développer et évaluer un assistant conversationnel utilisant la technique du **Retrieval-Augmented Generation (RAG)** pour rendre les démarches administratives du canton de Genève plus accessibles aux citoyens.

L'idée centrale : un citoyen peut poser une question en langage naturel (« Combien coûte un passeport ? », « Comment déclarer un déménagement ? ») et obtenir une réponse claire, fiable et sourcée, construite à partir des documents officiels publiés par l'État de Genève.

### Question de recherche

> *Dans quelle mesure un système RAG appliqué à des documents administratifs en français produit-il des réponses fiables et pertinentes pour des utilisateurs non-experts ?*

### Apport original

Ce travail propose une évaluation concrète du RAG sur un cas réel : des documents administratifs en français, dans un contexte local genevois. Cette contribution n'existe pas encore dans la littérature scientifique, qui s'est jusqu'ici concentrée sur l'anglais et les corpus généralistes.

---

## 🏗️ Architecture cible

Le système est conçu pour fonctionner **entièrement en local**, sur un VPS hébergé en Suisse, afin de garantir la souveraineté des données — exigence centrale pour un service public.

```
┌─────────────────────────────────────────────────────────┐
│                   VPS Infomaniak (Suisse)               │
│                                                         │
│   Interface web (Streamlit / Flask)                     │
│              ↓                                          │
│   Framework RAG (LangChain ou LlamaIndex)               │
│              ↓                                          │
│   ┌─────────────┬─────────────┬────────────────┐        │
│   │ Embeddings  │  ChromaDB   │  Mistral 7B    │        │
│   │  (local)    │ (vectoriel) │  via Ollama    │        │
│   └─────────────┴─────────────┴────────────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

> ⚠️ Les technologies nommées dans ce schéma (Streamlit, LangChain, ChromaDB, Mistral, etc.) ne sont que des **exemples envisagés**, pas des choix arrêtés : ils seront étudiés et tranchés en **Partie 1** du travail.

Aucune donnée ne sort du serveur suisse, aucun appel externe pendant l'inférence.

---

## 🔧 Stack technique

> ⚠️ **Aucun choix technologique n'est arrêté à ce stade.** Les éléments ci-dessous sont des **pistes envisagées**, données à titre indicatif. Elles seront étudiées, comparées et tranchées en **Partie 1** du travail (revue de littérature).

| Composant | Pistes envisagées | À étudier en |
|---|---|---|
| **Langage** | Python 3.13 | (socle du projet) |
| **Framework RAG** | LangChain, LlamaIndex, OpenRAG, Haystack, etc. | Chapitre 2 |
| **LLM** | modèles open-source servis en local (ex. Mistral via Ollama, Llama, etc.) | Chapitre 3 |
| **Embeddings** | modèles multilingues (ex. BGE-M3, etc.) | Chapitre 4 |
| **Base vectorielle** | ChromaDB, Qdrant, FAISS, pgvector, etc. | Chapitre 5 |
| **Évaluation** | RAGAS, etc. | Chapitre 6 |
| **Interface** | Streamlit, Flask, etc. | Partie 2 |
| **Déploiement** | VPS Linux suisse (ex. Infomaniak) — souveraineté des données | Partie 2 |

---

## 📚 Sources de données

Les documents indexés proviennent exclusivement de sources publiques officielles :

- `ge.ch` — Portail principal de l'État de Genève
- `etat.ge.ch` — Services administratifs
- `sig-ge.ch` — Services industriels
- `tpg.ch` — Transports publics genevois
- Autres sources institutionnelles selon les besoins

L'aspiration des contenus est réalisée par un script Python dédié, qui respecte les conditions d'utilisation de chaque site.

---

## 📂 Structure du dépôt

```
ge-trouve-ch/
├── README.md                  ← Présentation du projet (ce fichier)
├── memoire/                   ← Mémoire de Bachelor et bibliographie
│   ├── Memoire_GeTrouve.docx
│   ├── images/
│   └── biblio/                ← Articles scientifiques de référence
├── docs/                      ← Documentation technique
│   ├── architecture.md
│   ├── notes_rdv/             ← Notes des rendez-vous avec le directeur de mémoire
│   └── decisions/             ← Choix techniques argumentés
├── src/                       ← Code source Python
│   ├── scraping/              ← Aspiration des sources officielles
│   ├── indexing/              ← Pipeline d'indexation (chunking, embeddings)
│   ├── retrieval/             ← Recherche dans la base vectorielle
│   ├── generation/            ← Appel au LLM via Ollama
│   └── app/                   ← Interface web
├── tests/                     ← Tests unitaires (questions types)
├── evaluation/                ← Scripts et résultats d'évaluation RAGAS
├── data/                      ← Documents scrapés (non versionné)
├── requirements.txt           ← Dépendances Python
└── .gitignore
```

---

## 📅 Calendrier du projet

Le projet est mené sur **8 semaines à plein temps** (~360 heures, 12 ECTS).

| Phase | Contenu | Pondération |
|---|---|---|
| **Partie 1 — Recherche et littérature** | Revue de littérature, comparaison des choix techniques | 30% |
| **Partie 2 — Développement** | Spécifications, pipeline RAG, interface, déploiement | 50% |
| **Partie 3 — Évaluation** | Tests RAGAS, analyse des erreurs, conclusions | 20% |

---

## 📖 Bibliographie principale

La revue de littérature s'appuie sur sept articles scientifiques majeurs :

1. **Guu et al. (2020)** — *REALM: Retrieval-Augmented Language Model Pre-Training*
2. **Lewis et al. (2020)** — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*
3. **Borgeaud et al. (2021)** — *Improving Language Models by Retrieving from Trillions of Tokens (RETRO)*
4. **Ji et al. (2022-2024)** — *Survey of Hallucination in Natural Language Generation*
5. **Gao et al. (2023-2024)** — *Retrieval-Augmented Generation for Large Language Models: A Survey*
6. **Es et al. (2024)** — *RAGAS: Automated Evaluation of Retrieval Augmented Generation*
7. **Sharma (2025)** — *Retrieval-Augmented Generation: A Comprehensive Survey of Architectures, Enhancements, and Robustness Frontiers*

L'ensemble des résumés détaillés est disponible dans le dossier `memoire/biblio/`.

---

## 👤 Auteur

**Daniel Garcia**
Étudiant en Informatique de gestion — HEG-Genève
Travail de Bachelor 2026

**Directeur de mémoire :** Frédéric Mencier

---

## 🤖 Déclaration concernant l'usage de l'IA

Conformément aux directives de la HEG, l'usage d'outils d'intelligence artificielle est déclaré explicitement.

**Claude (Anthropic, Claude Opus 4.7, 2026)** a été utilisé comme assistant à la rédaction : formulation de phrases, correction grammaticale, reformulation et mise en forme du texte. Le contenu, les idées et les choix intellectuels restent entièrement ceux de l'auteur.

---

## 📄 Licence

Ce projet est publié sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

Les documents administratifs indexés restent la propriété de leurs ayants droit respectifs (État de Genève et institutions associées). Seul le code de l'application est couvert par la licence MIT.

---

## 🔗 Liens utiles

- **Domaine du projet** : [ge-trouve.ch](https://ge-trouve.ch) *(en cours de déploiement)*
- **HEG-Genève** : [hesge.ch/heg](https://www.hesge.ch/heg)
- **État de Genève** : [ge.ch](https://www.ge.ch)
