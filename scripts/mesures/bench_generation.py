# scripts/mesures/bench_generation.py

"""
Mesure de génération LLM — débits et latences via Ollama
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Mesurer, sur l'API locale Ollama (/api/chat), la vitesse de génération des deux
modèles de langage (gemma4:12b, llama3.1:8b) : latence du premier jeton, débit
en jetons/s, durée de chargement à froid. Bibliothèque standard uniquement.
N'écrit rien : imprime des lignes de tableau à coller dans le journal des
mesures. Ne teste pas la qualité des réponses (température 0).
"""

import json
import os
import statistics
import time
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODELES = ["gemma4:12b", "llama3.1:8b"]
OPTIONS = {"temperature": 0, "seed": 42, "num_predict": 256, "num_ctx": 4096}

# Consigne courte, sans jeton <|think|> (mode direct, cf. chapitre 4).
SYSTEME = (
    "Tu es un assistant administratif pour les démarches du canton de Genève. "
    "Réponds de façon simple et factuelle, en français, à partir du contexte fourni."
)

# Contexte factice rédigé pour la mesure, jamais scrapé.
CONTEXTE = (
    "Contexte : les demandes de permis de séjour pour les personnes étrangères "
    "s'adressent à l'office cantonal de la population et des migrations. Le dossier "
    "comprend un formulaire de demande, une pièce d'identité valable, un justificatif "
    "de domicile et, selon la situation, un contrat de travail ou une attestation "
    "d'inscription. Le dépôt se fait au guichet de l'office, sur rendez-vous, ou par "
    "voie postale à l'adresse indiquée sur le formulaire. Une taxe est perçue au dépôt. "
    "Pour un renouvellement, la demande se dépose avant l'échéance du permis en cours. "
    "La commune de domicile peut orienter l'usager vers le service compétent."
)
QUESTION = "Où déposer ma demande de permis de séjour ?"


def generer(modele):
    """Lance une génération en flux et retourne les métriques de la requête."""
    corps = {
        "model": modele,
        "messages": [
            {"role": "system", "content": SYSTEME},
            {"role": "user", "content": CONTEXTE + "\n\n" + QUESTION},
        ],
        "stream": True,
        "think": False,  # mode direct : réflexion désactivée (chapitre 4)
        "options": OPTIONS,
    }
    requete = urllib.request.Request(
        OLLAMA_URL + "/api/chat",
        data=json.dumps(corps).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    debut = time.perf_counter()
    latence_premier = None
    dernier = {}
    with urllib.request.urlopen(requete) as reponse:
        for ligne in reponse:
            if not ligne.strip():
                continue
            bloc = json.loads(ligne)
            if latence_premier is None and bloc.get("message", {}).get("content"):
                latence_premier = time.perf_counter() - debut
            if bloc.get("done"):
                dernier = bloc
    jetons = dernier.get("eval_count", 0)
    duree_eval = dernier.get("eval_duration", 0) / 1e9
    return {
        "latence": latence_premier or 0.0,
        "jetons": jetons,
        "debit": jetons / duree_eval if duree_eval else 0.0,
        "chargement": dernier.get("load_duration", 0) / 1e9,
    }


def main():
    """Pour chaque modèle : 1 exécution à froid puis 3 à chaud, médiane des 3."""
    print("| Modele | Chargement a froid (s) | Latence 1er jeton (s) | Debit (jetons/s) | Jetons |")
    print("|---|---|---|---|---|")
    for modele in MODELES:
        froid = generer(modele)
        chauds = [generer(modele) for _ in range(3)]
        latence = statistics.median(c["latence"] for c in chauds)
        debit = statistics.median(c["debit"] for c in chauds)
        jetons = int(statistics.median(c["jetons"] for c in chauds))
        print(f"| {modele} | {froid['chargement']:.2f} | {latence:.2f} | {debit:.1f} | {jetons} |")


if __name__ == "__main__":
    main()
