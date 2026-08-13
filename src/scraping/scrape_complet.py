# src/scraping/scrape_complet.py

"""
Scraper du corpus complet — pages ge.ch et geneve.ch
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Lire le manifeste complet (une colonne `url`, plusieurs domaines), télécharger
chaque page autorisée par le robots.txt de SON domaine (délai de politesse, agent
identifiable), extraire son texte principal via HTMLToDocument (trafilatura) en
markdown avec les hyperliens préservés (résolus en absolu), en dériver le titre
depuis la page, et écrire un fichier JSON par page sous `DATA_DIR/pages/complet/`
(corpus brut, non versionné). Tient un journal résumé sous `resultats/complet/`
(versionné). Ne fait ni le découpage ni l'indexation.

Différences avec le pilote
──────────────────────────
  - manifeste à une seule colonne `url` : le titre est extrait de chaque page, et
    il n'y a pas de métadonnée « section » ;
  - plusieurs domaines : robots.txt et contrôle de redirection PAR domaine ;
  - reprise : une page déjà présente dans `DATA_DIR/pages/complet/` est sautée, donc
    une exécution interrompue reprend où elle s'était arrêtée ;
  - journal résumé (compteurs + liste des échecs), pas une ligne par page.

Politesse et sûreté
───────────────────
  - robots.txt vérifié pour chaque URL, sur le robots du domaine de l'URL ;
  - délai >= 2 s (ou le crawl-delay du domaine s'il est plus grand) entre deux requêtes ;
  - agent identifiable, HTML texte seulement, aucun crawl au-delà du manifeste ;
  - une redirection hors du domaine d'origine est un échec, pas une substitution ;
  - une URL en échec est consignée, jamais remplacée.

Usage
─────
  python src/scraping/scrape_complet.py             (scrape tout le manifeste)
  python src/scraping/scrape_complet.py --limite 5  (test : les 5 premières URL)
"""

import argparse
import csv
import hashlib
import html
import json
import re
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
UA_ROBOTS = "GeTrouveBot"  # nom d'agent testé contre robots.txt
MANIFESTE = Path("src/scraping/manifeste_sources.csv")
DELAI = 2.0  # secondes entre deux requêtes (politesse), sauf crawl-delay plus grand

DOSSIER_PAGES = Path(config.DATA_DIR) / "pages" / "complet"
JOURNAL = config.RESULTATS_DIR / "complet" / "journal_scraping.md"


# ── Utilitaires ───────────────────────────────────────────────────────
def charger_manifeste():
    """Charge les URL du manifeste (une colonne `url`, séparateur point-virgule)."""
    with open(MANIFESTE, encoding="utf-8") as fichier:
        return [ligne["url"] for ligne in csv.DictReader(fichier, delimiter=";")]


def robots_du_domaine(cache, netloc):
    """
    Renvoie le RobotFileParser d'un domaine, chargé une seule fois puis mis en cache.

    Le robots.txt est propre à chaque domaine : on le charge au premier passage sur
    ce domaine, puis on réutilise le résultat. Renvoie None si le fichier est illisible
    (par prudence, on n'aspire pas un domaine dont on n'a pas pu lire les règles).
    """
    if netloc not in cache:
        parseur = RobotFileParser()
        try:
            requete = urllib.request.Request(
                f"https://{netloc}/robots.txt", headers={"User-Agent": UA}
            )
            with urllib.request.urlopen(requete, timeout=20) as reponse:
                contenu = reponse.read().decode("utf-8", errors="replace")
            parseur.parse(contenu.splitlines())
        except (HTTPError, URLError):
            parseur = None
        cache[netloc] = parseur
    return cache[netloc]


def nom_fichier(url):
    """
    Nom de fichier unique et borné pour une URL.

    Domaine + chemin aplati (pour rester lisible), tronqué et suivi d'une empreinte de
    l'URL. L'empreinte garantit l'unicité même après troncature et même entre domaines ;
    la borne de longueur évite de dépasser la limite de chemin de Windows sur les URL longues.
    """
    morceaux = urlparse(url)
    base = f"{morceaux.netloc}__{morceaux.path.strip('/').replace('/', '__')}"
    empreinte = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    return f"{base[:120]}__{empreinte}.json"


def recuperer(url):
    """Télécharge une page et renvoie (contenu octets, statut HTTP, URL finale)."""
    requete = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        return reponse.read(), reponse.status, reponse.geturl()


