# src/app/app.py

"""
Interface Ge-Trouve — page de conversation locale (Streamlit)
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Exposer le pipeline de production (`src/repondre.py`) dans une page web locale : un champ
de question, la réponse (avec ses liens cliquables) affichée au fil de l'eau, et les pages
sources dans une barre latérale. Chaque question est traitée indépendamment (aucune mémoire
conversationnelle envoyée au modèle) ; l'historique reste affiché à l'écran. Consomme le
pipeline tel quel, sans le régler.

Conception
──────────
  - Un unique indicateur d'état, figé en haut à droite, décrit l'étape en cours (en attente,
    génération, terminé). Toujours visible, il évite tout indicateur au niveau du message,
    qui se cacherait derrière le champ de saisie fixe.
  - La réponse s'affiche au fur et à mesure (streaming) via un callback qui remplit une zone
    mot à mot ; aucun JavaScript, aucun fil d'exécution.
  - Mise en page en bandes figées : en-tête en haut, champ de saisie et bas de page en bas,
    pages sources dans la barre de gauche ; seule la conversation défile.

Ce que l'app n'est pas
──────────────────────
  - pas de comptes, pas d'historique persistant, rien d'écrit sur le disque ;
  - aucun appel externe : tout passe par le pipeline local (Ollama, Chroma).
"""

import sys
from pathlib import Path

import streamlit as st

# Accès au pipeline de production (src/repondre.py).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import repondre  # noqa: E402

SOUS_TITRE = "Assistant pour démarches administratives du canton de Genève"
INVITE = "Posez votre question sur une démarche genevoise…"


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


# ── Configuration de la page et styles ─────────────────────────────────
st.set_page_config(page_title="Ge-Trouve", layout="centered", initial_sidebar_state="expanded")

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
      .etat { position: fixed; top: 4.2rem; right: 2.5rem; z-index: 1100;
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
      .avert-lateral { display: none; position: fixed; bottom: 0; left: 0; width: 21rem; z-index: 1000;
                       margin: 0; padding: 0.6rem 1.5rem; color: #9CA3AF; font-size: 0.75rem !important; line-height: 1.3; }
      body:has([data-testid="stSidebar"][aria-expanded="true"]) .avert-lateral { display: block; }

      /* Bas de page figé, deux lignes (crédit + dépôt). */
      .pied { position: fixed; left: 0; right: 0; bottom: 0; z-index: 1000; text-align: center;
              height: 4rem; display: flex; flex-direction: column; justify-content: center;
              padding: 0 1rem; line-height: 1.45; background: #F7F8FA; border-top: 1px solid #E5E7EB; }
      .pied .credit { color: #4B5563; font-weight: 600; font-size: 0.76rem; }
      .pied .repo { font-size: 0.8rem; }
      .pied .repo a { color: #6B7280; text-decoration: none; }
      .pied .repo a:hover { text-decoration: underline; }

      /* Champ de saisie posé juste au-dessus du bas de page, fond opaque (le contenu défile derrière). */
      [data-testid="stBottom"] { bottom: 4rem; background: #FFFFFF; }

      /* En-tête et bas de page se décalent à droite de la barre latérale quand elle est ouverte. */
      @media (min-width: 900px) {
        body:has([data-testid="stSidebar"][aria-expanded="true"]) .entete,
        body:has([data-testid="stSidebar"][aria-expanded="true"]) .pied { left: 21rem; }
      }

      /* Marges du contenu : sous l'en-tête figé (haut) et au-dessus du champ + bas de page (bas),
         pour que la conversation défile entièrement sans être masquée. `!important` car Streamlit
         impose ses propres marges au conteneur principal. */
      [data-testid="stMainBlockContainer"], [data-testid="stMain"] .block-container {
        padding-top: 13rem !important; padding-bottom: 10rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── En-tête et bas de page (bandes figées) ─────────────────────────────
st.markdown(
    "<div class='entete'><h1>"
    "<span class='ge'>Ge</span><span class='tiret'>-</span><span class='trouve'>Trouve</span>"
    f"</h1><p>{SOUS_TITRE}</p></div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='pied'>"
    "<div class='credit'>Prototype réalisé par Daniel Garcia<br>"
    "Travail de Bachelor 2026, HEG Genève, filière Informatique de gestion · Licence MIT</div>"
    "<div class='repo'>"
    "<a href='https://github.com/DanielGarcia85/ge-trouve-ch' target='_blank' rel='noopener'>"
    "github.com/DanielGarcia85/ge-trouve-ch</a></div>"
    "</div>",
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

        texte, urls = interroger(question, sur_jeton)
        zone.markdown(texte)  # rendu final propre (liens, mise en forme)

    st.session_state.echanges.append({"question": question, "reponse": texte})
    st.session_state.dernieres_sources = urls
    afficher_sources(urls)
    afficher_etat("En attente de la prochaine question", "etat-pret")
