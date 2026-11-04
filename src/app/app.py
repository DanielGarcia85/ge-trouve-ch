# src/app/app.py

"""
Interface Ge-Trouve — point d'entrée Streamlit et navigation
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Configurer la page (titre, icône, barre latérale), appliquer les styles communs, afficher
le pied de page et déclarer les pages de l'interface dans une navigation placée en haut.
Streamlit exécute ce fichier à chaque interaction, puis la page demandée.

Ce que le fichier ne fait pas
─────────────────────────────
  - aucune logique de page : la conversation vit dans `vues/assistant.py` ;
  - aucun appel au pipeline de réponse.

Pages
─────
  - « Assistant » (page d'accueil) : `vues/assistant.py` ;
  - « À propos » (`/a-propos`) : `vues/a_propos.py`.

Le dossier s'appelle `vues/` et non `pages/` : Streamlit réserve à un dossier `pages/` placé
à côté du point d'entrée un comportement propre ; un autre nom évite toute ambiguïté.
"""

import sys
from pathlib import Path

import streamlit as st

# Dossier de l'interface, construit depuis ce fichier (pas le répertoire de lancement) :
# fonctionne en local (lancé depuis la racine) comme en conteneur (/app).
DOSSIER = Path(__file__).resolve().parent
sys.path.insert(0, str(DOSSIER))
import commun  # noqa: E402

# Repli sur l'icône par défaut de Streamlit si l'actif est absent.
FAVICON = DOSSIER / "assets" / "logo_ge-trouve.png"
st.set_page_config(
    page_title="Ge-Trouve",
    page_icon=str(FAVICON) if FAVICON.exists() else None,
    layout="centered",
    # « auto » : barre latérale ouverte sur un écran large, fermée sur mobile (elle couvrirait
    # sinon toute la page au premier affichage).
    initial_sidebar_state="auto",
)

commun.appliquer_styles()

navigation = st.navigation(
    [
        st.Page(DOSSIER / "vues" / "assistant.py", title="Assistant", default=True),
        st.Page(DOSSIER / "vues" / "a_propos.py", title="À propos", url_path="a-propos"),
    ],
    position="top",
)

commun.afficher_pied_de_page()
navigation.run()
