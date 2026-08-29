# evaluation/executer_banc.py

"""
Banc d'évaluation — exécution du pipeline de production sur le jeu d'auteur
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Poser les 20 questions du jeu d'évaluation (evaluation/jeu_evaluation.py) au
pipeline de production figé (src/repondre.py), une passe par question, et
archiver pour chacune : la question, la réponse du système, les fragments
remontés (rang, URL, contenu), la latence, et la réponse de référence associée.
Les traces vont dans resultats/evaluation/traces/ (un fichier JSON par question)
pour le contrôle humain (étape 6.4) et l'entrée du calcul RAGAS (etape 6.2).

Ce qu'il ne fait PAS : il ne calcule aucune métrique (c'est le rôle du script
RAGAS), ne modifie pas le pipeline (il le réutilise tel quel via
construire_pipeline) et n'introduit aucune consigne ni réglage nouveaux.

Étanchéité et régime
────────────────────
Lancer ce script EST le run officiel de l'évaluation (étape 6.3) : exécuter
sur la machine de développement au repos. Le système évalué est
le système déployé, figé : consigne active (V5), régime de production (OPTIONS),
top_k 5, sans seed (une seule passe par question, comme en production). Aucune
relance sélective : en cas d'échec technique, relancer la question à l'identique
et le consigner.
"""

import json
import sys
import time
from pathlib import Path

# ── Accès au code du pipeline (src/) et au jeu (dossier courant) ───────
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))          # pour importer repondre et config
sys.path.insert(0, str(Path(__file__).resolve().parent))  # pour importer jeu_evaluation

import config  # noqa: E402
import repondre  # noqa: E402
from jeu_evaluation import QUESTIONS  # noqa: E402

# ── Destination des traces (versionnées) ──────────────────────────────
DOSSIER_TRACES = Path(config.RESULTATS_DIR) / "evaluation" / "traces"


def _fragments_serialisables(documents):
    """Transforme les documents Haystack remontés en dictionnaires archivables."""
    fragments = []
    for rang, doc in enumerate(documents, start=1):
        fragments.append(
            {
                "rang": rang,
                "url": doc.meta.get("url"),
                # Contexte tel que le modèle l'a vu : version avec liens si présente,
                # sinon le contenu nettoyé. C'est ce texte qui servira de contexte à RAGAS.
                "contexte": doc.meta.get("texte_liens") or doc.content,
            }
        )
    return fragments


def _interroger(pipe, question):
    """Pose une question au pipeline et renvoie (réponse, fragments, latence en secondes)."""
    # La requête est préfixée par la consigne de tâche Qwen ; la question brute sert au prompt.
    requete_instruite = f"Instruct: {repondre.TACHE}\nQuery:{question}"
    depart = time.perf_counter()
    resultat = pipe.run(
        {"embedder": {"text": requete_instruite}, "prompt_builder": {"question": question}},
        include_outputs_from={"retriever"},
    )
    latence = time.perf_counter() - depart
    reponse = resultat["generator"]["replies"][0]
    fragments = resultat["retriever"]["documents"]
    return reponse, fragments, latence


def main():
    """Exécute le banc sur les 20 questions et archive une trace JSON par question."""
    DOSSIER_TRACES.mkdir(parents=True, exist_ok=True)

    # Le pipeline est construit une seule fois, dans son régime de production (consigne active
    # et OPTIONS par défaut, sans seed) : ni consigne ni régime d'échantillonnage ne sont
    # surchargés. Seul le délai d'attente client est relevé (garde réseau pour la génération CPU
    # longue, surtout au chargement à froid), sans modifier repondre.py ni le système évalué.
    config.TIMEOUT_GENERATION = 1200
    pipe = repondre.construire_pipeline()

    # Trace de provenance du run (régime exact appliqué à toutes les questions).
    provenance = {
        "modele_generation": config.OLLAMA_GENERATION_MODEL,
        "modele_embeddings": config.OLLAMA_EMBEDDING_MODEL,
        "top_k": config.TOP_K,
        "options": config.OPTIONS_GENERATION,
        "tache_embedding": repondre.TACHE,
        "nombre_questions": len(QUESTIONS),
    }
    (DOSSIER_TRACES / "run_info.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total = len(QUESTIONS)
    latence_totale = 0.0
    for indice, q in enumerate(QUESTIONS, start=1):
        question = q["question"]
        print(f"[{indice}/{total}] q{q['id']:02d} — {question}")
        reponse, fragments, latence = _interroger(pipe, question)
        latence_totale += latence

        trace = {
            "id": q["id"],
            "question": question,
            "type": q["type"],
            "registre": q["registre"],
            "collectivite": q["collectivite"],
            "theme": q["theme"],
            "reponse_reference": q["reponse_reference"],
            "pages_sources_reference": q["pages_sources"],
            "reponse_systeme": reponse.text,
            "latence_s": round(latence, 2),
            # Contrôle permanent du mode direct : la réflexion doit rester vide (think=False).
            "reflexion": reponse.reasoning,
            "fragments": _fragments_serialisables(fragments),
        }
        chemin = DOSSIER_TRACES / f"q{q['id']:02d}.json"
        chemin.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"        {latence:6.1f} s · {len(fragments)} fragments · trace: {chemin.name}")

    print(
        f"\nTermine : {total} questions, {latence_totale:.0f} s au total "
        f"(~{latence_totale / total:.0f} s/question). Traces dans {DOSSIER_TRACES}."
    )


if __name__ == "__main__":
    main()
