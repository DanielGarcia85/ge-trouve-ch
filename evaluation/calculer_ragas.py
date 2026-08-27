# evaluation/calculer_ragas.py

"""
Calcul RAGAS — quatre métriques sur les traces du banc d'évaluation
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Lire les traces produites par le banc (resultats/evaluation/traces/), les mettre
au format RAGAS, et calculer les quatre métriques du chapitre 7 : précision du
contexte, rappel du contexte, fidélité et pertinence de la réponse. Écrit les
scores (par question et agrégés) dans resultats/evaluation/scores/.

Ce qu'il ne fait PAS : il n'interroge pas le pipeline de production (il travaille
sur les traces déjà produites), ne génère aucune réponse et ne modifie rien au
système évalué.

Câblage local (souveraineté)
────────────────────────────
Le juge et l'encodeur d'évaluation sont locaux, servis par Ollama, sans aucun
service externe. RAGAS exige un LLM de type BaseRagasLLM : on enveloppe donc les
composants LangChain-Ollama (ChatOllama, OllamaEmbeddings) dans les wrappers
LangChain de RAGAS. Le juge est Llama 3.1 8B, d'une autre famille que le rédacteur
Gemma (pas d'auto-jugement) ; les embeddings d'évaluation sont ceux de production
(Qwen3-Embedding-0.6B).

Périmètre
─────────
Les quatre métriques sont calculées sur les 20 questions, mais les agrégats sont
rapportés séparément pour les 16 questions avec réponse (où elles ont un sens) et
les 4 hors périmètre (les métriques RAGAS y sont peu parlantes : le contrôle humain
de l'étape 6.4 fait foi pour ces dernières).

"""

import json
import math
import sys
import tempfile
from pathlib import Path

# ── Accès à la configuration partagée (src/config.py) ─────────────────
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))
import config  # noqa: E402

import warnings  # noqa: E402

# RAGAS 0.4.3 est épinglé : on tait ses avertissements de dépréciation vers la v1.0
# (import des métriques, wrappers LangChain), sans objet sur une version figée.
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.cache import SQLiteCache  # noqa: E402
from langchain_core.globals import set_llm_cache  # noqa: E402
from langchain_ollama import ChatOllama, OllamaEmbeddings  # noqa: E402

from ragas import EvaluationDataset, RunConfig, evaluate  # noqa: E402
from ragas.embeddings import LangchainEmbeddingsWrapper  # noqa: E402
from ragas.llms import LangchainLLMWrapper  # noqa: E402
from ragas.metrics import (  # noqa: E402
    Faithfulness,
    LLMContextPrecisionWithoutReference,
    LLMContextRecall,
    ResponseRelevancy,
)

# ── Constantes ────────────────────────────────────────────────────────
# Juge d'une autre famille que le rédacteur (Gemma), pour écarter l'auto-jugement.
JUGE_MODELE = "llama3.1:8b"
# Contexte large pour le juge : les invites RAGAS (fidélité, rappel) concatènent la
# réponse et les extraits ; un contexte trop court les tronquerait.
JUGE_NUM_CTX = 8192

DOSSIER_TRACES = Path(config.RESULTATS_DIR) / "evaluation" / "traces"
DOSSIER_SCORES = Path(config.RESULTATS_DIR) / "evaluation" / "scores"


def construire_juge_et_embeddings():
    """
    Construit le juge et l'encodeur d'évaluation, locaux via Ollama.

    Le juge (Llama 3.1 8B) et l'encodeur (Qwen3-Embedding-0.6B) sont servis par
    Ollama (composants LangChain-Ollama) et enveloppés dans les wrappers LangChain
    de RAGAS, qui produisent les types BaseRagasLLM/BaseRagasEmbeddings attendus
    par evaluate.
    """
    juge = LangchainLLMWrapper(
        ChatOllama(
            model=JUGE_MODELE, base_url=config.OLLAMA_BASE_URL,
            temperature=0, num_ctx=JUGE_NUM_CTX,
        )
    )
    embeddings = LangchainEmbeddingsWrapper(
        OllamaEmbeddings(model=config.OLLAMA_EMBEDDING_MODEL, base_url=config.OLLAMA_BASE_URL)
    )
    return juge, embeddings


def charger_traces():
    """Charge les traces q01.json … q20.json, triées par identifiant."""
    fichiers = sorted(DOSSIER_TRACES.glob("q[0-9][0-9].json"))
    if not fichiers:
        raise FileNotFoundError(
            f"Aucune trace dans {DOSSIER_TRACES}. Lancer d'abord le banc (executer_banc.py)."
        )
    return [json.loads(f.read_text(encoding="utf-8")) for f in fichiers]


def construire_dataset(traces):
    """Met les traces au format RAGAS (un échantillon par question, ordre conservé)."""
    echantillons = []
    for t in traces:
        echantillons.append(
            {
                "user_input": t["question"],
                "response": t["reponse_systeme"],
                "retrieved_contexts": [f["contexte"] for f in t["fragments"]],
                "reference": t["reponse_reference"],
            }
        )
    return EvaluationDataset.from_list(echantillons)


