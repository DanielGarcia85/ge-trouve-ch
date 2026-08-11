# scripts/scraping/verifier_robots.py

"""
Vérification robots.txt — pré-requis au scraping ge.ch
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Lire le manifeste des sources, récupérer le robots.txt de www.ge.ch et tester,
pour chaque URL, si l'agent GeTrouveBot est autorisé à la récupérer. Imprime le
robots.txt, le crawl-delay éventuel et un verdict par URL. Ne récupère aucune
page de contenu et ne modifie rien.

Usage
─────
À lancer depuis la racine du dépôt : `python scripts/scraping/verifier_robots.py`.
Une URL du manifeste ressortant interdite justifie un STOP (pas de contournement).
"""

import csv
import urllib.request
from pathlib import Path
from urllib.robotparser import RobotFileParser

UA = "GeTrouveBot"
ROBOTS = "https://www.ge.ch/robots.txt"
MANIFESTE = Path("src/scraping/manifeste_sources_pilote.csv")


def charger_robots():
    """Récupère le robots.txt avec un en-tête identifiable et le renvoie en texte."""
    requete = urllib.request.Request(
        ROBOTS, headers={"User-Agent": "GeTrouveBot/0.1 (travail de bachelor HEG)"}
    )
    with urllib.request.urlopen(requete, timeout=20) as reponse:
        return reponse.read().decode("utf-8", errors="replace")


def main():
    """Imprime le robots.txt, le crawl-delay et le verdict par URL du manifeste."""
    contenu = charger_robots()
    print("=== robots.txt de www.ge.ch ===")
    print(contenu)
    print("=== fin robots.txt ===\n")

    rp = RobotFileParser()
    rp.parse(contenu.splitlines())
    print(f"crawl-delay pour {UA}  : {rp.crawl_delay(UA)}")
    print(f"request-rate pour {UA} : {rp.request_rate(UA)}\n")

    with open(MANIFESTE, encoding="utf-8") as fichier:
        lignes = list(csv.DictReader(fichier, delimiter=";"))
    print(f"{len(lignes)} URL du manifeste :")
    for ligne in lignes:
        autorise = rp.can_fetch(UA, ligne["url"])
        print(f"  [{'OK ' if autorise else 'NON'}] {ligne['url']}")


if __name__ == "__main__":
    main()
