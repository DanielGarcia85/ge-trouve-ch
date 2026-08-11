# scripts/mesures/bench_pipeline.py

"""
Mesure du pipeline de réponse pilote — latence et RAM
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Mesurer la latence de bout en bout du pipeline de réponse (étape 1.5) sur la
question type : une exécution à froid puis trois à chaud, médiane. Lit le détail
de génération dans la métadonnée Ollama (chargement, évaluation, jetons). Archive
la réponse et ses fragments pour le mémoire. Relève enfin la RAM du pipeline
chargé (Qwen, Gemma et Chroma résidents) via `releve_ram.ps1`, exécuté tant que
ce processus est vivant. Réutilise le pipeline de `repondre_pilote`, sans le
redéfinir.
"""

import statistics
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))
import config  # noqa: E402
import repondre_pilote as rp  # noqa: E402

RELEVE_RAM = RACINE / "scripts" / "mesures" / "releve_ram.ps1"
ARCHIVE = config.RESULTATS_DIR / "pilote" / "reponse_pilote.md"


def une_execution(pipe, question, requete_instruite):
    """Exécute le pipeline une fois et renvoie (latence totale, réponse, fragments)."""
    debut = time.perf_counter()
    resultat = pipe.run(
        {"embedder": {"text": requete_instruite}, "prompt_builder": {"question": question}},
        include_outputs_from={"retriever"},
    )
    total = time.perf_counter() - debut
    reply = resultat["generator"]["replies"][0]
    documents = resultat["retriever"]["documents"]
    return total, reply, documents


def archiver(question, reply, documents):
    """Écrit la réponse et ses fragments dans un fichier (matière pour le mémoire)."""
    lignes = [f"# Réponse pilote — {question}", "", "## Réponse", "", reply.text, "", "## Fragments utilisés", ""]
    for doc in documents:
        lignes.append(f"- {doc.meta.get('url')}")
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def main():
    """Mesure la latence, archive la réponse, puis relève la RAM du pipeline chargé."""
    pipe = rp.construire_pipeline()
    question = rp.QUESTION_DEFAUT
    requete_instruite = f"Instruct: {rp.TACHE}\nQuery:{question}"

    print("Mesure de latence (1 à froid, 3 à chaud)...")
    froid, reply_froid, _ = une_execution(pipe, question, requete_instruite)
    chauds = [une_execution(pipe, question, requete_instruite) for _ in range(3)]

    latences_chaud = [c[0] for c in chauds]
    latence_chaud = statistics.median(latences_chaud)
    reply, documents = chauds[-1][1], chauds[-1][2]

    meta = reply.meta
    eval_s = meta.get("eval_duration", 0) / 1e9
    jetons = meta.get("usage", {}).get("completion_tokens", 0)
    charge_froid_s = reply_froid.meta.get("load_duration", 0) / 1e9
    reste_chaud = max(latence_chaud - eval_s, 0.0)

    detail_chaud = ", ".join(f"{lat:.1f}" for lat in latences_chaud)
    print(f"\nLatence à froid          : {froid:.1f} s (chargements à froid de Qwen et Gemma inclus)")
    print(f"Latence à chaud (3 passes): {detail_chaud} s")
    print(f"Latence à chaud (médiane): {latence_chaud:.1f} s")
    print(f"  génération (eval Ollama): {eval_s:.1f} s pour {jetons} jetons")
    print(f"  encodage requête + recherche (reste): ~{reste_chaud:.1f} s")
    print(f"Chargement à froid de Gemma (métadonnée): {charge_froid_s:.1f} s")

    archiver(question, reply, documents)
    print(f"\nRéponse archivée : {ARCHIVE}")

    print("\n=== RAM du pipeline chargé (Qwen + Gemma + Chroma résidents) ===")
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RELEVE_RAM)]
    )


if __name__ == "__main__":
    main()