def _moyenne(valeurs):
    """Moyenne en ignorant les valeurs manquantes (NaN) ; None si aucune valeur exploitable."""
    propres = [v for v in valeurs if isinstance(v, (int, float)) and not math.isnan(v)]
    return sum(propres) / len(propres) if propres else None


def _agreger(scores_par_question, metriques):
    """Agrège les scores par sous-ensemble (avec réponse / hors périmètre / global)."""
    sous_ensembles = {
        "avec_reponse": [s for s in scores_par_question if s["type"] == "avec_reponse"],
        "hors_perimetre": [s for s in scores_par_question if s["type"] == "hors_perimetre"],
        "global": scores_par_question,
    }
    agregats = {}
    for nom, lignes in sous_ensembles.items():
        agregats[nom] = {
            "nombre": len(lignes),
            "moyennes": {m: _moyenne([l["scores"].get(m) for l in lignes]) for m in metriques},
        }
    return agregats


def _ecrire_scores(traces, scores):
    """
    Construit les scores par question et les agrégats à partir des scores RAGAS, puis les écrit.

    Sauvegarde d'abord les scores par question (la donnée brute la plus précieuse), puis les
    agrégats : on ne perd rien même si une étape ultérieure échoue. Renvoie (noms des métriques,
    agrégats) pour le récapitulatif.
    """
    noms_metriques = sorted({cle for ligne in scores for cle in ligne})
    scores_par_question = []
    for trace, ligne in zip(traces, scores):
        scores_par_question.append(
            {
                "id": trace["id"],
                "type": trace["type"],
                "registre": trace["registre"],
                "theme": trace["theme"],
                "question": trace["question"],
                "scores": {m: ligne.get(m) for m in noms_metriques},
            }
        )

    DOSSIER_SCORES.mkdir(parents=True, exist_ok=True)
    (DOSSIER_SCORES / "scores_par_question.json").write_text(
        json.dumps(scores_par_question, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    agregats = _agreger(scores_par_question, noms_metriques)
    provenance = {
        "juge": JUGE_MODELE,
        "embeddings_evaluation": config.OLLAMA_EMBEDDING_MODEL,
        "metriques": noms_metriques,
        "nombre_questions": len(traces),
    }
    (DOSSIER_SCORES / "scores_agreges.json").write_text(
        json.dumps({"provenance": provenance, "agregats": agregats}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return noms_metriques, agregats


def main():
    """Calcule les quatre métriques RAGAS sur les traces et écrit les scores."""
    DOSSIER_SCORES.mkdir(parents=True, exist_ok=True)
    traces = charger_traces()
    dataset = construire_dataset(traces)
    juge, embeddings = construire_juge_et_embeddings()

    # Seul le rappel du contexte se mesure contre la référence (mémoire 7.4) ; la précision
    # du contexte est donc la variante « sans référence » (jugée sur la réponse produite).
    metriques = [
        LLMContextPrecisionWithoutReference(),
        LLMContextRecall(),
        Faithfulness(),
        ResponseRelevancy(),
    ]

    # Le juge (Llama sur CPU) répond en série : on limite RAGAS à un appel à la fois, sinon les
    # appels concurrents s'accumulent et dépassent le délai. Délai par appel allongé en conséquence.
    config_ragas = RunConfig(max_workers=1, timeout=900)

    # Cache des appels au juge (déterministe à température 0) : un ré-lancement réutilise les appels
    # déjà faits au lieu de tout recalculer. La base vit dans le dossier temporaire de la machine
    # (hors du dépôt et de OneDrive, pas de conflit de synchronisation pendant l'écriture).
    set_llm_cache(SQLiteCache(str(Path(tempfile.gettempdir()) / "ge-trouve-ragas-cache.sqlite")))

    print(f"Calcul RAGAS sur {len(traces)} questions (juge {JUGE_MODELE}, local)…")
    resultat = evaluate(
        dataset=dataset,
        metrics=metriques,
        llm=juge,
        embeddings=embeddings,
        run_config=config_ragas,
        raise_exceptions=False,  # une métrique en échec sur une ligne renvoie NaN, sans tout arrêter
        show_progress=True,
    )

    # resultat.scores : une liste de dictionnaires {nom_metrique: score}, alignée sur l'ordre du dataset.
    noms_metriques, agregats = _ecrire_scores(traces, resultat.scores)

    # Récapitulatif lisible en fin de run.
    print("\nMoyennes (avec réponse / hors périmètre / global) :")
    for m in noms_metriques:
        av = agregats["avec_reponse"]["moyennes"][m]
        hp = agregats["hors_perimetre"]["moyennes"][m]
        gl = agregats["global"]["moyennes"][m]
        fmt = lambda v: f"{v:.3f}" if isinstance(v, float) else "  -  "
        print(f"  {m:40s} {fmt(av)} / {fmt(hp)} / {fmt(gl)}")
    print(f"\nScores écrits dans {DOSSIER_SCORES}.")


if __name__ == "__main__":
    main()
