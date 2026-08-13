# scripts/mesures/comparer_consignes.py

"""
Comparaison des variantes de consigne — étape 2
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Exécuter chaque question de mise au point avec chaque variante de consigne, à un
régime d'échantillonnage modéré (seed fixé pour comparer à conditions égales),
archiver les réponses et les latences (dans `resultats/`, versionné), et imprimer
un récapitulatif des latences. Sert à trancher la consigne (grille de lecture remplie
à la main sur l'archive). Réutilise le pipeline de `repondre`.

Régime d'échantillonnage
────────────────────────
On s'écarte du régime « recommandé par l'éditeur » (température 1.0, top_p 0.95,
top_k 64) : à température 1.0 sur CPU, Gemma déroule jusqu'au plafond de jetons, ce
qui donne des réponses longues et lentes (100 à 160 s), à rebours de la comparaison
qu'on veut mener. On abaisse donc la température à 0.3 : réponses quasi
reproductibles, comparables à conditions égales. Le plafond de jetons (`num_predict`)
est fixé à 512 et sert de marge, pas de cible : à température basse, le modèle
s'arrête de lui-même quand il a fini ; un plafond trop bas (256 aux premiers essais)
coupait certaines réponses en pleine phrase. Le régime de production reste tranché à
la clôture de l'étape (2.5).

Note
────
La recherche ne dépend pas de la consigne (seule la génération en dépend) : les
fragments récupérés sont donc identiques d'une variante à l'autre pour une même
question. L'archive les affiche une fois par question.
"""

import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))
import config  # noqa: E402
import repondre as rp  # noqa: E402
from generation.consignes import VARIANTES  # noqa: E402
from generation.questions_mise_au_point_pilote import QUESTIONS  # noqa: E402

ARCHIVE_DIR = config.RESULTATS_DIR / "consignes"

# Variantes rejouées à ce tour : les clés à jouer, puisées dans le catalogue unique
# `VARIANTES` (consignes.py). V1 et V2 ne sont pas rejouées : leur comportement est déjà
# connu, et la brièveté qu'elles poussent a été écartée. Pour rejouer d'autres variantes,
# ajouter leur clé ici.
A_ESSAYER = ["V3"]

# Archive datée et étiquetée par les variantes jouées : chaque run crée son propre fichier,
# aucun n'écrase le précédent (traçabilité).
ARCHIVE = ARCHIVE_DIR / f"comparaison_consignes_{'-'.join(A_ESSAYER).lower()}_{datetime.now():%Y-%m-%d_%H%M}.md"

# Régime modéré : température basse (comparaison à conditions égales) et plafond de
# jetons servant de marge (voir docstring), seed fixé pour comparer les variantes.
OPTIONS_ESSAI = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 64,
    "seed": 42,
    "num_predict": 512,
    "num_ctx": 4096,
}


def une_reponse(pipe, question):
    """Exécute le pipeline sur une question ; renvoie (réponse, latence, URLs des fragments)."""
    instruite = f"Instruct: {rp.TACHE}\nQuery:{question}"
    debut = time.perf_counter()
    resultat = pipe.run(
        {"embedder": {"text": instruite}, "prompt_builder": {"question": question}},
        include_outputs_from={"retriever"},
    )
    latence = time.perf_counter() - debut
    reponse = resultat["generator"]["replies"][0].text
    urls = [doc.meta.get("url") for doc in resultat["retriever"]["documents"]]
    return reponse, latence, urls


def ecrire_archive(resultats):
    """Écrit l'archive lisible, groupée par question, pour remplir la grille à la main."""
    lignes = [
        "# Comparaison des consignes — étape 2",
        "",
        f"Variantes : {', '.join(A_ESSAYER)}",
        f"Échantillonnage : {OPTIONS_ESSAI}",
        "",
    ]
    for indice, question in enumerate(QUESTIONS):
        lignes += [f"## Q{indice + 1} ({question['origine']}) — {question['texte']}", ""]
        # Les fragments ne dépendent pas de la consigne ; on prend ceux d'une variante qui a
        # abouti (la 1re variante peut avoir échoué avant de les capturer).
        urls = next((resultats[(indice, nom)]["urls"] for nom in A_ESSAYER if resultats[(indice, nom)]["urls"]), [])
        lignes += ["Fragments : " + ", ".join(urls), ""]
        for nom in A_ESSAYER:
            resultat = resultats[(indice, nom)]
            lignes += [f"**{nom}** ({resultat['latence']:.1f} s) : {resultat['reponse']}", ""]
    ARCHIVE.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def imprimer_recap(resultats):
    """Imprime le tableau des latences (question par variante) et la médiane par variante."""
    print("\n=== Latences (s) ===")
    print("Question".ljust(9) + "".join(nom.rjust(8) for nom in A_ESSAYER))
    for indice in range(len(QUESTIONS)):
        ligne = f"Q{indice + 1}".ljust(9) + "".join(f"{resultats[(indice, nom)]['latence']:8.1f}" for nom in A_ESSAYER)
        print(ligne)
    medianes = "médiane".ljust(9) + "".join(
        f"{statistics.median([resultats[(i, nom)]['latence'] for i in range(len(QUESTIONS))]):8.1f}" for nom in A_ESSAYER
    )
    print(medianes)
    print(f"\nArchive complète (réponses) : {ARCHIVE}")


def main():
    """Essaie chaque variante sur les 8 questions, archive et récapitule."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    resultats = {}
    for nom in A_ESSAYER:
        pipe = rp.construire_pipeline(consigne=VARIANTES[nom], options=OPTIONS_ESSAI)
        print(f"\n=== Variante {nom} ===")
        for indice, question in enumerate(QUESTIONS):
            debut = time.perf_counter()
            try:
                reponse, latence, urls = une_reponse(pipe, question["texte"])
                etat = f"{latence:5.1f} s"
            except Exception as erreur:  # un timeout ou une panne ne doit pas arrêter tout le run
                latence = time.perf_counter() - debut
                reponse, urls = f"[échec : {type(erreur).__name__}]", []
                etat = f"ÉCHEC après {latence:5.1f} s ({type(erreur).__name__})"
            resultats[(indice, nom)] = {"reponse": reponse, "latence": latence, "urls": urls}
            print(f"  Q{indice + 1} ({question['origine']:>11}) : {etat}")

    ecrire_archive(resultats)
    imprimer_recap(resultats)


if __name__ == "__main__":
    main()
