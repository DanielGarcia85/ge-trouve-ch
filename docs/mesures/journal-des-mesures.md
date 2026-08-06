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

**Protocole.**

- *Génération* (`bench_generation.py`) : API `/api/chat` en flux, `think:false` (mode direct),
  température 0, seed 42, `num_predict` 256, `num_ctx` 4096. Une passe à froid, puis trois à chaud
  (médiane). Consigne système, contexte fictif et question type « Où déposer ma demande de permis de séjour ? ».
- *Embeddings* (`bench_embeddings.py`) : via Haystack (`OllamaTextEmbedder` / `OllamaDocumentEmbedder`).
  Latence de requête = médiane sur 10 encodages ; débit d'indexation sur 100 documents (12 paragraphes cyclés).
- *RAM* (`releve_ram.ps1`) : `Get-CimInstance` + `ollama ps`, un relevé par état. Un modèle isolé via `ollama stop`.

**Génération (LLM).**

| Modèle | Chargement à froid | Latence 1er jeton | Débit | Jetons |
|---|---|---|---|---|
| `gemma4:12b` | 14,3 s | 3,2 s | 5,6 jetons/s | 57 |
| `llama3.1:8b` | 8,8 s | 2,5 s | 9,3 jetons/s | 63 |

**Embeddings (`qwen3-embedding:0.6b`).**

| Grandeur | Valeur |
|---|---|
| Latence d'encodage d'une requête | 245 ms (médiane sur 10) |
| Débit d'indexation | 1,2 docs/s (100 documents en 85,5 s) |
| Dimension des vecteurs | 1024 |

**RAM par état.** Empreinte = colonne SIZE de `ollama ps`.

| État | RAM utilisée | RAM libre | Empreinte |
|---|---|---|---|
| Repos (aucun modèle) | 11,2 Go | 16,5 Go | — |
| Gemma seul | 19,8 Go | 7,9 Go | 8,9 Go |
| Llama seul | 15,7 Go | 12,0 Go | 5,6 Go |
| Gemma + Llama | 24,8 Go | 2,9 Go | 8,9 + 5,6 Go |
| Qwen (Llama encore résident) | 17,1 Go | 10,6 Go | 2,4 Go (Qwen) |

**Observations.**

- RAM disponible 27,7 Go et non 32 (iGPU Radeon 780M réserve ~4 Go). Inférence CPU (iGPU non supporté
  par Ollama sous Windows).
- Gemma « pense » par défaut : le mode direct exige `think:false` dans l'appel API. En ligne de commande
  (`ollama run`), la réflexion reste active. Sans effet sur la RAM, mais elle allonge la latence et
  consomme des jetons (constaté au chapitre 4).
- Les deux LLM chargés simultanément saturent la machine (2,9 Go libres). En production, un seul LLM est
  servi : ce cas ne se présente que par recouvrement du keep-alive Ollama (déchargement après ~5 min d'inactivité).
- Budget de production : Gemma (8,9 Go) + Qwen (2,4 Go) ≈ 11,3 Go pour les deux modèles. Tient au palier
  de confort 18 Go avec l'OS, Chroma et l'application ; au palier plancher 12 Go, la bascule sur Llama
  (5,6 Go) redevient nécessaire. La mesure appuie l'arbitrage conjoint modèle/palier du chapitre 4.

---

## 2026-08-06 — Environnement local et premières mesures — poste GARCIAD

**Poste.** CD-CZC31679VJ · Intel Core i7-12700 · 16 Go de RAM (15,7 Go disponibles) · Windows 10
Entreprise LTSC (10.0.19044) · secteur. Second poste du projet, servant de contrepoint à DANIELGARCIA :
moins de RAM (16 Go contre 32) et une autre mémoire vive (DDR4 contre DDR5), donc plus proche des paliers
du VPS.

**Versions.** Python 3.13.1 · Ollama 0.32.6 · haystack-ai 3.0.0 · ollama-haystack 6.8.0 ·
chroma-haystack 4.4.0. Modèles identiques à la session DANIELGARCIA (mêmes ID : `gemma4:12b`
`4eb23ef187e2`, `llama3.1:8b` `46e0c10c039e`, `qwen3-embedding:0.6b` `ac6da0dfba84`).

**Protocole.** Identique à la session DANIELGARCIA, à une adaptation près : `bench_generation.py` décharge
désormais chaque modèle après ses passes (`keep_alive:0`), pour ne jamais cumuler deux LLM en RAM (sur
16 Go, Gemma + Llama saturerait). Sans effet sur une machine large.

**Génération (LLM).**

| Modèle | Chargement à froid | Latence 1er jeton | Débit | Jetons |
|---|---|---|---|---|
| `gemma4:12b` | 22,5 s | 1,2 s | 3,8 jetons/s | 58 |
| `llama3.1:8b` | 7,8 s | 0,5 s | 6,0 jetons/s | 52 |

**Embeddings (`qwen3-embedding:0.6b`).**

| Grandeur | Valeur |
|---|---|
| Latence d'encodage d'une requête | 191 ms (médiane sur 10) |
| Débit d'indexation | 1,1 docs/s (100 documents en 93,8 s) |
| Dimension des vecteurs | 1024 |

**RAM par état.** Empreinte = colonne SIZE de `ollama ps`. Chaque modèle mesuré isolé (déchargement des
autres au préalable).

| État | RAM utilisée | RAM libre | Empreinte |
|---|---|---|---|
| Repos (aucun modèle) | 8,7 Go | 7,0 Go | — |
| Gemma seul | 14,3 Go | 1,4 Go | 8,9 Go |
| Llama seul | 11,9 Go | 3,8 Go | 5,6 Go |
| Qwen seul | 8,4 Go | 7,3 Go | 2,4 Go |

**Observations.**

- Base au repos élevée (8,7 Go) : Windows Entreprise et ses agents. Ce n'est pas représentatif d'un VPS
  Ubuntu épuré (~2 Go au repos) ; garciad illustre le pire cas côté système.
- Préparation contre décodage : garciad produit le 1ᵉʳ jeton plus vite (CPU de bureau plus musclé), mais
  décode plus lentement, à ~65 % du débit de DANIELGARCIA. Le décodage CPU est borné par la bande passante
  mémoire (DDR4 ici, DDR5 là) ; le ratio est uniforme sur les deux modèles (0,68 et 0,65), donc c'est bien
  la bande passante, pas un défaut de mémoire (swap).
- Gemma à la limite sur 16 Go : chargement à froid allongé (22,5 s contre 14,3 s à cause de la pagination
  au chargement) et 1,4 Go libre une fois chargé. Gemma + Qwen ne tiendrait pas sur cette machine chargée ;
  Llama + Qwen (≈ 14 Go) tiendrait. Illustration concrète des deux paliers du chapitre 4.
- Empreintes identiques à DANIELGARCIA (Gemma 8,9 Go, Llama 5,6 Go, Qwen 2,4 Go) : reproductibles,
  indépendantes de la machine. Qwen a ici été mesuré isolé, ce qui confirme ses 2,4 Go chargés, au-dessus
  de l'hypothèse 0,5-1,5 Go du chapitre 4 (poste embeddings à réviser).
