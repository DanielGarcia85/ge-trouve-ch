# src/app/vues/a_propos.py

"""
Page « À propos » — le projet, son cadre et sa construction
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Présenter Ge-Trouve à un visiteur curieux ou à un recruteur : ce que fait l'outil, le cadre
du Travail de Bachelor, la façon dont le système est construit et évalué, les technologies
employées (versions lues dans `requirements.txt` et `deploy/docker-compose.yml`), les
limites connues et l'usage de l'IA pendant la fabrication. Page statique : aucun appel au
pipeline, aucune donnée de l'usager.
"""

import streamlit as st

import commun

# Technologies, par groupe : (nom et version, rôle dans le projet).
TECHNOLOGIES = {
    "Modèles": [
        ("Gemma 4 12B Instruct", "rédige les réponses, en mode direct (réflexion désactivée)"),
        ("Qwen3-Embedding-0.6B", "transforme fragments et questions en vecteurs de 1 024 dimensions"),
        ("Ollama 0.32.6", "sert les deux modèles sur le serveur, gardés en mémoire"),
    ],
    "Recherche et génération": [
        ("Haystack 3.0.0", "assemble le pipeline composant par composant, sans raccourci"),
        ("ollama-haystack 6.8.0 et chroma-haystack 4.4.0", "relient Haystack à Ollama et à Chroma"),
        ("Chroma", "base vectorielle embarquée, persistée sur le disque du serveur"),
        ("Trafilatura 2.2.0", "extrait le texte des pages officielles en gardant leurs liens"),
    ],
    "Interface": [
        ("Python 3.13 et Streamlit 1.62.0", "cette page, la conversation et l'affichage mot à mot"),
    ],
    "Livraison": [
        ("Docker Compose", "quatre conteneurs : modèles, application, proxy, téléchargement des modèles"),
        ("Caddy 2", "seul point exposé à Internet, HTTPS automatique (Let's Encrypt)"),
        ("GitHub Actions", "redéploiement automatique par un runner installé sur le serveur lui-même"),
        ("Serveur Infomaniak", "en Suisse : 6 vCPU, 18 Go de mémoire, Ubuntu 24.04, sans carte graphique"),
    ],
    "Évaluation (poste de développement)": [
        ("RAGAS 0.4.3", "quatre métriques de qualité, calculées en local"),
        ("Llama 3.1 8B", "modèle juge, d'une autre famille que le rédacteur"),
    ],
}


SECTIONS = (
    ("Le cadre", "le-cadre"),
    ("Ce que fait l'outil", "ce-que-fait-l-outil"),
    ("Comment il est construit", "construction"),
    ("Technologies", "technologies"),
    ("Limites connues", "limites"),
    ("Usage de l'IA", "usage-ia"),
)
TITRES = dict(SECTIONS)

commun.afficher_sommaire(SECTIONS)

st.title("À propos du projet")

st.markdown(
    "Ge-Trouve répond en français simple aux questions sur les démarches administratives du "
    "canton de Genève. Il retrouve les passages utiles dans les pages officielles de ge.ch et "
    "geneve.ch, rédige une réponse et cite ses sources, pour que chacun puisse vérifier.\n\n"
    "Tout s'exécute sur un serveur en Suisse, avec des modèles de langage open source : aucune "
    "question ne part vers un service d'intelligence artificielle externe."
)
st.info(
    "Ge-Trouve est un prototype, pas un service officiel de l'État de Genève. Les réponses "
    "peuvent contenir des erreurs : vérifiez toujours l'information à la source avant d'agir."
)

st.header("Le cadre", anchor=TITRES["Le cadre"])
st.markdown(
    "J'ai réalisé Ge-Trouve seul, pour mon Travail de Bachelor en Informatique de gestion à la "
    "Haute école de gestion de Genève (HEG), sous la direction de Frédéric Mencier. Le travail a "
    "été remis le 31 août 2026 et soutenu le 14 septembre 2026. Le mémoire couvre toute la "
    "démarche : la littérature sur le RAG, le choix de chaque technologie, la construction du "
    "système et son évaluation.\n\n"
    f"Le code, les journaux de décisions et de mesures et le [mémoire]({commun.MEMOIRE}) sont publics, "
    f"sur le [dépôt GitHub]({commun.DEPOT}).\n\n"
    "Le travail a été évalué à 5,6/6 pour le mémoire et 5,8/6 pour la soutenance."
)

