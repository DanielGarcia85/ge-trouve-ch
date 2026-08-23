# Journal des mesures — Ge-Trouve

Chaque session de mesure est datée, rattachée à un poste et reproductible : script versionné,
paramètres consignés. Seules des valeurs mesurées figurent ici, jamais des estimations.
Ce journal alimentera l'Annexe 2 du mémoire (mesures datées).

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

---

## 2026-08-06 et 07 — Étape 1, pipeline pilote (permis de séjour)

Premier pipeline complet, de bout en bout, sur un périmètre pilote (pages `www.ge.ch` du permis de
séjour), du scraping à la réponse sourcée. Deux natures de résultats se distinguent, et c'est ce qui
structure cette session : les **artefacts** (corpus scrapé, index Chroma, réponse) sont **indépendants
de la machine** et produits une seule fois ; les **mesures de performance** (latence, RAM, débit)
**dépendent du matériel** et sont donc relevées sur les **deux postes**, DANIELGARCIA (32 Go, DDR5) et
GARCIAD (16 Go, DDR4, meilleur proxy du VPS). Déroulé : manifeste et robots.txt le 06.08 ; scraping le
06.08 et indexation le 07.08 ; mesures du pipeline sur les deux postes le 07.08. OneDrive suspendu
pendant les exécutions.

**Vérification robots.txt (`www.ge.ch`), préalable au scraping.** Contrôle propre au site, indépendant
de la machine.

- `robots.txt` récupéré avec l'agent `GeTrouveBot`. Seul groupe présent : `User-agent: *` (nous concerne).
- Les **23 URL du manifeste** (12 de départ, plus 11 sous-pages ajoutées après inspection des 6 pages
  chapeau) sont **autorisées** (`can_fetch` = OK pour chacune).
- Règles `Disallow` du site (`/core/`, `/profiles/`, `/admin/`, `/search/`, `/user/*`, `/node/add/`,
  `/comment/reply/`, `/taxonomy/term/*/impression`, `/statusDB.php`, `README.txt`, `web.config`) :
  aucune ne touche les pages de démarches (URL propres `demander-permis-…`, `renouveler-…`, `arriver-…`).
- Aucun `crawl-delay` ni `request-rate` déclaré : on applique notre propre délai de politesse ≥ 2 s.
- `Sitemap: https://www.ge.ch/sitemap.xml`.
- Conditions d'utilisation : non contredites par le robots.txt ; le périmètre se limite à des pages
  publiques de démarches, pour un usage académique non commercial (revue formelle des CGU à compléter si besoin).

Verdict : **feu vert** pour les 23 URL du manifeste, délai ≥ 2 s, agent identifiable.

**Corpus scrapé (1.3).** Artefact indépendant de la machine (aspiré sur DANIELGARCIA).

- **23 pages sur 23, aucun échec** (HTTP 200 partout, y compris les URL `ue/aele`).
- Textes extraits (`HTMLToDocument` / trafilatura) de 556 à 7 379 caractères : les pages « hub » sont
  brèves (surtout des liens), les pages de cas plus denses.
- Durée ≈ 51 s, **dominée par le délai de politesse** (2 s × 22 intervalles) ; le temps de requête et
  d'extraction ne pèse que ~7 s au total. C'est ce délai, pas le matériel, qui fixera le temps à l'échelle
  du corpus complet.
- Sortie : un JSON par page dans `data/pilote/pages/` (corpus brut, non versionné), plus le journal
  `resultats/pilote/journal_scraping_pilote.md` (versionné).

**Index Chroma (1.4).** Artefact indépendant de la machine (construit sur DANIELGARCIA).

- 23 pages découpées en **72 fragments** (par mots, 200 par fragment, recouvrement 40) ; base vérifiée à
  72 fragments (politique overwrite, ré-exécution idempotente, IDs = hash du contenu).
- Embeddings Qwen (documents sans consigne), **dimension 1024** (conforme). Métadonnées par fragment :
  `url`, `titre`, `section`, `date_capture`, `position`.
