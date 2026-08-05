# Journal des mesures — Ge-Trouve

Chaque session de mesure est datée, rattachée à un poste et reproductible : script versionné,
paramètres consignés. Seules des valeurs mesurées figurent ici, jamais des estimations.
Ce journal alimentera l'annexe B du mémoire (mesures datées).

---

## 2026-08-06 — Environnement local et premières mesures — poste DANIELGARCIA

**Poste.** DANIELGARCIA · AMD Ryzen 7 7840HS (iGPU Radeon 780M) · 27,7 Go de RAM disponibles
(32 Go installés, ~4 Go réservés à l'iGPU) · Windows 11 Pro (10.0.26200) · secteur.

**Versions.** Python 3.13.2 · Ollama 0.32.5 · haystack-ai 3.0.0 · ollama-haystack 6.8.0 ·
chroma-haystack 4.4.0.

Modèles installés (Ollama) :

| Rôle | Tag | ID | Quantisation | Contexte | Taille disque |
|---|---|---|---|---|---|
| LLM rédacteur | `gemma4:12b` | `4eb23ef187e2` | Q4_K_M | 262 144 | 7,6 Go |
| Juge / repli | `llama3.1:8b` | `46e0c10c039e` | Q4_K_M | 131 072 | 4,9 Go |
| Embeddings | `qwen3-embedding:0.6b` | `ac6da0dfba84` | Q8_0 | 32 768 | 639 Mo |

**Protocole.** À compléter lors des relevés (scripts `scripts/mesures/`, paramètres de l'annexe B).

| Grandeur | Valeur | Unité | Méthode |
|---|---|---|---|
| *(à remplir lors des mesures)* |  |  |  |

**Observations.** RAM disponible 27,7 Go et non 32 (iGPU Radeon 780M réserve ~4 Go). Inférence CPU
(iGPU non supporté par Ollama sous Windows).
