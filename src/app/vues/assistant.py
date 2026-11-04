# src/app/vues/assistant.py

"""
Page « Assistant » — conversation avec le pipeline de production (Streamlit)
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Exposer le pipeline de production (`src/repondre.py`) dans une page web : un champ
de question, la réponse (avec ses liens cliquables) affichée au fil de l'eau, et les pages
sources dans une barre latérale. Chaque question est traitée indépendamment (aucune mémoire
conversationnelle envoyée au modèle) ; l'historique reste affiché à l'écran. Consomme le
pipeline tel quel, sans le régler. Page d'accueil de la navigation déclarée dans `app.py`,
qui fournit aussi la configuration de la page et le pied de page (`commun.py`).

Conception
──────────
  - Un unique indicateur d'état, figé en haut à droite, décrit l'étape en cours (en attente,
    génération, terminé). Toujours visible, il évite tout indicateur au niveau du message,
    qui se cacherait derrière le champ de saisie fixe.
  - La réponse s'affiche au fur et à mesure (streaming) via un callback qui remplit une zone
    mot à mot ; aucun JavaScript, aucun fil d'exécution.
  - Mise en page en bandes figées : en-tête en haut, champ de saisie et bas de page en bas,
    pages sources dans la barre de gauche ; seule la conversation défile.
  - Si le pipeline échoue, l'usager lit un message simple en français ; la trace de l'erreur
    part dans le journal du serveur, sans le texte de la question.

Ce que la page n'est pas
────────────────────────
  - pas de comptes, pas d'historique persistant, rien d'écrit sur le disque ;
  - aucun appel externe : tout passe par le pipeline local (Ollama, Chroma).
"""

import logging
import sys
from pathlib import Path

import streamlit as st

# Accès au pipeline de production (src/repondre.py) : ce fichier est src/app/vues/assistant.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import repondre  # noqa: E402

# Journal du serveur (sortie d'erreur du conteneur, lue par `docker compose logs app`).
JOURNAL = logging.getLogger("ge_trouve.assistant")

SOUS_TITRE = "Assistant pour démarches administratives du canton de Genève"
INVITE = "Posez votre question sur une démarche genevoise…"
MESSAGE_ERREUR = (
    "Le service n'a pas pu répondre. Réessayez dans quelques minutes : "
    "le serveur traite une seule question à la fois et peut être momentanément occupé."
)


# ── Pont vers le pipeline ──────────────────────────────────────────────
def interroger(question, sur_jeton):
    """
    Interroge le pipeline de production ; renvoie (texte de la réponse, URL sources uniques).

    `sur_jeton` reçoit chaque mot au fil de la génération (affichage progressif). Le pipeline
    est reconstruit à chaque question ; les modèles, eux, restent résidents côté Ollama.
    """
    pipe = repondre.construire_pipeline(streaming_callback=sur_jeton)
    requete = f"Instruct: {repondre.TACHE}\nQuery:{question}"
    resultat = pipe.run(
        {"embedder": {"text": requete}, "prompt_builder": {"question": question}},
        include_outputs_from={"retriever"},
    )
    texte = resultat["generator"]["replies"][0].text
    urls = []
    for doc in resultat["retriever"]["documents"]:
        url = doc.meta.get("url")
        if url and url not in urls:
            urls.append(url)
    return texte, urls