- Base persistante ≈ 2,7 Mo sur disque (`data/chroma/`, non versionné).
- Débit d'indexation (mesure dépendante du matériel, DANIELGARCIA) : **0,8 fragment/s** ; sous le bench de
  l'étape 0 (1,2 docs/s), du fait de fragments plus longs (200 mots contre ~150-180) et du chargement à
  froid de Qwen inclus dans la durée (~92 s au total).

**Réponse générée (1.5).** Comportement du pipeline, indépendant de la machine.

- **Mode direct confirmé** : `reasoning` vide dans la réponse, donc `think:false` bien effectif.
- **Qualité** (réponse archivée dans `resultats/pilote/reponse_pilote.md`) : correcte et sourcée (dépôt auprès
  de l'OCPM, en ligne ou par courrier), mais **incomplète** (ni lien en ligne ni adresse). Cause : ces
  détails ne sont pas dans le corpus, les hyperliens étant retirés par l'extraction (trafilatura garde la
  prose), et le service en ligne (e-démarches) comme les formulaires (PDF) étant hors périmètre pilote.
  Le modèle n'a rien inventé : fidélité au contexte respectée. Constat pour l'étape 3 (préserver les liens
  à l'ingestion, élargir le corpus) et l'étape 2 (consigne).

**Mesures du pipeline sur les deux postes (1.6).** Question type « Où déposer ma demande de permis de
séjour ? », `bench_pipeline.py`, conditions contrôlées, une exécution à froid puis trois à chaud (médiane).

| Grandeur | DANIELGARCIA (32 Go, DDR5) | GARCIAD (16 Go, DDR4) |
|---|---|---|
| Latence à chaud (médiane) | **8,1 s** (8,3 / 8,1 / 8,0) | **7,8 s** (8,5 / 7,8 / 7,7) |
| dont génération (25 jetons) | 4,8 s | 6,8 s |
| dont encodage requête + recherche | ~3,3 s | ~1,0 s |
| Latence à froid | 73 s (Gemma 13,7 s) | 88 s (Gemma 40 s) |
| RAM système sous pipeline | 22,4 / 32 Go (VS Code inclus) | 15,4 / 16 Go, 0,3 Go libre |

Empreinte des modèles **identique sur les deux postes** : Gemma 8,9 + Qwen 2,4 = **11,3 Go** (`ollama ps`) ;
processus Python/Chroma ~92 Mo.

- **Latences à chaud quasi égales (~8 s), mais réparties à l'inverse** : DANIELGARCIA décode vite (DDR5) et
  prépare lentement ; GARCIAD prépare vite (CPU de bureau) et décode lentement (DDR4). Sur une réponse
  courte, les deux effets se compensent. Confirme le constat de l'étape 0.
- **À froid, GARCIAD paie cher le chargement** (Gemma 40 s contre 13,7) : charger 11,3 Go de modèles sur
  16 Go force une forte pagination.
- **Dimensionnement du VPS verrouillé** : sur GARCIAD le pipeline tient tout juste (0,3 Go libre), donc le
  palier plancher 12 Go est exclu, 16 Go est un plancher extrême, et le palier de confort 18 Go (sur VPS
  épuré, sans les ~1,6 Go de VS Code) donne la marge nécessaire.

---

## 2026-08-10 et 11 — Étape 2, mise au point de la consigne de génération

Objet : régler la consigne système de génération (variante V3 retenue, voir le journal des décisions) et,
au passage, le régime d'échantillonnage de production. Essais sur DANIELGARCIA (10.08, variantes V0/V1/V2)
puis GARCIAD (11.08, V0/V3). Le détail des réponses est archivé dans le dépôt (versionné)
(`resultats/consignes/comparaison_consignes_*.md`).

**Régime d'échantillonnage, constats.**

- Régime « recommandé par l'éditeur » (température 1.0, top_p 0.95, top_k 64) : sur CPU, Gemma déroule
  jusqu'au plafond de jetons. Réponses de 400 à 500 jetons, **100 à 160 s chacune**, certaines dépassant
  300 s. Trop lent et trop bavard pour un assistant réactif.
- Température abaissée à **0.3** : réponses quasi reproductibles, ce qui permet de comparer les variantes
  à conditions égales (seed fixé pour les essais). Le plafond `num_predict` 256 coupait certaines réponses
  en pleine phrase ; porté à 512 pour les essais, puis à **1024 en production** (les réponses complètes de
  V3 dépassent parfois 512).
- `num_predict` est un plafond, pas une cible : à température basse, le modèle s'arrête de lui-même quand
  il a fini. Le relever ne pénalise pas les réponses courtes ; seule la longueur réelle de la réponse coûte
  du temps.

**Latences des essais V0/V3 (GARCIAD, 11.08, température 0.3, `num_predict` 512).** En secondes, par question.

| Question | V0 | V3 |
|---|---|---|
| Q1 | échec (>300 s) | 273,1 |
| Q2 | 203,3 | 262,0 |
| Q3 | 145,4 | 204,6 |
| Q4 | 129,9 | 290,3 |
| Q5 | 57,5 | 184,9 |
| Q6 | 114,6 | 218,0 |
| Q7 | 82,1 | 134,5 |
| Q8 | 156,3 | 110,0 |
| **médiane** | **137,6** | **211,3** |

- V3 plus lente que V0 : réponses plus complètes, donc plus de jetons à décoder. Cohérent avec l'arbitrage
  complétude / latence assumé au choix de la consigne.
- **Chiffres non fiables comme référence** : throttling thermique probable après ~40 min de génération
  continue sur garciad, et une génération V0 (Q1) coupée par le garde-fou de 300 s. Le premier run (10.08)
  avait de plus été faussé par une mise en veille nocturne (deux réponses en échec, latences aberrantes de
  plusieurs heures). Une latence propre du régime de production sera relevée séparément sur DANIELGARCIA.

**Latence propre sur DANIELGARCIA (11.08), machine au repos.** La mesure fiable annoncée ci-dessus.

- *Régime de production* (`bench_pipeline.py`, `num_predict` 1024, sans seed), sur la phrase-exemple « Où
  déposer ma demande de permis de séjour ? » (réponse V3 courte, 107 jetons) : latence à froid **110,6 s**
  (chargements Qwen et Gemma inclus) ; à chaud **42,8 s** de médiane (42,8 / 43,3 / 26,8), dont **23,0 s**
  de génération et ~19,8 s d'encodage plus recherche.
- *Régime des essais* (`comparer_consignes.py`, V3 seul, `num_predict` 512, seed 42), sur les 8 questions
  de mise au point (réponses souvent longues) : **médiane 147,4 s** (de 88,1 s pour une réponse courte à
  208,2 s pour une réponse détaillée).
- **Les deux chiffres ne se comparent pas** : le premier porte sur une question à réponse courte, le second
  sur des questions à réponses complètes et plus longues. La leçon rejoint celle de garciad : la latence
  d'une réponse V3 **suit sa longueur**, de quelques dizaines de secondes (réponse brève) à près de trois
  minutes (réponse détaillée) sur ce CPU.
- **RAM du pipeline chargé** : 26,2 / 27,7 Go utilisée, 1,5 Go libre ; empreinte Gemma 8,9 + Qwen 2,4 =
  **11,3 Go** (`ollama ps`), identique aux relevés précédents. `reponse_pilote.md` est régénérée en
  V3/production ; elle remplace l'ancienne réponse V0 de l'étape 1 (dont la description datée reste un
  constat d'époque).

**Ancrage vérifié à la source.** Les détails les plus spécifiques produits par V3 (SEFRI, délai « 6 à
8 semaines », permis Ci et carte de légitimation DFAE, pays à accord d'établissement, personnel académique)
ont été **retrouvés dans les pages sources correspondantes** du corpus pilote (recherche plein texte sur
`data/pilote/pages/`). V3 n'invente pas : sa richesse vient des extraits. Constat central pour la fidélité
(chapitre 7).

---

## 2026-08-13 — Indexation du corpus complet — poste DANIELGARCIA

**Poste.** DANIELGARCIA · AMD Ryzen 7 7840HS · secteur, mise en veille désactivée
(`powercfg /change standby-timeout-ac 0`). OneDrive suspendu pendant l'écriture de la base.

**Objet.** Indexation du corpus complet (4304 pages ge.ch + geneve.ch ; voir
`resultats/complet/journal_scraping.md`) via `indexer_complet.py` : découpage 200 mots / recouvrement 40,
embeddings Qwen (documents sans consigne), encodage et écriture par lots de 50 pages, reconstruction propre
de la base de production `data/chroma/`.

**Résultats.**

| Grandeur | Valeur |
|---|---|
| Pages indexées | 4304 |
| Fragments | 9651 (2,24 par page) |
| Débit d'encodage | 0,8 fragment/s |
| Taille base Chroma | 190,9 Mo |
| Dimension des vecteurs | 1024 |

- Métadonnées par fragment : `url`, `titre`, `date_capture`, `position` (pas de `section`, contrairement au
  pilote : le corpus complet ne la porte pas ; le titre est extrait de chaque page au scraping).
- **9651 fragments conformes au décompte déterministe** (découpage seul, sans encodage) : aucun doublon,
  rien de manquant. Débit **0,8 fragment/s**, identique à l'index pilote (même modèle, même CPU).

**Interruption et reprise (fait notable).** La première passe s'est arrêtée à **2750/4304 pages** (6146
fragments écrits) : le poste s'est mis en veille, la requête à Ollama a expiré (`ReadTimeout`). Après
désactivation de la veille, reprise avec l'option `--reprise` : les 2750 URL déjà indexées ont été sautées,
les **1554 pages restantes** traitées en **70,5 min**. Durées mesurées : **124,4 min** pour la première
passe (2750 pages), **70,5 min** pour la reprise (1554 pages), soit ~195 min de calcul effectif. La base
finale (9651 fragments) est identique à ce qu'aurait produit une passe unique : les IDs Chroma étant des
empreintes du contenu, la reprise n'introduit aucun doublon.

**Contrôle qualitatif.** Question type « Où déposer ma demande de permis de séjour ? » via
`repondre.py` sur le corpus complet : réponse fondée et sourcée, **plus complète que sur le pilote**
(elle couvre l'arrivée d'un autre canton, la recherche d'emploi, le regroupement familial et l'asile,
toutes présentes dans le corpus élargi), avec liens officiels cités **dont un lien vers une fiche document**
(`ge.ch/document/aide-pratique-…`). Cela valide en situation la préservation des liens décidée à l'étape 3 :
l'assistant pointe vers un document sans que la page document ait été scrapée. Mode direct confirmé
(réflexion vide).

---

## 2026-08-23 — Étape 4, latence de l'interface (streaming) sous consigne V5 — postes GARCIAD et DANIELGARCIA

**Objet.** Latence du pipeline de production (`repondre.py`, consigne **V5**, régime de production, top_k 5)
sur la question type « Où déposer ma demande de permis de séjour ? », dans les **deux modes** de
`bench_pipeline.py` : **appel direct** (réponse d'un bloc, équivalent de la mesure préalable prévue à
l'étape 4.2) et **`--streaming`** (appel comme l'app, qui relève en plus le **temps jusqu'au premier mot**,
la latence perçue). Une passe à froid, trois à chaud (médiane). Départ à froid garanti par un `ollama stop`
des deux modèles avant chaque exécution ; Streamlit fermé.

**Postes** (deux machines de développement, pour situer les ordres de grandeur ; **ni l'une ni l'autre ne
représente le VPS cible**, un Ubuntu épuré et dédié, alors que ces postes tournent sous Windows avec d'autres
logiciels : les chiffres de production réels seront relevés sur le VPS à l'étape 5).
- GARCIAD · Intel Core i7-12700 · 16 Go DDR4 · Windows 10.
- DANIELGARCIA · AMD Ryzen 7 7840HS · 32 Go DDR5 · Windows 11.

**Résultats à chaud (médiane sur 3 ; production = modèles résidents).**

| Grandeur | GARCIAD direct | GARCIAD streaming | DANIELGARCIA direct | DANIELGARCIA streaming |
|---|---|---|---|---|
| Temps jusqu'au premier mot | n/a | **1,0 s** | n/a | **3,5 s** |
| Temps total | 132,3 s | 124,7 s | 87,1 s | 80,2 s |
| dont génération (eval Ollama) | 131,2 s / 455 jetons | 123,7 s / 428 jetons | 75,3 s / 365 jetons | 73,2 s / 353 jetons |
| encodage requête + recherche (reste) | ~1,1 s | ~1,0 s | ~11,9 s | ~7,1 s |

**Résultats à froid (chargement des modèles ; n'arrive qu'au démarrage du VPS).**

| Grandeur | GARCIAD direct | GARCIAD streaming | DANIELGARCIA direct | DANIELGARCIA streaming |
|---|---|---|---|---|
| Temps jusqu'au premier mot | n/a | 86,6 s | n/a | 103,4 s |
| Temps total | 221,4 s / 388 jetons | 237,9 s / 521 jetons | 179,3 s / 352 jetons | 175,4 s / 348 jetons |

**RAM du pipeline chargé** (système entier, pipeline résident ; modèles = Gemma 8,9 + Qwen 2,4 = 11,3 Go, 100 % CPU) :
- GARCIAD : 13,8 Go utilisés, **1,9 Go libres** sur 16 (plancher extrême).
- DANIELGARCIA : ~23 Go utilisés, **4-5 Go libres** sur 27,7 (confortable).

**Constats.**
- **Le streaming n'ajoute aucun surcoût de calcul** : à chaud, le temps total est le même en appel direct et
  en streaming (l'écart, 132 vs 125 s sur garciad, vient du nombre de jetons, non-déterministe sans seed). Ce
  que le streaming apporte, c'est la **latence perçue** : le premier mot en **1 à 3,5 s selon le poste**
  (garciad ~1 s, DANIELGARCIA ~3,5 s), alors que la réponse complète met ~2 min à s'écrire. C'est la
  justification de la décision de streaming de l'étape 4.
- **Latence de calcul vs latence perçue** : à bien distinguer. Le calcul (temps total) est inchangé par le
  streaming ; seule la perception change, l'usager lit dès le premier mot.
- **Débit borné par le matériel** : DANIELGARCIA (Ryzen, DDR5) génère nettement plus vite (eval 75 s contre
  131 s sur garciad), ce qui confirme que la latence est dans la génération et dépend du CPU et de la bande
  passante mémoire.
- **Anomalie assumée sur DANIELGARCIA** : le « reste » (encodage + recherche + traitement du prompt) et le
  premier mot y sont plus élevés (premier mot 3,5 s ; reste 7-12 s) que sur garciad (~1 s), alors que la
  machine est plus rapide en génération. La base Chroma et la requête étant identiques, ce n'est pas la
  recherche qui est réellement plus lente ; l'explication probable est une activité de fond pendant la mesure
  (synchronisation OneDrive et cache disque récents) ou une contention mémoire liée à l'iGPU. Non surinterprété.
- **RAM** : les modèles tiennent partout (11,3 Go). garciad confirme que 16 Go est un plancher extrême (1,9 Go
  libres) ; le palier de confort 18 Go du VPS est le bon choix.
- **À froid** : 66 à 103 s avant le premier mot (chargement de Gemma et Qwen). Sur le VPS, en gardant les
  modèles résidents (`keep_alive`), cela n'arrive qu'au démarrage ; le service tourne ensuite au régime à chaud.
  À prévoir en étape 5 (déploiement) pour garantir l'expérience « premier mot en ~1 s ».
- **Effet de la consigne V5** : réponses plus courtes (~350-455 jetons à chaud) qu'en V4 (735 jetons lors des
  essais antérieurs), la liste « Sources » ayant été retirée (redondante avec la barre latérale de l'interface).

**Captures de l'interface** : `resultats/interface/capture_repos.PNG` (au repos) et
`resultats/interface/capture_reponse.PNG` (avec une réponse).
