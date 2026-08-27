# Contrôle humain — évaluation Ge-Trouve (étape 6.4)

Échantillon d'un quart des questions (5 sur 20), tiré au hasard. À relire **à l'aveugle**, avant de regarder les scores RAGAS, puis à confronter à ces notes.

**Critères de verdict :**

- **Correcte** : les faits énoncés sont exacts par rapport aux pages du corpus.
- **Complète** : rien d'essentiel ne manque par rapport à la référence.
- **Sourcée** : les pages remontées correspondent au sujet de la question.
- **Bien orientée** : hors périmètre uniquement — avoue l'absence d'information et oriente vers le bon interlocuteur ; n/a sinon.
- **Rien d'inventé** : aucune affirmation absente des pages du corpus.

En cas de défaut, noter le point de défaillance de Barnett (liste en bas).

---

## Q01 — Comment demander la naturalisation suisse à Genève ?
*(avec_reponse, registre courant)*

**Réponse de référence**

> La demande de naturalisation ordinaire se dépose auprès de l'Office cantonal de la population et des migrations (OCPM), Service des naturalisations, par courrier ou via le formulaire de contact. Le dossier doit être accompagné de plusieurs pièces : un acte d'état civil suisse de moins de 6 mois, une copie du permis C, des attestations de l'administration fiscale, de l'office des poursuites et de l'Hospice général, ainsi qu'une attestation de connaissance du français de niveau B1 à l'oral et A2 à l'écrit selon les normes fide. La procédure comprend un test de connaissances. L'émolument est de CHF 850 pour les personnes majeures de moins de 25 ans et de CHF 1250 au-delà.

**Réponse du système**

