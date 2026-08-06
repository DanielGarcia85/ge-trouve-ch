# scripts/scraping/lister_souspages_chapeau.py

"""
Découverte des sous-pages — aide à la construction du manifeste
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Pour chaque page « chapeau » du manifeste (colonne remarque), télécharger la page
et lister ses sous-pages directes sur www.ge.ch, afin de proposer des ajouts au
manifeste. Ne récupère que les pages chapeau (autorisées par robots.txt), avec un
délai de politesse et un agent identifiable. Ne récupère pas les sous-pages
trouvées : il ne fait que relever leurs URL. N'écrit rien.

Filtres
───────
  - même hôte www.ge.ch, et URL commençant par le chemin de la page chapeau
  - exclut les liens /document/ (PDF), les URL déjà présentes au manifeste
  - (les autres hôtes, dont e-demarches.ge.ch, sont écartés par le filtre d'hôte)
"""

import csv
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

UA = "GeTrouveBot/0.1 (travail de bachelor HEG)"
MANIFESTE = Path("src/scraping/manifeste_sources.csv")
DELAI = 2.0  # secondes entre deux requêtes (politesse)


class CollecteurLiens(HTMLParser):
    """Collecte les attributs href des balises <a> d'une page HTML."""

    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        """Retient le href de chaque lien rencontré."""
        if tag == "a":
            for cle, valeur in attrs:
                if cle == "href" and valeur:
                    self.hrefs.append(valeur)


def recuperer(url):
    """Télécharge une page avec l'agent identifiable et renvoie son HTML."""
    requete = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(requete, timeout=20) as reponse:
        return reponse.read().decode("utf-8", errors="replace")


def main():
    """Liste, par page chapeau, ses sous-pages directes candidates."""
    with open(MANIFESTE, encoding="utf-8") as fichier:
        lignes = list(csv.DictReader(fichier, delimiter=";"))
    connus = {ligne["url"].rstrip("/") for ligne in lignes}
    chapeaux = [ligne["url"] for ligne in lignes if "chapeau" in ligne["remarque"]]

    for indice, url in enumerate(chapeaux):
        if indice:
            time.sleep(DELAI)
        base = url.rstrip("/")
        try:
            html = recuperer(url)
        except Exception as erreur:
            print(f"\n## {url}\n  ECHEC: {erreur}")
            continue
        parseur = CollecteurLiens()
        parseur.feed(html)
        candidats = set()
        for href in parseur.hrefs:
            resolu = urljoin(url, href.split("#")[0].split("?")[0]).rstrip("/")
            if urlparse(resolu).netloc != "www.ge.ch":
                continue
            if not resolu.startswith(base + "/"):
                continue
            if "/document/" in resolu or resolu in connus:
                continue
            candidats.add(resolu)
        print(f"\n## {url}")
        if candidats:
            for candidat in sorted(candidats):
                print(f"  {candidat}")
        else:
            print("  (aucune sous-page directe nouvelle)")


if __name__ == "__main__":
    main()
