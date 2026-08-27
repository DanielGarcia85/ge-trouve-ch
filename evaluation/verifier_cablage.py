# evaluation/verifier_cablage.py

"""
Vérification du câblage RAGAS — juge et embeddings locaux (Ollama)
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Confirmer, avant le run officiel, que la chaîne d'évaluation tourne : RAGAS
installé, câblage LangChain-Ollama en place, juge et encodeur qui répondent via
Ollama, et les quatre métriques qui produisent un score. Sert de test de fumée ;
ne fait pas partie du run.

Étanchéité
──────────
Utilise un échantillon BIDON (une question générale, sans rapport avec le corpus
genevois ni le jeu d'évaluation). Les questions d'évaluation ne passent jamais ici :
elles ne sont posées qu'au run officiel (étape 6.3).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # pour importer calculer_ragas

from calculer_ragas import construire_juge_et_embeddings  # noqa: E402

from ragas import EvaluationDataset, evaluate  # noqa: E402
from ragas.metrics import (  # noqa: E402
    Faithfulness,
    LLMContextPrecisionWithoutReference,
    LLMContextRecall,
    ResponseRelevancy,
)

# Échantillon bidon, volontairement hors sujet (aucun lien avec le corpus ni le jeu).
ECHANTILLON_BIDON = {
    "user_input": "Quelle est la capitale de la France ?",
    "response": "La capitale de la France est Paris.",
    "retrieved_contexts": ["Paris est la capitale et la plus grande ville de la France."],
    "reference": "Paris est la capitale de la France.",
}


def main():
    """Lance les quatre métriques sur un unique échantillon bidon et affiche les scores."""
    juge, embeddings = construire_juge_et_embeddings()
    dataset = EvaluationDataset.from_list([ECHANTILLON_BIDON])
    metriques = [
        LLMContextPrecisionWithoutReference(),
        LLMContextRecall(),
        Faithfulness(),
        ResponseRelevancy(),
    ]
    print("Test de câblage (échantillon bidon, juge local)…")
    resultat = evaluate(
        dataset=dataset, metrics=metriques, llm=juge, embeddings=embeddings,
        raise_exceptions=True, show_progress=False,
    )
    print("Scores obtenus :", resultat.scores[0])
    print("Câblage OK : la chaîne RAGAS -> LangChain -> Ollama répond.")


if __name__ == "__main__":
    main()