> Pour demander la naturalisation ordinaire dans le canton de Genève, voici la démarche à suivre et les conditions à remplir :
>
> ### 1. Conditions de résidence
> Pour déposer une demande, vous devez remplir les conditions suivantes :
> *   Avoir séjouré **10 ans en Suisse** avec un permis valable (dont 3 ans au cours des 5 dernières années).
> *   Avoir séjouré **2 ans dans le canton de Genève** (dont les 12 derniers mois précédant la demande).
> *   Résider effectivement dans le canton de Genève pendant toute la durée de la procédure.
>
> *Note sur les permis :* Les permis B et C sont pris en compte intégralement. Pour le permis F, seule la moitié de la durée du séjour est comptabilisée. Le permis Ci est également pris en compte. Les permis L, N ou S ne sont pas pris en compte pour le calcul de la durée.
>
> ### 2. Procédure à suivre
> La démarche se déroule en trois étapes principales :
>
> **Étape 1 : Demander votre dossier**
> Vous devez envoyer une demande au Service des naturalisations de l'OCPM (Office cantonal de la population et des migrations) par courrier ou via leur formulaire de contact. Pour que votre requête soit examinée, vous devez joindre une **copie d'une pièce d'identité valable**. 
> Si les critères formels sont remplis, vous recevrez par poste le formulaire de demande de naturalisation ([voir exemple](https://www.ge.ch/node/2786)) ainsi que les formulaires spécifiques à votre situation et les explications nécessaires.
>
> **Étape 2 : Test des connaissances (si applicable)**
> Si vous êtes soumis à une session de test sur l'histoire, la géographie et les institutions suisses et genevoises, vous devez vous inscrire auprès du service naturalisations.
> *   **Inscription :** par téléphone au +41 22 546 46 20 (du lundi au vendredi entre 9h et 12h) ou via le formulaire de contact.
> *   **Préparation :** Vous pouvez utiliser le didacticiel en ligne ["Connaître la Suisse et Genève"](https://www.ge.ch/connaitre-suisse-geneve).
>
> **Étape 3 : Envoi du dossier complet**
> Une fois que vous avez réuni toutes les pièces, vous devez envoyer votre dossier complet par la poste.
>
> ### 3. Pièces à fournir (prérequis obligatoires)
> *   Un acte tiré du registre de l'état civil suisse datant de moins de 6 mois ;
> *   Une photocopie de votre autorisation d'établissement (permis C), dont le délai de contrôle n'est pas dépassé, ou un titre équivalent (comme le permis Ci), ainsi que tout autre document d'identité nécessaire ;
> *   2 photographies au format passeport ;
> *   Une attestation de l'administration fiscale cantonale datant de moins de 3 mois ;
> *   Une attestation de l'office cantonal des poursuites (ou de l'autorité compétente du lieu où vous avez résidé en Suisse durant les 5 dernières années) datant de moins de 3 mois.
>
> ### 4. Prestation de serment
> La procédure se termine par la prestation de serment, qui est obligatoire pour acquérir la nationalité suisse. Vous serez convié à une cérémonie organisée par le service naturalisations après le prononcé de l'arrêté de naturalisation du Conseil d'État.
>
> ### Contact
> **OCPM - Service naturalisations**
> Case postale 2753
> 1211 Genève 3
> Téléphone : +41 22 546 46 20 (du lundi au vendredi entre 9h et 12h)

**Pages remontées** (top-5, doublons retirés)

- https://www.ge.ch/devenir-suisse/naturalisation-ordinaire-depot-demande
- https://www.ge.ch/devenir-suisse/naturalisation-ordinaire-conditions-remplir

**Verdict** (à remplir)

| Correcte | Complète | Sourcée | Bien orientée | Rien d'inventé | Défaillance (n°) |
|---|---|---|---|---|---|
| oui | non | oui | n/a | non | 7 |

**Note libre :**
Le fond est exact : étapes de la procédure, conditions de résidence et coordonnées correspondent aux deux pages remontées. Mais la réponse est incomplète : la liste des pièces s'arrête à 5 éléments sur 9 (manquent notamment l'attestation de l'Hospice général, l'attestation de langue fide et celle du test de connaissances) et l'émolument n'est pas mentionné, alors que tout figure sur la page de dépôt —> d'où la défaillance n° 7. Une déformation relevée : le permis Ci est présenté comme équivalent du permis C dans les pièces à fournir, alors que les pages ne le citent que pour le calcul de la durée de séjour ; un titulaire de Ci croirait à tort pouvoir déposer sans permis C, d'où « rien d'inventé -> non ».

---

## Q05 — Comment obtenir un subside pour mon assurance-maladie ?
*(avec_reponse, registre courant)*

**Réponse de référence**

> Le subside est une aide financière pour payer les primes de l'assurance-maladie de base (LAMal), accordée selon le revenu et la situation familiale. Il est en principe versé automatiquement, sur la base du revenu, sans qu'il faille en faire la demande ; certaines catégories doivent toutefois déposer une demande (jeunes adultes, personnes imposées à la source, personnes récemment arrivées à Genève, personnes taxées d'office ou sans avis de taxation, changement de situation). Les demandes se font par correspondance ou en ligne auprès du Service de l'assurance-maladie (SAM). S'il est accordé, le subside est versé directement à l'assurance-maladie, qui le déduit des primes.

**Réponse du système**

> Pour obtenir un subside (aide financière) pour votre assurance-maladie, voici les informations utiles selon votre situation :
>
> ### Principe général
> Le subside est en principe accordé **automatiquement** sur la base de vos revenus. Si vous y avez droit, le montant est versé directement à votre assurance-maladie qui le déduit de vos primes. 
>
> Cependant, certaines catégories de personnes doivent obligatoirement déposer une demande :
> *   Les jeunes adultes (nés entre 2001 et 2007) ;
> *   Les personnes imposées à la source en 2024 ;
> *   Les personnes arrivées à Genève en 2025 ou en 2026 ;
> *   Les personnes n'ayant pas reçu leur avis de taxation 2024 ou ayant été taxées d'office en 2024 ;
> *   Les personnes dont la situation économique ou familiale a changé récemment.
>
> ### Démarches selon votre situation spécifique
>
> **1. Si vous avez des revenus bruts > 200'000.- ou une fortune brute > 250'000.- en 2024 :**
> *   **Quand :** Envoyez votre demande au Service de l’assurance-maladie (SAM) avant le **30 novembre 2026**.
> *   **Comment :** Vous devez écrire une lettre datée et signée indiquant que vous faites une demande de subside.
> *   **Envoi :** Envoyez cette lettre au SAM via ce lien : [Contacter le SAM](https://www.ge.ch/node/41062).
>
> **2. Si vous n'avez pas reçu votre avis de taxation 2024 ou si vous avez été taxé d'office en 2024 :**
> *   **Quand :** Envoyez votre dossier complet au SAM avant le **30 novembre 2026**. Si le retard de taxation persiste, vous pouvez écrire jusqu'au 31 décembre 2026 pour informer le SAM et conserver votre droit.
> *   **Comment :** Complétez, datez et signez le [Formulaire de demande](https://www.ge.ch/document/41256/telecharger) en joignant tous les justificatifs mentionnés dans celui-ci.
>
> **3. En cas de changement de situation économique ou familiale en 2026 :**
> *   **Quand :** Envoyez votre dossier complet au SAM avant le **30 novembre 2026**.
> *   **Comment :** Complétez, datez et signez le [Formulaire de demande](https://www.ge.ch/document/41853/telecharger) en joignant tous les justificatifs mentionnés dans celui-ci.
>
> ### Informations complémentaires
> *   **Suivi de la demande :** Vous pouvez suivre l'évolution de votre demande en ligne en vous connectant à votre compte e-démarches ([Mon EDM](https://espace-edemarches.app.ge.ch/)).
> *   **Personnes vivant en concubinage avec des enfants :** Les RDU 2026 sont additionnés pour déterminer le droit au subside du groupe familial. Un [Formulaire pour les personnes vivant en concubinage](https://www.ge.ch/document/41248/telecharger) est disponible.
> *   **Contact :** Pour toute information complémentaire ou pour transmettre vos demandes, consultez ce lien : [Contacter le SAM](https://www.ge.ch/node/41062). Le SAM ne reçoit du public que sur [rendez-vous](https://www.ge.ch/document/demande-rendez-vous-aupres-du-service-assurance-maladie).

**Pages remontées** (top-5, doublons retirés)

- https://www.ge.ch/demander-subside-assurance-maladie-2026
- https://www.ge.ch/informations-generales-subside-assurance-maladie
- https://www.ge.ch/demander-subside-assurance-maladie-2026/revenu-brut-sup-200-000-fortune-brute-sup-250-000
- https://www.ge.ch/demander-subside-assurance-maladie-2026/avis-taxation-2024-non-recu-taxation-office-2024
- https://www.ge.ch/demander-subside-assurance-maladie-2026/changement-situation-economique-familiale-2026

**Verdict** (à remplir)

| Correcte | Complète | Sourcée | Bien orientée | Rien d'inventé | Défaillance (n°) |
|---|---|---|---|---|---|
| oui | oui | oui | n/a | oui | - |

**Note libre :**
Réponse sans défaut : le principe (automatique, versé à l'assureur), les cinq catégories devant déposer une demande et les coordonnées du SAM correspondent aux pages. Les trois situations détaillées (seuils 200'000/250'000, avis de taxation non reçu, changement de situation) reprennent exactement les délais (30.11.2026, rattrapage 31.12.2026) et les numéros de formulaires (41256, 41853) des sous-pages remontées. Vérification par sondage sur les sous-pages du corpus : aucun écart. Le meilleur cas de l'échantillon.

---

## Q08 — Quelles démarches après une naissance à Genève ?
*(avec_reponse, registre courant)*

**Réponse de référence**

> En cas de naissance en milieu hospitalier, l'établissement ou la maison de naissance annonce directement la naissance à l'arrondissement de l'état civil compétent ; à la Maternité des HUG, l'enregistrement peut se faire auprès de l'antenne de l'état civil sur place. Si l'enfant naît à domicile, les parents doivent annoncer la naissance dans les trois jours à l'arrondissement de l'état civil du lieu de naissance, attestée par un médecin ou une sage-femme. L'état civil enregistre la naissance et transmet les informations pour la mise à jour du registre des habitants. Si l'enfant est étranger et les parents titulaires d'un titre de séjour, un rendez-vous est fixé pour ses données biométriques en vue de son permis de séjour.

**Réponse du système**

> Pour les démarches suite à une naissance à Genève, les étapes dépendent de la situation de l'enfant et de ses parents. Voici les informations contenues dans les extraits :
>
> ### Si votre enfant est né à l'étranger et vient se domicilier à Genève
> *   **Si l'un des parents est suisse :** Vous devez informer la représentation suisse à l'étranger de la naissance, puis procéder aux démarches d'[annonce d'arrivée à Genève](https://www.ge.ch/annoncer-mon-arrivee-ocpm/annonce-arrivee-geneve-suisses).
> *   **Si l'enfant est de nationalité étrangère :** Vous devez déposer une [demande de regroupement familial](https://www.ge.ch/demander-permis-sejour-ma-famille-regroupement-familial).
>
> ### Pour obtenir les documents d'identité de votre enfant
> Avant de pouvoir demander des documents d'identité, l'enfant doit être inscrit dans le registre des habitants du canton. 
> *   **Si l'enfant réside à Genève :** Dès réception de l'acte de naissance (ou de reconnaissance/certificat de famille), vous devez [annoncer la prise de résidence](https://www.ge.ch/annoncer-mon-arrivee-ocpm/annonce-arrivee-genee-suisses).
> *   **Si l'enfant réside à l'étranger :** La demande de documents d'identité doit être déposée auprès de la représentation suisse à l'étranger, en leur transmettant l'acte de naissance, de reconnaissance ou le certificat de famille.
>
> ### Démarches liées à l'installation dans le canton
> Si vous souhaitez installer votre enfant de manière permanente et durable à Genève, les démarches suivantes sont nécessaires :
> 1.  **Autorisation de séjour ou annonce auprès de l'OCPM :** 
>     *   Pour les ressortissants suisses : [annonce auprès de l'office cantonal de la population et des migrations](https://www.ge.ch/node/3538).
>     *   Pour les ressortissants de l'Union européenne : annonce à [l'OCPM](https://www.ge.ch/node/3538) dans les 3 mois suivant l'arrivée.
>     *   Pour les ressortissants d'États tiers (hors Union européenne) : annonce personnelle à [l'OCPM](https://www.ge.ch/node/3538) dans les 14 jours suivant l'arrivée.
> 2.  **Inscription à l'école :** Pour les enfants en âge de scolarité obligatoire (de 4 à 15 ans).
>     *   [Enfants de 4 à 11 ans](https://www.ge.ch/node/1737)
>     *   [Enfants de 12 à 15 ans](https://www.ge.ch/node/3045)
>     *   Note : Les jeunes de 16 à 18 ans ont [l'obligation d'être en formation](https://www.ge.ch/filieres-formation-enseignement-secondaire-ii).
>
> ### Informations complémentaires sur l'état civil
> Pour obtenir un acte de naissance enregistré par l'arrondissement de l'état civil de la Ville de Genève (pour les 110 dernières années) :
> *   **Jusqu'à 1899 :** Requête auprès des [Archives de la Ville de Genève](https://archives.geneve.ch/n/etat-civil-genealogie/n:112).
> *   **De 1900 à aujourd'hui :** Contactez le service de l'état civil par courriel ([etat-civil@geneve.ch](mailto:etat-civil@geneve.ch)) ou par courrier (37 Rue de la Mairie 1207 Genève).
> *   **Pièces requises pour cette démarche :** Une pièce d'identité scannée (max 5 Mo) et une adresse pour l'envoi. L'émolument est de CHF 30.- plus les frais de port.

**Pages remontées** (top-5, doublons retirés)

- https://www.ge.ch/naissance
- https://www.ge.ch/arriver-dans-canton-geneve-toutes-informations-pratiques
- https://www.geneve.ch/demarches/acte-naissance
- https://www.ge.ch/commander-documents-identite-suisses/reponses-aux-questions-frequentes

**Verdict** (à remplir)

| Correcte | Complète | Sourcée | Bien orientée | Rien d'inventé | Défaillance (n°) |
|---|---|---|---|---|---|
| oui | non | partiel | n/a | oui | 2, 4 (ou 3) |

**Note libre :**
Cas révélateur : aucune affirmation fausse, mais la réponse passe à côté de la question. Le cœur attendu (annonce par l'hôpital, délai de 3 jours à domicile, attestation médecin/sage-femme, biométrie du nouveau-né étranger) figure sur la page ge.ch/naissance, remontée en première position, et n'a pas été extrait — défaillance n° 4 (ou 3 si la section n'a pas atteint le contexte). À la place, le prototype a recopié fidèlement la liste des démarches d'installation destinée aux nouveaux arrivants (page « Bienvenue dans le canton »), remontée par proximité sémantique. S'y ajoute une défaillance de récupération : la page de l'antenne état civil des HUG n'apparaît pas dans le top-5 (n° 2). Vérification faite : les délais cités (UE 3 mois, États tiers 14 jours) sont exacts par rapport au corpus.

---

## Q14 — Quels sont les horaires et l'adresse de l'office cantonal de la population ?
*(avec_reponse, registre précis)*

**Réponse de référence**

> L'Office cantonal de la population et des migrations (OCPM) se situe route de Chancy 88, 1213 Onex (tél. +41 22 546 48 88). Les horaires de guichet ne figurent pas sur les pages consultées ; pour les connaître, il faut consulter ge.ch ou contacter l'office directement.

**Réponse du système**

> L'Office cantonal de la population et des migrations est situé à l'adresse suivante :
>
> Route de Chancy 88
> 1213 Onex
>
> Vous pouvez également le contacter par téléphone au +41 22 546 48 88.

**Pages remontées** (top-5, doublons retirés)

- https://www.geneve.ch/demarches/changement-adresse-canton-geneve
- https://www.ge.ch/exigences-preserver-qualite-zone-5-villa/se-renseigner-tout-complement-dossier
- https://www.ge.ch/agente-agent-detention-brevete-travailler-geneve/postuler-detention
- https://www.ge.ch/prestations-cas-incapacite-passagere-totale-partielle-travail-pcm
- https://www.ge.ch/obtenir-renseignements-personne-etablie-geneve

**Verdict** (à remplir)

| Correcte | Complète | Sourcée | Bien orientée | Rien d'inventé | Défaillance (n°) |
|---|---|---|---|---|---|
| oui | non | partiel | n/a | oui | 1 |

**Note libre :**
Adresse et téléphone exacts (route de Chancy 88, +41 22 546 48 88), tirés de la seule page pertinente du top-5. La moitié « horaires » de la question reste sans réponse : vérification faite sur les 5 pages remontées et leurs sous-pages, aucune ne contient les horaires de guichet de l'OCPM — contenu absent du contexte, défaillance n° 1, le comportement attendu étant de signaler cette absence plutôt que de se taire. Récupération très bruitée : 4 pages sur 5 hors sujet (zone villa, agents de détention, PCM, renseignements sur une personne), accrochées par le vocabulaire « office cantonal / horaires / guichet ». Point fort : ces pages contenaient les horaires d'autres offices (9h-12h, 14h-16h) et le modèle n'en a attribué aucun à l'OCPM — rien d'inventé malgré un contexte piégeux.

---

## Q17 — Comment calculer ma future rente AVS ?
*(hors_perimetre, registre courant)*

**Réponse de référence**

> Le calcul d'une future rente AVS ne relève pas du canton de Genève, mais de l'assurance-vieillesse et survivants (AVS), gérée au niveau fédéral. Le système ne dispose pas de cette information dans le corpus genevois et doit le reconnaître, en orientant la personne vers sa caisse de compensation AVS ou le portail ch.ch pour une estimation de rente.

**Réponse du système**

> Pour obtenir votre rente AVS (1er pilier), il est important de noter que celle-ci n'est pas versée automatiquement. Voici les informations relatives à cette démarche :
>
> **Démarche et délais**
> Vous devez déposer une demande écrite auprès de la **caisse de compensation** où vous avez versé vos dernières cotisations. Pour permettre à votre caisse de calculer votre rente en temps voulu, cette demande doit être déposée **au moins 3 mois avant** d'atteindre l'âge légal de la retraite (que celle-ci soit ordinaire, anticipée ou ajourée).
>
> **Identifier sa caisse de compensation**
> Si vous ne savez pas comment contacter votre caisse de compensation, le site web de la centrale de compensation peut vous aider à l'identifier.
>
> **Précisions sur les prestations complémentaires**
> Si vous avez besoin d'une estimation pour les prestations complémentaires (PC) AVS/AI, un [simulateur](https://www.ahv-iv.ch/fr/Assurances-sociales/Prestations-compl%C3%A9mentaires-PC/Calculateur-de-prestations-compl%C3%A9mentaires) de la Confédération permet d'effectuer un calcul indicatif des prestations fédérales auxquelles vous pourriez avoir droit.
>
> Pour obtenir des conseils ou une aide pour vos démarches, vous pouvez consulter la page : [Conseil et accompagnement administratif](https://www.ge.ch/node/37399/).

**Pages remontées** (top-5, doublons retirés)

- https://www.geneve.ch/demarches/demander-rente
- https://www.ge.ch/prestations-complementaires-avs/ai/documents-utiles
- https://www.ge.ch/impot-prevoyance-retraite-du-2e-3e-pilier/comment-deduire-cotisations-au-2e-3e-pilier
- https://www.ge.ch/dossier/geneve-au-service-seniors/preparer-sa-retraite/rentes-soutiens-financiers
- https://www.ge.ch/prestations-complementaires-avs/ai

**Verdict** (à remplir)

| Correcte | Complète | Sourcée | Bien orientée | Rien d'inventé | Défaillance (n°) |
|---|---|---|---|---|---|
| oui | non | n/a (hors corpus) | non | non | 1, 6 |

**Note libre :**
Le test du hors-périmètre échoue sur l'essentiel : le prototype n'avoue jamais que le calcul de la rente AVS ne relève pas du corpus genevois et répond à une autre question (« demander sa rente » au lieu de « calculer ») — défaillance n° 1, avec glissement de spécificité (n° 6). Le simulateur cité concerne les prestations complémentaires, pas la rente elle-même. L'orientation attendue est à moitié présente : la caisse de compensation est bien indiquée, mais sans lien avec un aveu d'absence. Les faits cités sont fidèles aux pages remontées, à une exception : la règle des « 3 mois avant l'âge légal » est généralisée aux retraites anticipée et ajournée, dont les délais, différents, figurent pourtant dans la même page — une fusion de passages voisins, trompeuse pour une retraite anticipée. Même mécanisme d'erreur qu'en Q01 (permis Ci).

---

## Rappel — les 7 points de défaillance (Barnett et al., Tableau 7.1)

1. Contenu absent (corpus) — la réponse n'existe pas dans les documents ; le système devrait dire qu'il ne sait pas.
2. Bons documents mal classés (récupération).
3. Perdus à l'assemblage (récupération).
4. Non extraite (génération) — la réponse est dans le contexte, le modèle ne l'en tire pas.
5. Mauvais format (génération).
6. Spécificité inadaptée (génération) — trop générale ou trop précise.
7. Incomplète (génération) — juste mais partielle.