def extraire_titre(html_octets, url):
    """Extrait le titre depuis la balise <title>, nettoyé d'un éventuel suffixe du site."""
    texte = html_octets.decode("utf-8", errors="replace")
    correspondance = re.search(r"<title[^>]*>(.*?)</title>", texte, re.IGNORECASE | re.DOTALL)
    if correspondance:
        titre = html.unescape(correspondance.group(1)).strip()
        titre = titre.split("|")[0].strip()  # retire un suffixe « | ge.ch », « | Ville de Genève »
        if titre:
            return titre
    # Repli : dernier segment de l'URL rendu lisible.
    return urlparse(url).path.strip("/").split("/")[-1].replace("-", " ")


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


def ecrire_journal(total, reussies, sautees, echecs, capture):
    """Écrit un journal résumé : compteurs, puis la liste des échecs (les succès sont seulement comptés)."""
    lignes = [
        f"# Journal de scraping du corpus complet — {capture}",
        "",
        f"- URL du manifeste : {total}",
        f"- Pages présentes dans le corpus : {reussies + sautees}",
        f"  - dont scrapées lors de cette exécution : {reussies}",
        f"  - déjà présentes (sautées) : {sautees}",
        f"- Échecs : {len(echecs)}",
        "",
    ]
    if echecs:
        lignes += ["## Échecs", "", "| URL | Raison |", "|---|---|"]
        lignes += [f"| {url} | {raison} |" for url, raison in echecs]
    else:
        lignes.append("Aucun échec.")
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text("\n".join(lignes) + "\n", encoding="utf-8")


# ── Point d'entrée ────────────────────────────────────────────────────
def main():
    """Scrape les pages du manifeste (reprise incluse) et écrit un JSON par page réussie."""
    analyseur = argparse.ArgumentParser(description="Scraper du corpus complet (ge.ch + geneve.ch).")
    analyseur.add_argument("--limite", type=int, help="ne traiter que les N premières URL (pour tester)")
    args = analyseur.parse_args()

    urls = charger_manifeste()
    if args.limite:
        urls = urls[: args.limite]
    total = len(urls)

    convertisseur = HTMLToDocument()
    DOSSIER_PAGES.mkdir(parents=True, exist_ok=True)
    capture = date.today().isoformat()
    cache_robots = {}

    reussies = 0
    sautees = 0
    echecs = []
    requete_faite = False  # sert à ne pas attendre avant la toute première requête réseau

    for indice, url in enumerate(urls, start=1):
        destination = DOSSIER_PAGES / nom_fichier(url)

        # Reprise : si la page est déjà scrapée, on la saute (aucune nouvelle requête).
        if destination.exists():
            sautees += 1
            continue

        netloc = urlparse(url).netloc
        robots = robots_du_domaine(cache_robots, netloc)
        if robots is None:
            echecs.append((url, "robots.txt illisible"))
            print(f"  [NON] robots illisible  {url}")
            continue
        if not robots.can_fetch(UA_ROBOTS, url):
            echecs.append((url, "robots : interdit"))
            print(f"  [NON] robots interdit  {url}")
            continue

        # Délai de politesse avant chaque requête réseau (sauf la première).
        if requete_faite:
            time.sleep(max(DELAI, robots.crawl_delay(UA_ROBOTS) or 0))
        requete_faite = True

        try:
            html_octets, statut, url_finale = recuperer(url)
        except HTTPError as erreur:
            echecs.append((url, f"HTTP {erreur.code}"))
            print(f"  [NON] HTTP {erreur.code}  {url}")
            continue
        except URLError as erreur:
            echecs.append((url, f"réseau : {erreur.reason}"))
            print(f"  [NON] réseau  {url}")
            continue

        # Une redirection qui sort du domaine d'origine est un échec, pas une substitution.
        if urlparse(url_finale).netloc != netloc:
            echecs.append((url, f"redirection hors domaine ({url_finale})"))
            print(f"  [NON] redirection hors domaine  {url}")
            continue

        texte = extraire_texte(convertisseur, html_octets, url_finale)
        if not texte:
            echecs.append((url, "texte vide"))
            print(f"  [NON] texte vide  {url}")
            continue

        page = {
            "url": url,
            "titre": extraire_titre(html_octets, url_finale),
            "date_capture": capture,
            "texte": texte,
        }
        destination.write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf-8")
        reussies += 1
        print(f"  [OK ] {indice}/{total}  {len(texte):>6} car.  {url}")

    ecrire_journal(total, reussies, sautees, echecs, capture)
    print(f"\n{reussies} réussies, {sautees} sautées, {len(echecs)} échecs sur {total} URL.")
    print(f"Journal : {JOURNAL}")


if __name__ == "__main__":
    main()
