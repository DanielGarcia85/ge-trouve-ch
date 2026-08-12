# src/scraping/scrape_pilote.py

"""
Scraper pilote — pages ge.ch du permis de séjour
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Lire le manifeste des sources, télécharger chaque page autorisée par robots.txt
(délai de politesse, agent identifiable), extraire son texte principal via
HTMLToDocument (trafilatura), en markdown avec les hyperliens préservés (résolus en
absolu), et écrire un fichier JSON par page sous `DATA_DIR/pilote/pages/` (corpus brut,
non versionné). Tient un journal d'exécution
dans `resultats/pilote/` (versionné). Ne fait ni le découpage ni l'indexation.

Politesse et sûreté
───────────────────
  - robots.txt vérifié pour chaque URL (page ignorée si interdite) ;
  - délai >= 2 s entre deux requêtes, une seule passe ;
  - agent identifiable, HTML texte seulement, aucun crawl au-delà du manifeste ;
  - une URL en échec est consignée, jamais remplacée ; moins de 10 pages -> arrêt.
"""

import csv
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from haystack.components.converters import HTMLToDocument
from haystack.dataclasses import ByteStream

# Accès au module de configuration partagé (src/config.py).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

# ── Constantes ────────────────────────────────────────────────────────
UA = "GeTrouveBot/0.1 (+https://github.com/DanielGarcia85/ge-trouve-ch)"
ROBOTS_URL = "https://www.ge.ch/robots.txt"
HOTE = "www.ge.ch"
MANIFESTE = Path("src/scraping/manifeste_sources_pilote.csv")
DELAI = 2.0            # secondes entre deux requêtes (politesse)
MINIMUM_PAGES = 10     # en dessous, on arrête et on diagnostique

# Corpus brut sous DATA_DIR (non versionné) ; journal d'exécution sous RESULTATS_DIR (versionné).
DOSSIER_PILOTE = Path(config.DATA_DIR) / "pilote"
DOSSIER_PAGES = DOSSIER_PILOTE / "pages"
JOURNAL = config.RESULTATS_DIR / "pilote" / "journal_scraping_pilote.md"


# ── Utilitaires ───────────────────────────────────────────────────────
def charger_manifeste():
    """Charge les lignes du manifeste (séparateur point-virgule)."""
    with open(MANIFESTE, encoding="utf-8") as fichier:
        return list(csv.DictReader(fichier, delimiter=";"))


def charger_robots():
    """Récupère et analyse le robots.txt de www.ge.ch."""
    requete = urllib.request.Request(ROBOTS_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(requete, timeout=20) as reponse:
        contenu = reponse.read().decode("utf-8", errors="replace")
    parseur = RobotFileParser()
    parseur.parse(contenu.splitlines())
    return parseur


def nom_fichier(url):
    """Chemin de l'URL aplati, pour un nom de fichier sans collision entre hubs."""
    return urlparse(url).path.strip("/").replace("/", "__") + ".json"


def recuperer(url):
    """Télécharge une page et renvoie (contenu octets, statut HTTP, URL finale)."""
    requete = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        return reponse.read(), reponse.status, reponse.geturl()


def extraire_texte(convertisseur, html_octets, url):
    """Extrait le texte principal via HTMLToDocument (trafilatura), en markdown avec les
    hyperliens préservés et résolus en absolu (paramètre url)."""
    flux = ByteStream(data=html_octets, mime_type="text/html")
    resultat = convertisseur.run(
        sources=[flux],
        extraction_kwargs={"output_format": "markdown", "include_links": True, "url": url},
    )
    documents = resultat["documents"]
    if documents and documents[0].content:
        return documents[0].content.strip()
    return ""


def ecrire_journal(entrees, reussies, echecs, capture):
    """Écrit le journal d'exécution du scraping au format Markdown."""
    lignes = [
        f"# Journal de scraping pilote — {capture}",
        "",
        f"{reussies} pages réussies, {echecs} échecs, sur {len(entrees)} URL du manifeste.",
        "",
        "| URL | Statut | Taille (caractères) | Durée (s) |",
        "|---|---|---|---|",
    ]
    for url, statut, taille, duree in entrees:
        lignes.append(f"| {url} | {statut} | {taille} | {duree:.2f} |")
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text("\n".join(lignes) + "\n", encoding="utf-8")


# ── Point d'entrée ────────────────────────────────────────────────────
def main():
    """Scrape les pages du manifeste et écrit un JSON par page réussie."""
    lignes = charger_manifeste()
    robots = charger_robots()
    convertisseur = HTMLToDocument()
    DOSSIER_PAGES.mkdir(parents=True, exist_ok=True)
    capture = date.today().isoformat()

    entrees_journal = []
    reussies = 0
    echecs = 0

    for indice, ligne in enumerate(lignes):
        url = ligne["url"]
        if indice:
            time.sleep(DELAI)  # délai de politesse entre deux requêtes

        if not robots.can_fetch("GeTrouveBot", url):
            entrees_journal.append((url, "robots : interdit", 0, 0.0))
            echecs += 1
            print(f"  [NON] robots interdit  {url}")
            continue

        debut = time.perf_counter()
        try:
            html, statut, url_finale = recuperer(url)
        except HTTPError as erreur:
            entrees_journal.append((url, f"HTTP {erreur.code}", 0, time.perf_counter() - debut))
            echecs += 1
            print(f"  [NON] HTTP {erreur.code}  {url}")
            continue
        except URLError as erreur:
            entrees_journal.append((url, f"erreur réseau : {erreur.reason}", 0, time.perf_counter() - debut))
            echecs += 1
            print(f"  [NON] réseau  {url}")
            continue
        duree = time.perf_counter() - debut

        # Une redirection qui sort de www.ge.ch est un échec, pas une substitution.
        if urlparse(url_finale).netloc != HOTE:
            entrees_journal.append((url, f"redirection hors ge.ch ({url_finale})", 0, duree))
            echecs += 1
            print(f"  [NON] redirection hors ge.ch  {url}")
            continue

        texte = extraire_texte(convertisseur, html, url_finale)
        if not texte:
            entrees_journal.append((url, "texte vide", 0, duree))
            echecs += 1
            print(f"  [NON] texte vide  {url}")
            continue

        page = {
            "url": url,
            "titre": ligne["titre"],
            "section": ligne["section"],
            "date_capture": capture,
            "texte": texte,
        }
        (DOSSIER_PAGES / nom_fichier(url)).write_text(
            json.dumps(page, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        entrees_journal.append((url, f"HTTP {statut}", len(texte), duree))
        reussies += 1
        print(f"  [OK ] {len(texte):>6} car.  {url}")

    ecrire_journal(entrees_journal, reussies, echecs, capture)
    print(f"\n{reussies} pages réussies, {echecs} échecs. Journal : {JOURNAL}")
    if reussies < MINIMUM_PAGES:
        print(f"ARRET : moins de {MINIMUM_PAGES} pages exploitables, diagnostic nécessaire.")
        sys.exit(1)


if __name__ == "__main__":
    main()
