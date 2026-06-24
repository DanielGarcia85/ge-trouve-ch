# CLAUDE.md — Contexte projet pour Claude Code

> Ce fichier est lu automatiquement par Claude Code au début de chaque session.
> Il décrit le projet, la stack, les conventions et les règles de travail à respecter.

## Projet

**ge-trouve.ch** — Assistant conversationnel RAG en français pour l'accessibilité aux
démarches administratives du canton de Genève.

Travail de Bachelor (HEG-Genève, module 66-62, filière Informatique de gestion).
Auteur : Daniel Garcia. Directeur : Frédéric Mencier.

**Question de recherche :** Dans quelle mesure un système RAG appliqué à des documents
administratifs en français du canton de Genève produit-il des réponses fiables et pertinentes pour des
utilisateurs non-experts ?

## Stack technique

- **Langage :** Python
- **Framework RAG :** LangChain / LlamaIndex / OpenRAG (choix à justifier — chapitre 2)
- **LLM :** Mistral 7B servi via Ollama, en local (choix à justifier — chapitre 3)
- **Embeddings :** modèle multilingue à choisir (chapitre 4)
- **Base vectorielle :** ChromaDB envisagée (à confirmer — chapitre 5)
- **Évaluation :** RAGAS
- **Interface :** Streamlit envisagé
- **Déploiement :** local pendant le développement, puis VPS Linux Infomaniak (souveraineté suisse)

## Contrainte d'architecture (IMPORTANT)

Architecture cible **tout-en-local sur le VPS suisse** : interface web + framework RAG +
embeddings + base vectorielle + Mistral via Ollama. **Aucun appel à une API externe pendant
l'inférence**, pour respecter la souveraineté des données d'un service public.

Conséquence : ne jamais proposer de solution qui enverrait des données utilisateur ou des
documents administratifs vers un service tiers (OpenAI, Anthropic, etc.) en production.
Claude est un outil de développement, pas un composant du produit final.

## Structure du repo

```
ge-trouve-ch/
├── data/        # données scrapées depuis ge.ch, etat.ge.ch, etc. (NON versionné)
├── docs/        # documentation technique
├── memoire/     # rédaction du mémoire
├── src/         # code source du pipeline RAG
├── tests/       # tests unitaires (questions types, anti-hallucination)
├── .gitignore
├── README.md
└── requirements.txt
```

## Sources de données

Sources publiques officielles uniquement : ge.ch, etat.ge.ch, sig-ge.ch, tpg.ch, AFC, etc.

## Conventions de code

- Code commenté en français.
- Respecter PEP 8.
- Dépendances ajoutées dans `requirements.txt` (avec version épinglée).
- Variables sensibles dans un fichier `.env` (jamais commité — voir `.gitignore`).
- Messages de commit clairs et en français.
- **Aucune signature ni trace de l'IA dans les commits (RÈGLE ABSOLUE).** Ne jamais
  ajouter de ligne `Co-Authored-By: Claude ...`, ni mention « Generated with »,
  ni aucune marque indiquant qu'un assistant a participé. Le dépôt ne doit laisser
  paraître nulle part que Daniel a été aidé : l'auteur unique des commits est Daniel.
  Cela vaut pour les messages de commit, les PR et tout fichier versionné.
- **Toutes les commandes git sont exécutées manuellement par Daniel (RÈGLE ABSOLUE).**
  Claude ne lance JAMAIS lui-même une commande git (pas de `git add`, `commit`,
  `push`, `reset`, etc.). À chaque fois qu'une opération git est nécessaire, Claude
  écrit les commandes à exécuter dans la discussion ; Daniel les lance lui-même dans
  son terminal, colle/montre le résultat, et on valide ensemble avant de passer à la
  suite. C'est Daniel qui veut, qui doit et qui fait les commandes git — pour garder
  la maîtrise totale du dépôt et pouvoir tout défendre en soutenance.
- **Fichiers de configuration remplis au fur et à mesure, jamais à l'avance.**
  Le `.gitignore`, `requirements.txt` et les autres fichiers de config ne doivent
  contenir que ce qui existe réellement dans le projet à l'instant T. On ajoute une
  entrée quand le fichier/dossier/dépendance correspondant apparaît concrètement —
  pas avant. Objectif : Daniel garde la maîtrise et la compréhension complète de
  chaque ligne, et peut la défendre en soutenance. Ne jamais pré-remplir « pour
  plus tard » des outils ou chemins qu'on n'utilise pas encore.

## Règles de travail (à respecter impérativement)

1. **Étape par étape :** procéder une étape à la fois et attendre la validation explicite
   de Daniel avant de passer à la suivante. Ne pas enchaîner plusieurs modifications d'un coup.
2. **Expliquer avant de faire :** pour chaque tâche non triviale, expliquer ce qui va être
   fait et pourquoi, avant de modifier le code.
3. **Daniel doit comprendre et pouvoir défendre chaque ligne** en soutenance. Ne rien
   produire d'opaque ou de « magique ».
4. **Rédaction du mémoire :** français académique mais naturel et humain — pas pompeux,
   pas généré par IA. Varier les structures de phrases.
5. **Sources scientifiques :** toute affirmation de la revue de littérature doit être
   appuyée par une source sérieuse (arXiv, NeurIPS, ACL, EACL, rapports institutionnels).
6. **Réalisme :** le projet tient en 8 semaines à plein temps, ce n'est pas une thèse de
   doctorat. Garder la portée focalisée.
7. **Répondre en français.**

## Déclaration IA (rappel)

L'usage de l'IA est déclaré dans le mémoire : Claude (Anthropic) est utilisé comme assistant
à la rédaction et au développement. Le contenu, les idées et les choix intellectuels restent
ceux de l'auteur.
