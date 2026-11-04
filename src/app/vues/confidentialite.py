# src/app/vues/confidentialite.py

"""
Page « Confidentialité » — ce que le site fait réellement des données
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Décrire, pour l'usager, ce que devient sa question et ce que le serveur garde : journaux
techniques, cookies, hébergement, sauvegardes, sécurité et droits. Chaque affirmation
correspond à un fait vérifié dans le code du dépôt et sur le serveur de production
(configuration Docker, Caddy, Streamlit, pare-feu). Page statique : aucun appel au pipeline,
aucune donnée de l'usager.

À tenir à jour
──────────────
Toute modification qui change ce que le site enregistre ou transmet (journaux, cookies,
service tiers, sauvegardes) doit être reportée ici, avec la date de mise à jour
(`MISE_A_JOUR`).
"""

import streamlit as st

import commun

MISE_A_JOUR = "4 novembre 2026"
PFPDT = "https://www.edoeb.admin.ch"

SECTIONS = (
    ("En bref", "en-bref"),
    ("Qui est responsable", "responsable"),
    ("Ce que devient votre question", "question"),
    ("Journaux techniques", "journaux"),
    ("Cookies et stockage local", "cookies"),
    ("Hébergement et tiers", "hebergement"),
    ("Sauvegardes", "sauvegardes"),
    ("Sécurité", "securite"),
    ("Vos droits", "droits"),
    ("Modifications de cette page", "modifications"),
)
TITRES = dict(SECTIONS)

commun.afficher_sommaire(SECTIONS)

commun.afficher_titre("Confidentialité", f"Dernière mise à jour : {MISE_A_JOUR}")

st.header("En bref", anchor=TITRES["En bref"])
st.markdown(
    "- Pas de compte, pas de publicité, pas de traceur, pas de mesure d'audience.\n"
    "- Votre question est traitée sur un serveur en Suisse, sans aucun service d'intelligence "
    "artificielle externe, et l'application ne l'enregistre nulle part.\n"
    "- Le serveur tient des journaux techniques, limités en volume ; votre question n'y "
    "figure pas.\n"
    "- Aucune donnée n'est vendue ni transmise à qui que ce soit."
)

st.header("Qui est responsable", anchor=TITRES["Qui est responsable"])
st.markdown(
    "Ge-Trouve est un prototype réalisé dans le cadre de mon Travail de Bachelor à la HEG "
    "Genève, sans activité commerciale. Le responsable du traitement est Daniel Garcia, "
    f"personne privée, à Genève, en Suisse. Pour toute question sur cette page : {commun.CONTACT}."
)

st.header("Ce que devient votre question", anchor=TITRES["Ce que devient votre question"])
st.markdown(
    "- Elle part de votre navigateur vers le serveur en HTTPS (connexion chiffrée).\n"
    "- Sur le serveur, elle est transformée en vecteur, comparée aux pages officielles indexées, "
    "puis transmise avec les extraits retrouvés au modèle de langage, qui rédige la réponse. "
    "Tout se passe en mémoire, sur cette machine.\n"
    "- L'application ne l'écrit ni dans un fichier ni dans une base de données.\n"
    "- Elle reste affichée dans votre onglet, avec la réponse, tant que vous ne le fermez ou ne "
    "le rechargez pas. Le serveur garde cet affichage en mémoire le temps de votre visite, puis "
    "le libère : Streamlit, la bibliothèque de l'interface, efface les sessions fermées au plus "
    "tôt deux minutes après leur fermeture.\n"
    "- Le modèle de langage garde en mémoire la dernière demande traitée, pour répondre plus "
    "vite si elle revient ; la question suivante la remplace.\n\n"
    "L'assistant n'a besoin d'aucune donnée personnelle pour répondre : n'écrivez dans vos "
    "questions ni votre nom, ni votre adresse, ni un numéro d'assuré ou de dossier."
)

