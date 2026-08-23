# src/pull_modeles.py

"""
Provisionnement des modèles Ollama — lecture de config.py
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Tirer dans le serveur Ollama les modèles déclarés par `config.py`
(`OLLAMA_GENERATION_MODEL` et `OLLAMA_EMBEDDING_MODEL`), au provisionnement.
Exécuté par le service one-shot `ollama-pull` du docker-compose, qui réutilise
l'image de l'application (elle contient ce script, `config.py` et le client
Ollama tiré par `ollama-haystack`). Ne construit pas l'index, ne sert aucune requête.

Source unique
─────────────
Les noms de modèles ne sont écrits qu'à un seul endroit, `config.py` : le pull et
l'application lisent la même valeur. Changer de modèle = une seule édition.

Idempotence
───────────
Tirer un modèle déjà présent et à jour ne retélécharge rien (simple vérification
du manifeste) ; le service peut donc se relancer à chaque déploiement sans coût.
"""

import sys
from pathlib import Path

import ollama

# Accès au module de configuration partagé (src/config.py).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402


def _statut(etape):
    """Extrait le champ « status » d'une étape de progression (objet typé ou dict)."""
    valeur = getattr(etape, "status", None)
    if valeur is None and isinstance(etape, dict):
        valeur = etape.get("status")
    return valeur


def tirer(client, modele):
    """Tire un modèle en affichant chaque changement d'état (progression lisible dans les logs)."""
    print(f"[pull] {modele}", flush=True)
    dernier = None
    for etape in client.pull(modele, stream=True):
        statut = _statut(etape)
        if statut and statut != dernier:
            print(f"  {statut}", flush=True)
            dernier = statut
    print(f"[ok] {modele}", flush=True)


def main():
    """Tire les modèles déclarés par config.MODELES_A_TIRER, puis rend la main."""
    client = ollama.Client(host=config.OLLAMA_BASE_URL)
    for modele in config.MODELES_A_TIRER:
        tirer(client, modele)


if __name__ == "__main__":
    main()