st.header("Ce que fait l'outil", anchor=TITRES["Ce que fait l'outil"])
st.markdown(
    "- Il accepte les questions en français courant, tous registres confondus.\n"
    "- Il répond uniquement à partir des pages officielles indexées, avec des liens cliquables "
    "vers le guichet en ligne ou le formulaire utile.\n"
    "- Il affiche dans la barre latérale les pages d'où vient chaque réponse.\n"
    "- Il est conçu pour dire quand la question sort de ce qu'il connaît et orienter vers le bon "
    "interlocuteur.\n"
    "- Il écrit la réponse mot à mot, au fil de la génération.\n"
    "- Il ne demande aucun compte et ne garde aucun historique."
)

st.header("Comment il est construit", anchor=TITRES["Comment il est construit"])
st.markdown(
    "**L'indexation, en amont.** J'ai listé 4 322 pages officielles dans un manifeste, puis je "
    "les ai aspirées en respectant les règles des deux sites (robots.txt, deux secondes entre "
    "deux requêtes). Le texte est découpé en 9 651 fragments de 200 mots, chacun avec son "
    "adresse et sa date de capture, puis encodé et rangé dans une base Chroma d'environ 191 Mo.\n\n"
    "**À chaque question.** La question est encodée par le même modèle, la base renvoie les cinq "
    "fragments les plus proches, et Gemma 4 rédige la réponse à partir de ces seuls extraits.\n\n"
    "**En production.** Quatre conteneurs Docker tournent sur un serveur Infomaniak en Suisse. "
    "Un proxy Caddy, seul exposé à Internet, gère le HTTPS. Chaque modification du code poussée "
    "sur la branche principale est redéployée automatiquement par un runner installé sur le "
    "serveur.\n\n"
    "**L'évaluation.** J'ai écrit vingt questions genevoises à la main, dont quatre "
    "volontairement hors du périmètre, et noté les réponses avec RAGAS, entièrement en local. "
    "Moyennes sur les seize questions qui ont une réponse : précision du contexte 0,92, rappel "
    "du contexte 0,93, fidélité 0,85, pertinence de la réponse 0,71. J'ai aussi relu à "
    "l'aveugle un quart des réponses. La recherche est le point fort ; les réponses trop "
    "longues pèsent sur la pertinence."
)

st.header("Technologies", anchor=TITRES["Technologies"])
for groupe, elements in TECHNOLOGIES.items():
    st.subheader(groupe)
    st.markdown("\n".join(f"- **{nom}** : {role}." for nom, role in elements))

st.header("Limites connues", anchor=TITRES["Limites connues"])
st.markdown(
    "- Sur ce serveur sans carte graphique, le premier mot d'une réponse à une question nouvelle "
    "arrive après 90 à 120 secondes ; la suite s'écrit ensuite en continu. C'est le prix d'une "
    "exécution entièrement locale sur un serveur modeste.\n"
    "- Le serveur traite une seule question à la fois.\n"
    "- Chaque question est traitée seule : l'assistant ne se souvient pas des précédentes.\n"
    "- Seules les pages web sont indexées ; les documents PDF et les formulaires ne le sont pas."
)

st.header("Usage de l'IA", anchor=TITRES["Usage de l'IA"])
st.markdown(
    "- En production, aucun service d'IA externe n'est utilisé : le modèle de langage est un "
    "modèle open source exécuté localement sur le serveur du projet, et aucune donnée d'usager "
    "n'en sort.\n"
    "- Pendant la fabrication du projet, Claude (Anthropic) a été utilisé comme assistant à la "
    "rédaction du mémoire et, via Claude Code, comme assistant au développement, sous les "
    "spécifications de l'auteur. Le contenu, les idées, les choix techniques et leur validation "
    "restent entièrement ceux de l'auteur ; chaque décision est consignée dans le journal des "
    "décisions."
)
