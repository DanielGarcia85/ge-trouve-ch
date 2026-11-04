# src/app/commun.py

"""
Éléments communs de l'interface — styles, pied de page, constantes
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Rassembler ce que toutes les pages de l'interface partagent : les constantes affichées
(dépôt, contact), les styles valables partout (dont la largeur de la barre latérale, présente
sur chaque page pour que la mise en page ne se décale pas d'une page à l'autre), le sommaire
des pages de texte et le pied de page figé en bas de l'écran.
Appelé une fois par le point d'entrée (`app.py`) à chaque exécution, avant la page
demandée. Ne contient aucune logique de réponse et n'appelle pas le pipeline.

Ce que le module ne fait pas
────────────────────────────
  - pas de style propre à une page (l'en-tête, l'indicateur d'état et les sources de
    l'assistant vivent dans `vues/assistant.py`) ;
  - aucun appel externe, aucune écriture sur le disque.
"""

import streamlit as st

# ── Constantes affichées ──────────────────────────────────────────────
DEPOT = "https://github.com/DanielGarcia85/ge-trouve-ch"
CONTACT = "danielgarcia2_1_85@hotmail.com"
MEMOIRE = f"{DEPOT}/releases/tag/v1.0.0"

# Technologies citées dans le pied de page (détail et versions : page « À propos »).
TECHNOLOGIES = ("Haystack", "Gemma 4", "Qwen3-Embedding", "Chroma", "Ollama", "Streamlit", "Caddy", "Docker")

# Liens internes du pied de page : (libellé, adresse). Une page ajoutée à la navigation
# (app.py) s'ajoute aussi ici.
LIENS_INTERNES = (("À propos", "/a-propos"), ("Confidentialité", "/confidentialite"))



# ── Styles communs ────────────────────────────────────────────────────
def appliquer_styles():
    """Injecte les styles valables sur toutes les pages (pied de page, marges du contenu)."""
    st.markdown(
        f"""
        <style>
          /* Hauteur du pied de page, reprise par les marges des pages (et par le champ de
             saisie de l'assistant) pour que rien ne passe dessous. Plus haute sur mobile,
             où les lignes du pied se replient. */
          :root {{ --hauteur-pied: 6rem; }}
          @media (max-width: 640px) {{ :root {{ --hauteur-pied: 8.5rem; }} }}

          /* Barre latérale, sur toutes les pages : largeur figée quand elle est ouverte (pas
             de redimensionnement), repli intact. */
          body:has([data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stSidebar"] {{
            width: 21rem !important; min-width: 21rem !important; max-width: 21rem !important;
          }}
          [data-testid="stSidebarResizeHandle"] {{ display: none !important; }}

          /* Pied de page figé, trois lignes : crédit, technologies, liens. */
          .pied {{ position: fixed; left: 0; right: 0; bottom: 0; z-index: 1000; text-align: center;
                   height: var(--hauteur-pied); box-sizing: border-box; display: flex; flex-direction: column;
                   justify-content: center; gap: 0.15rem; padding: 0 1rem 0.6rem; line-height: 1.4;
                   background: #F7F8FA; border-top: 1px solid #E5E7EB; }}
          .pied .credit {{ color: #4B5563; font-weight: 600; font-size: 0.76rem; }}
          .pied .techno {{ color: #6B7280; font-size: 0.72rem; }}
          .pied .liens {{ font-size: 0.78rem; color: #9CA3AF; }}
          .pied .liens a {{ color: #6B7280; text-decoration: none; }}
          .pied .liens a:hover {{ text-decoration: underline; }}

          /* Le pied se décale à droite de la barre latérale quand elle est ouverte (écran large). */
          @media (min-width: 900px) {{
            body:has([data-testid="stSidebar"][aria-expanded="true"]) .pied {{ left: 21rem; }}
          }}

          /* Marges par défaut des pages de texte : le titre commence juste sous la navigation,
             et le contenu défile entièrement au-dessus du pied de page. L'assistant impose
             ses propres marges (en-tête figé). */
          [data-testid="stMainBlockContainer"], [data-testid="stMain"] .block-container {{
            padding-top: 4.5rem !important;
            padding-bottom: calc(var(--hauteur-pied) + 3rem) !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Sommaire des pages de texte ───────────────────────────────────────
def afficher_sommaire(sections):
    """
    Affiche dans la barre latérale le sommaire « Sur cette page » : un lien par section.

    `sections` est une suite de couples (titre, ancre) ; chaque titre de la page est posé avec
    la même ancre (`st.header(titre, anchor=ancre)`), fixée à la main pour ne pas dépendre
    des accents. Un clic fait défiler la page jusqu'à la section.
    """
    with st.sidebar:
        st.markdown("### Sur cette page")
        st.markdown("\n".join(f"- [{titre}](#{ancre})" for titre, ancre in sections))


# ── Pied de page ──────────────────────────────────────────────────────
def afficher_pied_de_page():
    """Affiche le pied de page figé : crédit, technologies utilisées, liens."""
    liens = [f"<a href='{adresse}' target='_self'>{libelle}</a>" for libelle, adresse in LIENS_INTERNES]
    liens += [
        f"<a href='{DEPOT}' target='_blank' rel='noopener'>GitHub</a>",
        f"<a href='{DEPOT}/blob/main/LICENSE' target='_blank' rel='noopener'>Licence MIT</a>",
    ]
    st.markdown(
        "<div class='pied'>"
        "<div class='credit'>Prototype réalisé par Daniel Garcia · "
        "Travail de Bachelor 2026, HEG Genève</div>"
        f"<div class='techno'>{' · '.join(TECHNOLOGIES)}</div>"
        f"<div class='liens'>{' · '.join(liens)}</div>"
        "</div>",
        unsafe_allow_html=True,
    )
