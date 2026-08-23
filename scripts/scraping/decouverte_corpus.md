# Découverte du corpus : quelles pages scraper, et pourquoi

Ce document explique comment les pages à aspirer pour le corpus complet (étape 3) ont été déterminées,
comment refaire la démarche, et pourquoi certaines pages sont retenues et d'autres écartées. L'outil qui
met cette méthode en œuvre est [`decouvrir_sitemap.py`](decouvrir_sitemap.py), dans ce même dossier.

## Le problème

Un site comme `www.ge.ch` contient des dizaines de milliers de pages. Avant de scraper, il faut savoir
**quelles pages existent**, puis décider **lesquelles sont pertinentes** pour un assistant de démarches
administratives. Aspirer tout le site ramènerait surtout de l'actualité, des événements et des documents
sans rapport avec une démarche, ce qui dégraderait la qualité des réponses.

## La méthode, en trois temps

1. **Récupérer le sitemap du site.** Un *sitemap* est un fichier XML que le site publie lui-même pour
   lister ses pages (norme sitemaps.org, prévue à l'origine pour les moteurs de recherche). C'est la
   manière officielle et prévue d'énumérer un site. Le `robots.txt` de ge.ch l'annonce explicitement :
   `Sitemap: https://www.ge.ch/sitemap.xml`. Celui de ge.ch est un *index* qui pointe vers 14 sous-sitemaps
   paginés ; en les parcourant, on obtient la liste complète des URL.

2. **Classer les URL par catégorie.** Le premier segment du chemin de chaque URL (`document/…`,
   `actualite/…`, `demander-…`, `dossier/…`) sert de catégorie ; l'outil compte le nombre de pages par
   catégorie. Cela donne le paysage réel du site.

3. **Filtrer.** Les catégories substantielles (les démarches et les dossiers) sont gardées, le bruit est
   écarté (documents en vrac, actualité, événements, variantes de langue). Le résultat est la liste des
   pages à scraper.

## Les outils utilisés

Tout est en Python, avec la bibliothèque standard, rien d'exotique :

| Outil | Rôle |
|---|---|
| Le **sitemap** du site | savoir quelles pages existent |
| `urllib.request` | télécharger le sitemap (XML) |
| Expressions régulières (`re`) | extraire les URL des balises `<loc>…</loc>` |
| `collections.Counter` | regrouper et compter les URL par catégorie |

À noter ce que ce n'est **pas** : ce n'est pas *trafilatura* (qui sert plus tard à extraire le texte
d'une page une fois téléchargée), et ce n'est pas non plus le scraping lui-même. C'est une étape amont
de cadrage.

## Comment lancer l'outil

L'outil s'utilise en ligne de commande, sur n'importe quel domaine :

```
python scripts/scraping/decouvrir_sitemap.py <url_sitemap> [--garder seg1,seg2] [--sortie fichier.csv] [--ajouter]
```

- **`<url_sitemap>`** (obligatoire) : l'URL du sitemap du site à analyser. Elle se trouve dans le
  `robots.txt` du site (ligne `Sitemap:`) ou, à défaut, à l'emplacement standard `/sitemap.xml`. Pour
  ge.ch : `https://www.ge.ch/sitemap.xml` ; pour geneve.ch : `https://www.geneve.ch/sitemap.xml`.
- **`--garder`** (optionnel) : bascule le filtre en mode « ne garder que ». On indique un ou plusieurs
  premiers segments de chemin, séparés par des virgules (par exemple `--garder demarches`), et seules les
  pages de ces dossiers sont retenues. Sans cette option, le filtre par défaut s'applique : garder tout
  **sauf** le bruit connu (documents, actualité, événements, variantes de langue). Les deux modes existent
  parce que les sites ne rangent pas leurs démarches de la même façon (voir les deux exemples de sites
  plus bas).
- **`--sortie`** (optionnel) : si fourni, les URL retenues sont écrites dans ce fichier CSV (le manifeste).
  Sans cette option, l'outil se contente d'afficher l'analyse.
- **`--ajouter`** (optionnel) : ajoute les URL à un manifeste existant au lieu de l'écraser, sans réécrire
  l'entête. Sert à réunir plusieurs domaines (ge.ch puis geneve.ch) dans un seul fichier.

Exemples :

```
# 1. Analyser ge.ch (mode par défaut : écarter le bruit), sans rien écrire
python scripts/scraping/decouvrir_sitemap.py https://www.ge.ch/sitemap.xml

# 2. Analyser geneve.ch en ne gardant que le dossier /demarches/
python scripts/scraping/decouvrir_sitemap.py https://www.geneve.ch/sitemap.xml --garder demarches

# 3. Analyser ET écrire le manifeste des pages retenues
python scripts/scraping/decouvrir_sitemap.py https://www.ge.ch/sitemap.xml --sortie src/scraping/manifeste_sources.csv

# 4. Construire le manifeste complet du corpus (ge.ch, puis geneve.ch ajouté à la suite)
python scripts/scraping/decouvrir_sitemap.py https://www.ge.ch/sitemap.xml --sortie src/scraping/manifeste_sources.csv
python scripts/scraping/decouvrir_sitemap.py https://www.geneve.ch/sitemap.xml --garder demarches --sortie src/scraping/manifeste_sources.csv --ajouter
```

Pour un nouveau domaine, la marche à suivre est : lancer d'abord l'analyse **sans** `--sortie` pour voir sa
répartition par catégorie ; choisir le mode de filtrage selon cette répartition (écarter le bruit si les
démarches sont éparpillées, ou `--garder <dossier>` si elles sont regroupées dans un dossier propre) ; puis
relancer **avec** `--sortie` pour écrire le manifeste.

## Ce que le sitemap de ge.ch révèle

Le sitemap de ge.ch liste **27 484 pages**. La répartition est éclairante :

| Catégorie | Nombre | Nature |
|---|---|---|
| `document/*` | 17 362 | fiches, formulaires, PDF (63 % du site) |
| `actualite/*` | 3 608 | actualités datées |
| `evenement/*` | 1 478 | événements ponctuels |
| `dossier/*` | 1 196 | dossiers thématiques (regroupent des démarches) |
| `blog`, `organisation`, langues, `teaser` | ~1 100 | divers / institutionnel |
| démarches (verbes d'action : `demander`, `obtenir`, `annoncer`, `consulter`…) | ~1 300 | les procédures citoyennes |

Autrement dit, « toutes les démarches de ge.ch » ne représentent qu'une petite partie du site : le gros,
ce sont des documents et de l'actualité.

## Ce qui est gardé, ce qui est écarté, et pourquoi

**Gardé** (le substantiel citoyen) : les **pages de démarches** (les procédures « comment faire X »),
les **dossiers** thématiques et les **autres pages hors bruit**. Après filtrage, **4 072 pages**.

**Écarté** :
- `document/*` **en vrac** : 17 362 pages, en grande majorité sans rapport avec une démarche (vieux
  documents, rapports, PV). Elles ne sont pas aspirées en bloc ; en revanche, les formulaires et fiches
  **réellement liés depuis une démarche** seront pris en suivant les liens de ces pages. C'est là qu'est
  leur valeur, pas dans la masse.
- `actualite/*` et `evenement/*` : de l'information **datée** (« nouveau site 2016 », une séance publique),
  pas de l'information de démarche.
- `blog`, `teaser`, `organisation`, les variantes de langue (`en`, `pt-pt`…), et les pages Drupal sans
  alias (`node/12345`, ambigües).

**La raison de fond n'est ni la place ni le temps** (le projet en a) **mais la pertinence.** L'assistant
sert à répondre à des questions de démarches ; un corpus rempli d'actualités et de documents divers ferait
remonter du bruit dans la recherche et dégraderait les réponses. Un corpus focalisé sur les démarches est
plus utile et plus défendable.

## Ce que le sitemap de geneve.ch révèle

geneve.ch (la Ville de Genève) est rangé autrement que ge.ch. Son sitemap liste **31 218 pages**, mais
elles sont très majoritairement institutionnelles :

| Catégorie | Nombre | Nature |
|---|---|---|
| `autorites/*` | 21 251 | conseil municipal, procès-verbaux, annuaire du personnel (68 % du site) |
| `themes/*` | 4 487 | contenu éditorial (culture, bibliothèques…) |
| `actualites/*` | 1 790 | actualités datées |
| `agenda/*` | 894 | événements |
| **`demarches/*`** | **250** | **les démarches citoyennes** |
| longue traîne (crèches, écoles, parcs, restaurants…) | ~2 500 | lieux et équipements de la Ville |

Ici, contrairement à ge.ch, les démarches sont **toutes regroupées dans un dossier propre `/demarches/`**.
Le filtre par défaut (écarter le bruit) ne conviendrait pas, puisqu'il garderait aussi les 21 251 pages
institutionnelles. On utilise donc le mode « ne garder que » avec `--garder demarches`, qui retient
exactement les **250 pages** de démarches et écarte tout le reste (institutionnel, actualité, agenda,
annuaire, équipements). C'est l'usage prévu de l'option `--garder`.

## Le périmètre retenu

Le corpus est **cantonal genevois**. Sont retenus :
- **`ge.ch`** : les ~4 072 pages de démarches et dossiers, plus les documents liés ;
- **`geneve.ch`** : les **250** pages du dossier `/demarches/` (Ville de Genève).

**Rien d'autre n'est ajouté à ce stade** : le catalogue de ge.ch couvre déjà un très large éventail
(impôts, emploi, état civil, santé, permis, agriculture…). Les autres communes, les assurances sociales
ou la législation (`silgeneve.ch`) restent des **extensions possibles**, à activer seulement si
l'évaluation (Partie 3) révèle un manque. Le corpus n'est pas gonflé avant d'avoir mesuré.

## Le scraping restera responsable

La découverte ne fait que lire les sitemaps. Le scraping proprement dit (étape suivante) respecte
`robots.txt` domaine par domaine, s'annonce avec l'agent `GeTrouveBot`, et attend **2 secondes** entre
deux requêtes. Aucun `crawl-delay` n'est imposé par ge.ch : ce délai est un choix de politesse envers
les serveurs officiels.

## Où cette étape se place dans le pipeline

- **`robots.txt`** : ce qui est autorisé.
- **sitemap** : quelles pages existent (cette étape).
- **`urllib`** : télécharger.
- **trafilatura** : extraire le texte principal d'une page.
- **Qwen + Chroma** : découper, encoder, indexer.
