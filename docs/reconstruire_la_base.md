# Reconstruire le corpus et la base vectorielle

Le dossier `data/` (corpus brut scrapé et base Chroma) **n'est pas versionné** : il est
**régénérable** à partir du pipeline. La reproductibilité du projet repose sur ces scripts et
sur le **manifeste des sources** (versionné), pas sur les fichiers bruts. Ce document décrit la
marche à suivre pour reconstruire `data/` depuis zéro.

## Reconstruire ou copier ?

Deux situations distinctes :

- **Déploiement courant** : on **copie** une base déjà construite (rapide, environ deux minutes) au
  lieu de la reconstruire. C'est le choix par défaut sur le VPS, exactement comme les modèles Ollama
  sont tirés une seule fois. Voir la section « Note déploiement » en fin de document.
- **Reconstruction depuis zéro** (ce guide) : pour repartir d'une machine neuve sans base existante,
  ou pour **rafraîchir le corpus** (pages ge.ch modifiées).

Attention : re-scraper aujourd'hui peut produire une base **différente** de celle mesurée et évaluée,
car les pages officielles évoluent. Pour garder la base qui correspond aux mesures et à l'évaluation,
il faut la **copier**, pas la reconstruire.

## Prérequis

- venv Python 3.13 avec `requirements.txt` installé.
- Ollama lancé, avec le modèle d'embeddings `qwen3-embedding:0.6b` (indispensable à l'indexation).
  Pour tester la réponse à la fin, `gemma4:12b` est également nécessaire.
- Accès Internet (scraping de `ge.ch` et `geneve.ch`).
- Se placer à la racine du dépôt.

## Étapes

### 1. (optionnel) Régénérer le manifeste des sources

Le manifeste `src/scraping/manifeste_sources.csv` est **versionné** : il est déjà présent. Ne refaire
cette étape que pour rafraîchir la liste des URL. Un passage par domaine :

```
python scripts/scraping/decouvrir_sitemap.py https://www.ge.ch/sitemap.xml --sortie src/scraping/manifeste_sources.csv
python scripts/scraping/decouvrir_sitemap.py https://www.geneve.ch/sitemap.xml --garder demarches --sortie src/scraping/manifeste_sources.csv --ajouter
```

`ge.ch` est traité en mode par défaut (on écarte le bruit connu) ; `geneve.ch` en ne gardant que le
dossier `/demarches/`, ajouté au même fichier. La méthode est détaillée dans
`scripts/scraping/decouverte_corpus.md`.

Contrôle facultatif de `robots.txt` (le scraper le refait de toute façon) :

```
python scripts/scraping/verifier_robots.py
```

### 2. Scraper le corpus

Télécharge les pages du manifeste vers `data/pages/complet/` (un fichier JSON par page). Délai poli
d'au moins deux secondes, `robots.txt` vérifié par domaine (un refus arrête le scraping, aucun
contournement), titre extrait de chaque page, reprise automatique (une page déjà scrapée est sautée),
journal résumé dans `resultats/complet/`.

```
python src/scraping/scrape_complet.py
```

Durée : plusieurs dizaines de minutes (plus de 4000 pages, délai poli entre chaque).

### 3. Indexer

Découpe le corpus en fragments, les encode avec Qwen, puis écrit dans Chroma (`data/chroma/`) avec les
métadonnées par fragment (`url`, `titre`, `date_capture`, `position`). Les liens vers les PDF et
documents sont conservés dans le texte (leur contenu n'est pas indexé à ce stade). Encodage par lots
avec reprise.

```
python src/indexing/indexer_complet.py
```

En cas d'interruption, reprendre là où l'indexation s'était arrêtée :

```
python src/indexing/indexer_complet.py --reprise
```

Durée : plusieurs dizaines de minutes sur CPU (encodage de milliers de fragments).

### 4. Vérifier

```
python src/repondre.py "Où déposer ma demande de permis de séjour ?"
```

La commande doit renvoyer une réponse fondée sur les extraits, avec des fragments issus de
`ge.ch` / `geneve.ch`.

## Résultat

- `data/pages/complet/` : le corpus brut (un JSON par page).
- `data/chroma/` : la base vectorielle (`chroma.sqlite3` et un dossier de segment), environ 191 Mo.

## Note déploiement (VPS)

En production, la base n'est **pas** reconstruite à chaque déploiement. Elle est **copiée une fois**
sur le VPS, dans `/mnt/data/chroma`, exactement comme les modèles Ollama sont tirés une fois. Copier
garantit que la base servie en ligne est **identique** à celle qui a été mesurée et évaluée. La
reconstruction décrite ci-dessus reste la **garantie de reproductibilité** : le pipeline et le
manifeste versionné suffisent à tout régénérer.

Transfert typique depuis un poste disposant de la base :

```
scp -r -i <cle_ssh> data/chroma/* <utilisateur>@<ip_vps>:/mnt/data/chroma/
```

Le dossier cible `/mnt/data/chroma` doit exister et appartenir à l'utilisateur de déploiement, dont
l'UID est aligné avec celui du conteneur (voir `deploy/Dockerfile`), afin que le conteneur puisse lire
et écrire la base sans retouche de permissions.
