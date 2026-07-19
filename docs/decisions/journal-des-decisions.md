# Journal des décisions techniques — Ge-Trouve

Ce fichier consigne les décisions techniques du projet, au fur et à mesure qu'elles sont arrêtées.
Chaque entrée précise sa date, ce qu'elle tranche, ses motifs, ce qui reste ouvert, et son lien avec
le mémoire. Une décision reste valable jusqu'à révision explicite, consignée à son tour ici.

Les décisions les plus récentes sont ajoutées en haut.

---

## 2026-07-15 — Modèle de langage (LLM) : Gemma 4 12B Instruct

**Décision.** Le modèle de langage retenu est **Gemma 4 12B Instruct**, servi en local via Ollama.
Le choix du modèle et celui du palier serveur sont **liés** : c'est une décision conjointe.

**Lien avec le mémoire.** Chapitre 4 (choix du LLM).

**Modèle et service.**
- Paquet Ollama : `gemma4:12b` (quantisation Q4_K_M, 7,6 Go, contexte 256K, licence Apache 2.0).
- Régime de service : mode direct. La réflexion (*thinking*) est **désactivée** via le jeton de contrôle
  documenté par l'éditeur.
- Repli documenté (si le palier plancher est retenu) : Llama 3.1 8B Instruct (`llama3.1:8b`, Q4_K_M, 4,9 Go).

**Serveur de production.** Infomaniak Serveur Cloud. Palier de confort : 6 CPU / 18 Go de RAM. Palier
plancher : 4 CPU / 12 Go, retenu comme scénario de repli. Rien n'est souscrit à ce stade ; souscription
prévue en août.

**Budget mémoire (hypothèses à confronter aux mesures réelles).**
- Postes fixes ≈ 6 Go : OS ~1,5 ; embeddings 0,5-1,5 ; base vectorielle <0,5 ; application ~1 ; réserve ~1,5.
- Enveloppe modèle : 5-6 Go au palier plancher, 10-11 Go au palier de confort.

**Souveraineté.** Inférence 100 % locale via Ollama (`http://localhost:11434`). Aucune donnée ni
document ne part vers un service externe à l'exécution.

**Ce qui reste ouvert.** Embeddings (chapitre 5) et base vectorielle (ChromaDB pressentie, chapitre 6)
non tranchés. Le code doit rester paramétrable pour échanger ces maillons sans réécriture.

**État.** Décision documentée. Rien n'est installé (ni Ollama, ni modèle, ni pipeline).

---

## 2026-07-14 — Framework d'orchestration RAG : Haystack 2.x

**Décision.** Le framework d'orchestration du pipeline RAG est **Haystack 2.x**.

**Lien avec le mémoire.** Décision actée en **section 3.4** (choix du framework RAG).

**Motifs.**
- Pipelines explicites, composant par composant : le câblage reste visible et défendable, ce qui sert
  directement l'objectif de transparence du travail.
- Licence Apache-2.0 (gouvernance ouverte).
- Intégrations Ollama et Chroma maintenues par l'éditeur (deepset).

**Mise en œuvre.**
- Paquets : `haystack-ai` (cœur 2.x), `ollama-haystack`, `chroma-haystack`.
- Versions **épinglées** dans `requirements.txt` dès la première installation. Aucune montée de version
  sans décision explicite de Daniel.
- Composants de référence : `OllamaTextEmbedder` / `OllamaDocumentEmbedder`, `OllamaGenerator` ou
  `OllamaChatGenerator`, `ChromaDocumentStore`, `ChromaEmbeddingRetriever`, `PromptBuilder`.
- Pipelines assemblés explicitement (`add_component` / `connect`), sans raccourci masquant le flux.

**Souveraineté.** Inférence 100 % locale via Ollama (`http://localhost:11434`). Aucune donnée ni
document ne part vers un service externe à l'exécution. Toute bibliothèque qui exigerait une clé d'API
externe doit être signalée avant usage.

**Ce qui reste ouvert (ne rien présumer dans le code).**
- **LLM** : chapitre 4 en cours. Mistral 7B via Ollama sert de modèle de travail provisoire pour le
  développement, ce n'est pas le choix final.
- **Embeddings** : chapitre 5, non traité.
- **Base vectorielle** : ChromaDB pressentie, décision au chapitre 6.

Le code doit rester paramétrable pour échanger ces maillons sans réécriture.

**Environnement.** Développement local Windows (Ryzen 7 7840HS, 32 Go de RAM, CPU uniquement, pas de
GPU supporté par Ollama ici). Cible de production : VPS Infomaniak Ubuntu, environ 12 Go de RAM.
Viser la sobriété à chaque choix.