# ── Styles propres à cette page ─────────────────────────────────────
st.markdown(
    """
    <style>
      /* En-tête figé en haut, fond blanc opaque (masque le texte qui défile dessous). */
      .entete { position: fixed; top: 0; left: 0; right: 0; z-index: 900;
                background: #FFFFFF; text-align: center; padding: 3rem 0 0.6rem; }
      .entete h1 { margin: 0; font-weight: 800; letter-spacing: -0.5px; font-size: 2.4rem; }
      .entete .ge { color: #F2B705; }       /* jaune genevois */
      .entete .tiret { color: #1F2430; }    /* trait d'union noir */
      .entete .trouve { color: #C8102E; }   /* rouge genevois */
      .entete p { color: #6B7280; margin: 0.2rem 0 0; font-size: 0.98rem; }

      /* Indicateur d'état, figé en haut à droite. Point de couleur : vert = prêt,
         orange (clignotant) = génération en cours. */
      .etat { position: fixed; top: 1rem; right: 2.5rem; z-index: 999999;
              display: inline-flex; align-items: center; gap: 0.45rem;
              padding: 0.3rem 0.8rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600;
              border: 1px solid #E5E7EB; background: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
      .etat::before { content: ''; width: 0.55rem; height: 0.55rem; border-radius: 50%; flex: none; }
      .etat-pret { color: #15803D; }
      .etat-pret::before { background: #22C55E; }
      .etat-actif { color: #B45309; animation: clignote 1s ease-in-out infinite; }
      .etat-actif::before { background: #F59E0B; }
      @keyframes clignote { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

      /* Barre latérale : largeur figée quand ouverte (pas de redimensionnement), repli intact. */
      body:has([data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stSidebar"] {
        width: 21rem !important; min-width: 21rem !important; max-width: 21rem !important;
      }
      [data-testid="stSidebarResizeHandle"] { display: none !important; }

      /* Texte d'attente des sources : petite police, sur une seule ligne. */
      .attente-sources { color: #9CA3AF !important; font-size: 0.8rem !important; white-space: nowrap; margin: 0; }

      /* Avertissement « vérifiez à la source », collé au bas de la barre latérale (visible
         seulement quand elle est ouverte). */
      .avert-lateral { display: none; position: fixed; bottom: 0.4rem; left: 0; width: 21rem; z-index: 1000;
                       margin: 0; padding: 0.6rem 1.5rem 0.9rem; color: #9CA3AF; font-size: 0.75rem !important; line-height: 1.3; }
      body:has([data-testid="stSidebar"][aria-expanded="true"]) .avert-lateral { display: block; }

      /* Champ de saisie posé juste au-dessus du pied de page (hauteur définie dans commun.py), fond opaque (le contenu défile derrière). */
      [data-testid="stBottom"] { bottom: var(--hauteur-pied); background: #FFFFFF; }

      /* L'en-tête se décale à droite de la barre latérale quand elle est ouverte. */
      @media (min-width: 900px) {
        body:has([data-testid="stSidebar"][aria-expanded="true"]) .entete { left: 21rem; }
      }

      /* Barre latérale ouverte : elle passe devant l'indicateur d'état, qui reste visible
         dans l'espace qu'elle ne couvre pas (au lieu de disparaître). */
      body:has([data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stSidebar"] {
        z-index: 1000000 !important;
      }

      /* Marges du contenu : sous l'en-tête figé (haut) et au-dessus du champ + bas de page (bas),
         pour que la conversation défile entièrement sans être masquée. `!important` car Streamlit
         impose ses propres marges au conteneur principal. */
      [data-testid="stMainBlockContainer"], [data-testid="stMain"] .block-container {
        padding-top: 13rem !important; padding-bottom: calc(var(--hauteur-pied) + 6rem) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── En-tête (bande figée) ─────────────────────────────────────────────
st.markdown(
    "<div class='entete'><h1>"
    "<span class='ge'>Ge</span><span class='tiret'>-</span><span class='trouve'>Trouve</span>"
    f"</h1><p>{SOUS_TITRE}</p></div>",
    unsafe_allow_html=True,
)


# ── Indicateur d'état (haut à droite) ──────────────────────────────────
etat = st.empty()


def afficher_etat(texte, classe):
    """Met à jour l'indicateur d'état en haut à droite (texte + point de couleur)."""
    etat.markdown(f"<div class='etat {classe}'>{texte}</div>", unsafe_allow_html=True)


afficher_etat("En attente de votre question", "etat-pret")


# ── Barre latérale (pages sources) ─────────────────────────────────────
# Créée tôt, avec une zone actualisable : vidée dès l'envoi d'un prompt, remplie à la réponse.
with st.sidebar:
    st.markdown("### Pages sources")
    zone_sources = st.empty()
    st.markdown(
        "<p class='avert-lateral'>Les réponses s'appuient sur les pages officielles citées.<br>"
        "Vérifiez toujours l'information à la source.</p>",
        unsafe_allow_html=True,
    )


def afficher_sources(sources):
    """Affiche les liens des pages sources (ou le texte d'attente si la liste est vide)."""
    if sources:
        zone_sources.markdown("\n".join(f"- [{url}]({url})" for url in sources))
    else:
        zone_sources.markdown(
            "<p class='attente-sources'>Les sources de la dernière réponse s'afficheront ici.</p>",
            unsafe_allow_html=True,
        )


afficher_sources(st.session_state.get("dernieres_sources", []))


# ── Conversation ───────────────────────────────────────────────────────
if "echanges" not in st.session_state:
    st.session_state.echanges = []

# Historique déjà échangé (le modèle ne le reçoit pas : chaque question est indépendante).
for echange in st.session_state.echanges:
    with st.chat_message("user"):
        st.markdown(echange["question"])
    with st.chat_message("assistant"):
        if echange.get("erreur"):
            st.error(echange["reponse"])
        else:
            st.markdown(echange["reponse"])

question = st.chat_input(INVITE)
if question:
    with st.chat_message("user"):
        st.markdown(question)

    # État « génération » et sources vidées AVANT l'appel, donc dès l'envoi du prompt.
    afficher_etat("Génération en cours", "etat-actif")
    afficher_sources([])

    with st.chat_message("assistant"):
        zone = st.empty()
        morceaux = []

        def sur_jeton(chunk):
            """Ajoute le mot reçu et rafraîchit l'affichage en direct (portée locale)."""
            morceaux.append(getattr(chunk, "content", "") or "")
            zone.markdown("".join(morceaux))

        try:
            texte, urls = interroger(question, sur_jeton)
            erreur = False
            zone.markdown(texte)  # rendu final propre (liens, mise en forme)
        except Exception:
            # Trace complète dans le journal du serveur, sans la question (rien de l'usager).
            JOURNAL.exception("Échec du pipeline de réponse")
            texte, urls, erreur = MESSAGE_ERREUR, [], True
            zone.error(texte)

    st.session_state.echanges.append({"question": question, "reponse": texte, "erreur": erreur})
    st.session_state.dernieres_sources = urls
    afficher_sources(urls)
    afficher_etat("En attente de la prochaine question", "etat-pret")
