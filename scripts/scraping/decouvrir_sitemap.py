# scripts/scraping/decouvrir_sitemap.py

"""
Découverte des pages d'un site via son sitemap — étape 3
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Avant de scraper un site, savoir **quelles pages existent** et **lesquelles retenir**.
Le script récupère le sitemap d'un domaine (le fichier que le site publie pour lister
ses pages), en extrait toutes les URL, les classe par catégorie (premier segment du
chemin), applique un filtre, puis affiche le décompte et un échantillon. En option, il
écrit les URL retenues dans un manifeste CSV. Ne fait PAS le scraping ni l'extraction.

Deux modes de filtrage, selon la façon dont le site range ses pages :
  - par défaut, on ÉCARTE le bruit connu (documents en vrac, actualité, événements,
    variantes de langue) et on garde le reste. Adapté à ge.ch, dont les démarches sont
    éparpillées dans des URL plates, sans dossier commun.
  - avec --garder, on ne GARDE QUE certains dossiers (premiers segments du chemin).
    Adapté à geneve.ch, qui range ses démarches dans un dossier propre /demarches/.

Ce que le script n'est pas
──────────────────────────
  - ce n'est pas trafilatura (qui extrait le texte d'une page déjà téléchargée) ;
  - il ne vérifie pas robots.txt (fait par le scraper, avant d'aspirer) ;
  - il ne télécharge que des sitemaps (XML), jamais les pages elles-mêmes.

Usage
─────
  python scripts/scraping/decouvrir_sitemap.py <url_sitemap> [--garder seg1,seg2] [--sortie fichier.csv] [--ajouter]

Exemples :
  python scripts/scraping/decouvrir_sitemap.py https://www.ge.ch/sitemap.xml
  python scripts/scraping/decouvrir_sitemap.py https://www.geneve.ch/sitemap.xml --garder demarches
  python scripts/scraping/decouvrir_sitemap.py https://www.ge.ch/sitemap.xml --sortie src/scraping/manifeste_sources.csv
  python scripts/scraping/decouvrir_sitemap.py https://www.geneve.ch/sitemap.xml --garder demarches --sortie src/scraping/manifeste_sources.csv --ajouter

Le raisonnement derrière le filtre est expliqué dans `decouverte_corpus.md`.
"""

import argparse
import csv
import os
import re
import time
import urllib.request
from collections import Counter
from urllib.parse import urlparse

# ── Constantes ────────────────────────────────────────────────────────
UA = "GeTrouveBot/0.1 (+https://github.com/DanielGarcia85/ge-trouve-ch)"
DELAI = 1.5  # secondes entre deux requêtes de sitemap (politesse ; les sitemaps sont peu nombreux)

# Premiers segments de chemin à écarter en mode par défaut : du bruit, pas des démarches.
# Décision documentée dans decouverte_corpus.md (catégories observées sur ge.ch).
PREFIXES_ECARTES = {"document", "actualite", "evenement", "blog", "teaser", "organisation"}


# ── Récupération et parcours du sitemap ───────────────────────────────
def recuperer(url):
    """Télécharge le contenu d'une URL (texte), avec l'agent identifiable."""
    requete = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        return reponse.read().decode("utf-8", errors="replace")


def urls_du_sitemap(url):
    """
    Renvoie toutes les URL de pages listées par un sitemap.

    Un sitemap peut être un *index* (il pointe vers d'autres sitemaps) ou un *urlset*
    (il liste directement des pages). On distingue les deux par la balise racine, et on
    descend récursivement dans les sous-sitemaps.
    """
    contenu = recuperer(url)
    locs = re.findall(r"<loc>([^<]+)</loc>", contenu)
    if "<sitemapindex" in contenu:  # index : chaque <loc> est un sous-sitemap, on descend
        pages = []
        for sous_sitemap in locs:
            pages += urls_du_sitemap(sous_sitemap)
            time.sleep(DELAI)  # politesse entre deux sous-sitemaps
        return pages
    return locs  # urlset : les <loc> sont déjà des pages


# ── Filtre : deux modes (écarter le bruit, ou ne garder que certains dossiers) ──
def premier_segment(url):
    """Premier segment du chemin d'une URL (la « catégorie » de la page)."""
    chemin = urlparse(url).path.strip("/")
    return chemin.split("/")[0] if chemin else "(racine)"