st.header("Journaux techniques", anchor=TITRES["Journaux techniques"])
st.markdown(
    "Comme tout serveur, celui de Ge-Trouve note ce qui lui permet de fonctionner et de "
    "diagnostiquer une panne :\n\n"
    "- **L'application** note ses démarrages et ses erreurs (le type d'erreur et la ligne de "
    "code en cause), jamais le texte de votre question.\n"
    "- **Le serveur de modèles** note une ligne technique par demande (l'heure, la durée, le "
    "type de demande), sans son contenu.\n"
    "- **Le proxy HTTPS** ne note pas les visites. Seulement quand la transmission d'une page "
    "échoue, il note la demande en cause : votre adresse IP, votre navigateur, sa langue, la "
    "page demandée et l'heure.\n"
    "- **Le pare-feu du serveur** note les connexions qu'il refuse (adresse IP d'origine, "
    "port visé), le plus souvent des robots qui sondent Internet.\n\n"
    "Les journaux de l'application, du serveur de modèles et du proxy sont limités en volume : "
    "au-delà, les lignes les plus anciennes sont remplacées par les plus récentes. Seul "
    "l'exploitant du serveur y a accès."
)

st.header("Cookies et stockage local", anchor=TITRES["Cookies et stockage local"])
st.markdown(
    "Le site ne pose aucun cookie tiers et ne garde dans votre navigateur que ce dont "
    "l'interface a besoin pour fonctionner :\n\n"
    "- **`_streamlit_xsrf`** : un cookie qui protège le site contre les requêtes forgées par un "
    "autre site ; il disparaît à la fermeture du navigateur.\n"
    "- **Le thème de l'interface**, une clé gardée par Streamlit dans le stockage local de "
    "votre navigateur.\n\n"
    "Les statistiques d'usage que Streamlit peut envoyer à son éditeur sont désactivées. La "
    "page ne charge aucune ressource depuis un autre site : police, scripts et images sont "
    "servis par le serveur de Ge-Trouve."
)

st.header("Hébergement et tiers", anchor=TITRES["Hébergement et tiers"])
st.markdown(
    "- **Infomaniak** (Infomaniak Network SA, Genève) héberge le serveur, dans un centre de "
    "données en Suisse.\n"
    "- **Let's Encrypt** délivre le certificat HTTPS du site ; il ne reçoit aucune donnée des "
    "visiteurs.\n"
    "- **GitHub** héberge le code source public ; il ne reçoit aucune donnée des visiteurs.\n\n"
    "Vos données ne quittent pas la Suisse et ne sont communiquées à personne."
)

st.header("Sauvegardes", anchor=TITRES["Sauvegardes"])
st.markdown(
    "Ge-Trouve est un prototype de Travail de Bachelor : aucune sauvegarde du serveur n'est en "
    "place. Le site ne garde de toute façon aucune donnée de ses usagers à sauvegarder."
)

st.header("Sécurité", anchor=TITRES["Sécurité"])
st.markdown(
    "Tout le site est servi en HTTPS. Seul le proxy est joignable depuis Internet ; "
    "l'application et le serveur de modèles tournent dans un réseau interne, et l'application "
    "s'exécute sans privilèges. L'administration du serveur passe par une connexion SSH "
    "protégée par clé, derrière un pare-feu."
)

st.header("Vos droits", anchor=TITRES["Vos droits"])
st.markdown(
    "Selon la loi fédérale sur la protection des données (LPD), vous pouvez demander quelles "
    "données vous concernant sont traitées, les faire corriger ou supprimer. Le site "
    "n'enregistrant rien qui vous identifie, hors des journaux décrits plus haut, il n'aura en "
    f"général rien à vous communiquer ; écrivez quand même à {commun.CONTACT}, la réponse est "
    "gratuite.\n\n"
    "Si vous estimez que vos droits ne sont pas respectés, vous pouvez vous adresser au Préposé "
    f"fédéral à la protection des données et à la transparence ([PFPDT]({PFPDT}))."
)

st.header("Modifications de cette page", anchor=TITRES["Modifications de cette page"])
st.markdown(
    "Cette page décrit le site tel qu'il fonctionne. Elle change quand le site change, et la "
    "date en tête indique sa dernière mise à jour."
)