def est_langue(segment):
    """Vrai si le segment est un code de langue (`en`, `de`, `pt-pt`…) : variante à écarter."""
    return bool(re.match(r"^[a-z]{2}(-[a-z]{2})?$", segment))


def est_bruit(url):
    """Vrai si l'URL est à écarter du corpus (pas une démarche : document, actualité, langue…)."""
    segment = premier_segment(url)
    if segment in ("(racine)", "node"):  # racine et pages Drupal sans alias : ambigües
        return True
    if segment.split("-")[0] in PREFIXES_ECARTES:
        return True
    if est_langue(segment):
        return True
    return False


def retenir(urls, garder):
    """
    Applique le filtre et renvoie les URL retenues.

    Si `garder` est fourni (ensemble de premiers segments), on ne garde QUE ces dossiers
    (mode « ne garder que », utile quand un site range ses démarches dans un dossier propre).
    Sinon, on écarte le bruit connu (mode par défaut, adapté aux URL plates de ge.ch).
    """
    if garder:
        return [u for u in urls if premier_segment(u).split("-")[0] in garder]
    return [u for u in urls if not est_bruit(u)]


# ── Point d'entrée ────────────────────────────────────────────────────
def main():
    """Analyse le sitemap passé en argument ; écrit le manifeste si --sortie est fourni."""
    analyseur = argparse.ArgumentParser(
        description="Découvre les pages d'un site via son sitemap et propose une sélection."
    )
    analyseur.add_argument("sitemap", help="URL du sitemap (ex. https://www.ge.ch/sitemap.xml)")
    analyseur.add_argument(
        "--garder",
        help="ne garder QUE ces premiers segments, séparés par des virgules (ex. demarches) ; "
        "sinon, on écarte les catégories de bruit connues",
    )
    analyseur.add_argument(
        "--sortie",
        help="fichier CSV du manifeste ; sans cette option, le script se contente d'analyser",
    )
    analyseur.add_argument(
        "--ajouter",
        action="store_true",
        help="ajouter les URL à un manifeste existant au lieu de l'écraser (pour réunir plusieurs domaines)",
    )
    args = analyseur.parse_args()

    garder = set(args.garder.split(",")) if args.garder else None

    urls = urls_du_sitemap(args.sitemap)
    if not urls:
        # Cas le plus courant : on a passé une page du site, pas son sitemap.
        print(f"Aucune URL trouvée : {args.sitemap} ne semble pas être un sitemap")
        print("(le contenu ne contient aucune balise <loc>).")
        print("Un sitemap est un fichier XML, en général à /sitemap.xml, annoncé dans le robots.txt du site.")
        print("Vérifiez l'URL : elle doit pointer vers le sitemap, pas vers une page du site.")
        return
    print(f"Total d'URL dans le sitemap : {len(urls)}")

    # Répartition par catégorie : ce qui permet de décider quoi garder.
    categories = Counter(premier_segment(u).split("-")[0] for u in urls)
    print("\n--- Répartition par catégorie (>= 20 pages) ---")
    for categorie, nombre in categories.most_common():
        if nombre >= 20:
            print(f"  {nombre:6}  {categorie}")

    gardees = retenir(urls, garder)
    mode = f"ne garder que {', '.join(sorted(garder))}" if garder else "écarter le bruit connu"
    print(f"\nMode de filtrage : {mode}")
    print(f"Écartées : {len(urls) - len(gardees)}")
    print(f"Gardées  : {len(gardees)}")

    print("\n--- Échantillon réparti dans les pages gardées ---")
    pas = max(1, len(gardees) // 15)
    for u in gardees[::pas][:15]:
        print("  ", u)

    if args.sortie:
        # En mode --ajouter, on complète un manifeste existant (autre domaine) sans réécrire l'entête.
        ajouter = args.ajouter and os.path.exists(args.sortie) and os.path.getsize(args.sortie) > 0
        with open(args.sortie, "a" if ajouter else "w", encoding="utf-8", newline="") as fichier:
            ecrivain = csv.writer(fichier, delimiter=";")
            if not ajouter:
                ecrivain.writerow(["url"])
            for u in gardees:
                ecrivain.writerow([u])
        if ajouter:
            print(f"\nManifeste complété : {args.sortie} (+{len(gardees)} URL)")
        else:
            print(f"\nManifeste écrit : {args.sortie} ({len(gardees)} URL)")


if __name__ == "__main__":
    main()
