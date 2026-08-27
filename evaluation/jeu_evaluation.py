# evaluation/jeu_evaluation.py

"""
Jeu d'évaluation — 20 questions d'auteur
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Porter le jeu d'évaluation de la Partie 3 : 20 questions écrites à la main, avec
pour chacune sa réponse de référence et ses pages sources (tirées du corpus). Ce
fichier est une donnée figée : il sert d'entrée au banc d'évaluation (étape 6.2)
et au calcul RAGAS. Il ne contient aucune logique d'exécution.

Ce qu'il ne fait PAS : il n'interroge pas le système, ne charge pas la base et
n'appelle aucun modèle. Les réponses de référence ont été rédigées à partir des
seules pages brutes du corpus (data/pages/complet/), sans jamais exécuter le
pipeline, pour préserver l'étanchéité de l'évaluation.

Composition
───────────
16 questions avec réponse attendue (ids 1 à 16) puis 4 questions hors périmètre
(ids 17 à 20), volontairement placées à la fin.

Étanchéité
──────────
Les questions n'ont jamais été posées au système avant le run officiel (étape 6.3).
Elles sont entièrement disjointes des 8 questions de mise au point
(src/generation/questions_mise_au_point_pilote.py).

Champs de chaque entrée
───────────────────────
  - id                : numéro de la question (1 à 20)
  - question          : la question, telle qu'un usager la poserait
  - registre          : "courant" | "familier" | "précis"
  - collectivite      : "État" | "Ville" | "hors périmètre"
  - theme             : thème court, pour le classement des résultats
  - type              : "avec_reponse" | "hors_perimetre"
  - reponse_reference : réponse attendue, 2 à 4 phrases factuelles tirées des pages
                        (pour un "hors_perimetre" : aveu d'ignorance et orientation)
  - pages_sources     : URL des pages du corpus qui fondent la réponse
                        (liste vide pour un "hors_perimetre" : rien dans le corpus)

Toutes les pages ont été capturées le 2026-08-13 (champ date_capture du corpus).
"""

QUESTIONS = [
    {
        "id": 1,
        "question": "Comment demander la naturalisation suisse à Genève ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "naturalisation",
        "type": "avec_reponse",
        "reponse_reference": (
            "La demande de naturalisation ordinaire se dépose auprès de l'Office cantonal "
            "de la population et des migrations (OCPM), Service des naturalisations, par "
            "courrier ou via le formulaire de contact. Le dossier doit être accompagné de "
            "plusieurs pièces : un acte d'état civil suisse de moins de 6 mois, une copie du "
            "permis C, des attestations de l'administration fiscale, de l'office des poursuites "
            "et de l'Hospice général, ainsi qu'une attestation de connaissance du français de "
            "niveau B1 à l'oral et A2 à l'écrit selon les normes fide. La procédure comprend un "
            "test de connaissances. L'émolument est de CHF 850 pour les personnes majeures de moins de "
            "25 ans et de CHF 1250 au-delà."
        ),
        "pages_sources": [
            "https://www.ge.ch/devenir-suisse/naturalisation-ordinaire-depot-demande",
        ],
    },
    {
        "id": 2,
        "question": "Quels documents faut-il pour se marier civilement à Genève ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "mariage-civil",
        "type": "avec_reponse",
        "reponse_reference": (
            "Pour se marier, les fiancés déposent une demande en vue du mariage auprès du "
            "Service de l'état civil, accompagnée des documents requis. Pour les Suisses "
            "célibataires, veufs ou divorcés, il faut le formulaire de demande en vue du "
            "mariage, une pièce d'identité (passeport ou carte d'identité) et, si le domicile "
            "est hors du canton, une attestation de domicile ; une copie du titre de séjour est "
            "jointe le cas échéant. Pour les fiancés étrangers, les documents varient selon le "
            "pays d'origine et l'Office de l'état civil informe de la procédure ; toute personne "
            "non suisse doit établir la légalité de son séjour. La procédure préparatoire coûte "
            "CHF 150."
        ),
        "pages_sources": [
            "https://www.geneve.ch/demarches/procedure-preparatoire-mariage",
        ],
    },
    {
        "id": 3,
        "question": "C'est où pour échanger mon permis de conduire étranger ?",
        "registre": "familier",
        "collectivite": "État",
        "theme": "echange-permis-conduire",
        "type": "avec_reponse",
        "reponse_reference": (
            "L'échange d'un permis de conduire étranger se fait en se présentant "
            "personnellement, sans rendez-vous, aux guichets du service des permis de conduire "
            "(à 1227 Carouge, tél. +41 22 388 30 30). La demande doit être faite dans les 12 "
            "mois suivant la prise de domicile en Suisse ; passé ce délai on ne peut plus "
            "conduire, mais l'échange du permis étranger valable reste possible. Il faut "
            "notamment le formulaire d'échange, une pièce d'identité, une attestation d'opticien "
            "de moins de 24 mois, une photo, l'original du permis étranger et, selon le pays, une "
            "traduction officielle. L'émolument est de CHF 150 (hors catégories C, C1, D)."
        ),
        "pages_sources": [
            "https://www.ge.ch/echanger-son-permis-conduire-etranger",
        ],
    },
    {
        "id": 4,
        "question": "Comment inscrire mon enfant dans une crèche de la Ville de Genève ?",
        "registre": "courant",
        "collectivite": "Ville",
        "theme": "creche",
        "type": "avec_reponse",
        "reponse_reference": (
            "Pour inscrire un enfant de 0 à 4 ans dans une structure d'accueil municipale ou "
            "subventionnée de la Ville de Genève, on enregistre sa demande via le portail "
            "« Demande de place en structure d'accueil de la petite enfance » ou auprès du "
            "Bureau d'information de la petite enfance (BIPE), sur rendez-vous. La demande peut "
            "être enregistrée dès la 12e semaine de grossesse. Le BIPE se situe rue du Cendrier "
            "8, 1201 Genève (tél. +41 22 418 81 81, bipe@geneve.ch). Tous les 6 mois, il faut "
            "fournir les documents actualisés sur sa situation professionnelle pour conserver sa "
            "place sur la liste d'attente."
        ),
        "pages_sources": [
            "https://www.geneve.ch/demarches/demande-place-creche",
        ],
    },
    {
        "id": 5,
        "question": "Comment obtenir un subside pour mon assurance-maladie ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "subside-assurance-maladie",
        "type": "avec_reponse",
        "reponse_reference": (
            "Le subside est une aide financière pour payer les primes de l'assurance-maladie de "
            "base (LAMal), accordée selon le revenu et la situation familiale. Il est en "
            "principe versé automatiquement, sur la base du revenu, sans qu'il faille en faire "
            "la demande ; certaines catégories doivent toutefois déposer une demande (jeunes "
            "adultes, personnes imposées à la source, personnes récemment arrivées à Genève, "
            "personnes taxées d'office ou sans avis de taxation, changement de situation). Les "
            "demandes se font par correspondance ou en ligne auprès du Service de "
            "l'assurance-maladie (SAM). S'il est accordé, le subside est versé directement à "
            "l'assurance-maladie, qui le déduit des primes."
        ),
        "pages_sources": [
            "https://www.ge.ch/informations-generales-subside-assurance-maladie",
            "https://www.ge.ch/demander-subside-assurance-maladie-2026",
        ],
    },
    {
        "id": 6,
        "question": "J'ai perdu mon travail : quelles démarches pour toucher le chômage à Genève ?",
        "registre": "familier",
        "collectivite": "État",
        "theme": "chomage",
        "type": "avec_reponse",
        "reponse_reference": (
            "Pour toucher le chômage, il faut s'inscrire à l'Office cantonal de l'emploi (OCE), "
            "au plus tard le premier jour pour lequel on demande des indemnités. On choisit une "
            "caisse de chômage, à qui on transmet les documents, et c'est elle qui détermine le "
            "droit aux indemnités ; leur durée et leur montant dépendent des cotisations versées "
            "durant les deux années précédentes. Il faut préparer une pièce d'identité ou un "
            "permis de séjour valable, la carte AVS ou d'assurance-maladie, un éventuel "
            "certificat médical et, le cas échéant, la lettre de licenciement. Un premier entretien avec un "
            "conseiller en personnel est ensuite fixé ; l'OCE se situe rue des Gares 16 à Genève."
        ),
        "pages_sources": [
            "https://www.ge.ch/inscrire-au-chomage",
            "https://www.ge.ch/inscrire-au-chomage/mode-emploi-inscrire",
            "https://www.ge.ch/inscrire-au-chomage/conditions-inscrire",
        ],
    },
    {
        "id": 7,
        "question": "Comment annoncer mon arrivée à Genève quand je viens d'un autre canton ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "arrivee-autre-canton",
        "type": "avec_reponse",
        "reponse_reference": (
            "Toute personne qui arrive à Genève depuis un autre canton doit annoncer son "
            "arrivée, en règle générale dans les 14 jours. Les Suisses peuvent le faire en ligne, par courrier ou "
            "auprès de leur commune de résidence (formulaire A, attestation de départ du canton "
            "de provenance) ; le Service de l'état civil est compétent pour la Ville de Genève. "
            "Les personnes étrangères s'annoncent à l'Office cantonal de la population et des "
            "migrations (OCPM) : les ressortissants UE/AELE dans les 14 jours suivant l'arrivée "
            "(au plus tôt 30 jours avant), les ressortissants d'États tiers doivent demander "
            "l'autorisation de changer de canton 3 mois avant. Les formalités de départ se font "
            "auprès du canton de provenance."
        ),
        "pages_sources": [
            "https://www.ge.ch/annoncer-mon-arrivee-ocpm/annonce-arrivee-geneve-suisses",
            "https://www.ge.ch/annoncer-mon-arrivee-ocpm/changement-canton-arrivee-provenance-autre-canton",
            "https://www.geneve.ch/demarches/arrivee-geneve-annonce",
        ],
    },
    {
        "id": 8,
        "question": "Quelles démarches après une naissance à Genève ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "naissance",
        "type": "avec_reponse",
        "reponse_reference": (
            "En cas de naissance en milieu hospitalier, l'établissement ou la maison de "
            "naissance annonce directement la naissance à l'arrondissement de l'état civil "
            "compétent ; à la Maternité des HUG, l'enregistrement peut se faire auprès de "
            "l'antenne de l'état civil sur place. Si l'enfant naît à domicile, les parents "
            "doivent annoncer la naissance dans les trois jours à l'arrondissement de l'état "
            "civil du lieu de naissance, attestée par un médecin ou une sage-femme. L'état civil "
            "enregistre la naissance et transmet les informations pour la mise à jour du registre "
            "des habitants. Si l'enfant est étranger et les parents titulaires d'un titre de "
            "séjour, un rendez-vous est fixé pour ses données biométriques en vue de son permis "
            "de séjour."
        ),
        "pages_sources": [
            "https://www.ge.ch/naissance",
            "https://www.geneve.ch/demarches/naissance-enregistrement",
        ],
    },
    {
        "id": 9,
        "question": "Comment demander une bourse d'études cantonale ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "bourse-etudes",
        "type": "avec_reponse",
        "reponse_reference": (
            "La demande de bourse (ou de prêt) d'études se dépose auprès du Service des bourses "
            "et prêts d'études (SBPE), via le compte e-démarches ou en version papier. Elle doit "
            "être déposée au plus tard 6 mois après le début de l'année scolaire ou académique, "
            "et peut l'être dès le mois de mai précédant la rentrée. La bourse, qui ne se "
            "rembourse pas, atteint au maximum 12 550 francs pour le degré secondaire II et "
            "16 740 francs pour le degré tertiaire, plafonds augmentés de 4 000 francs par enfant "
            "à charge. Les personnes séjournant en Suisse uniquement pour leurs études (permis B "
            "formation) n'ont en principe pas droit à ces aides du SBPE (sauf si les parents sont frontaliers)."
        ),
        "pages_sources": [
            "https://www.ge.ch/obtenir-bourse-pret-etudes-apprentissage",
        ],
    },
    {
        "id": 10,
        "question": "Comment fonctionne l'impôt à la source pour un titulaire de permis B ?",
        "registre": "précis",
        "collectivite": "État",
        "theme": "impot-source",
        "type": "avec_reponse",
        "reponse_reference": (
            "Un travailleur étranger résidant en Suisse qui n'a pas le permis C, comme un "
            "titulaire de permis B, est en principe imposé à la source, et non au régime "
            "ordinaire. On cesse d'être imposé à la source dès qu'on obtient la "
            "nationalité suisse ou le permis C, ou qu'on se marie avec un conjoint suisse ou "
            "titulaire d'un permis C : on devient alors contribuable au régime ordinaire. On est "
            "considéré comme résident au sens fiscal dès un séjour d'au moins 30 jours, sans "
            "interruption, en travaillant en Suisse."
        ),
        "pages_sources": [
            "https://www.ge.ch/impot-source/qui-est-soumis-impot-source",
        ],
    },
    {
        "id": 11,
        "question": "Je déménage à l'intérieur du canton : je dois faire quoi ?",
        "registre": "familier",
        "collectivite": "État",
        "theme": "demenagement-intracantonal",
        "type": "avec_reponse",
        "reponse_reference": (
            "Un changement d'adresse à l'intérieur du canton doit être annoncé dans les 14 jours "
            "à l'Office cantonal de la population et des migrations (OCPM). On transmet le "
            "formulaire C (ou un courrier libre), une copie d'une pièce d'identité et, pour les "
            "locataires, une copie du bail ; la démarche est gratuite. Les titulaires d'un permis "
            "valable reçoivent automatiquement une attestation de domicile à leur nouvelle "
            "adresse. Les personnes suisses peuvent s'adresser directement à leur commune de "
            "domicile ; l'OCPM se situe route de Chancy 88, 1213 Onex."
        ),
        "pages_sources": [
            "https://www.ge.ch/annoncer-changement-adresse-geneve/annoncer-changement-adresse",
            "https://www.geneve.ch/demarches/changement-adresse-canton-geneve",
        ],
    },
    {
        "id": 12,
        "question": "Comment obtenir une attestation de résidence ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "attestation-residence",
        "type": "avec_reponse",
        "reponse_reference": (
            "Toute personne résidant légalement à Genève, au bénéfice d'une autorisation de "
            "séjour ou d'établissement, peut commander une attestation de résidence auprès de "
            "l'Office cantonal de la population et des migrations (OCPM) ; un émolument de CHF 25 "
            "est perçu. Les demandes faites avec un compte vérifié sont en règle générale "
            "traitées rapidement, la clé de téléchargement de l'attestation étant transmise par courriel. Les personnes "
            "suisses peuvent commander leur attestation auprès de leur commune de domicile (pour "
            "la Ville de Genève, le Service de l'état civil, compétent pour ses habitants). Il "
            "faut fournir une copie de sa pièce d'identité et, si la commande est pour un tiers, "
            "une procuration."
        ),
        "pages_sources": [
            "https://www.ge.ch/obtenir-attestation-ocpm/commander-attestation-residence",
            "https://www.geneve.ch/demarches/obtenir-attestation-residence",
        ],
    },
    {
        "id": 13,
        "question": "Comment contester une amende d'ordre reçue à Genève ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "amende-ordre",
        "type": "avec_reponse",
        "reponse_reference": (
            "L'amende d'ordre elle-même ne peut pas être contestée ; son montant maximal est de "
            "600 francs et elle doit être payée dans un délai de 30 jours. Si elle n'est pas "
            "payée dans ce délai, elle est transmise au Service des contraventions et convertie "
            "en ordonnance pénale, majorée d'un émolument. C'est cette ordonnance pénale qui peut "
            "être contestée, dans les 10 jours suivant sa notification, en écrivant au Service "
            "des contraventions. Si le service maintient son ordonnance, le cas est transmis au "
            "Tribunal de police pour jugement."
        ),
        "pages_sources": [
            "https://www.ge.ch/contraventions/amende-ordre",
            "https://www.geneve.ch/demarches/contester-amende",
        ],
    },
    {
        # Question pratique : le corpus donne l'adresse de l'OCPM mais AUCUN horaire de guichet.
        # Conservée volontairement comme test anti-hallucination : le système doit donner
        # l'adresse et NE PAS inventer d'horaires.
        "id": 14,
        "question": "Quels sont les horaires et l'adresse de l'office cantonal de la population ?",
        "registre": "précis",
        "collectivite": "État",
        "theme": "ocpm-coordonnees",
        "type": "avec_reponse",
        "reponse_reference": (
            "L'Office cantonal de la population et des migrations (OCPM) se situe route de "
            "Chancy 88, 1213 Onex (tél. +41 22 546 48 88). Les horaires de guichet ne figurent "
            "pas sur les pages consultées ; pour les connaître, il faut consulter ge.ch ou "
            "contacter l'office directement."
        ),
        "pages_sources": [
            "https://www.geneve.ch/demarches/changement-adresse-canton-geneve",
        ],
    },
    {
        # Remplace la question initiale sur l'aide sociale (mal couverte : le corpus ne fait
        # qu'orienter vers l'Hospice général, hors corpus). Réserve R2, bien couverte.
        "id": 15,
        "question": "Comment inscrire mon enfant à l'école primaire à Genève ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "inscription-ecole-primaire",
        "type": "avec_reponse",
        "reponse_reference": (
            "À Genève, l'école primaire commence à 4 ans révolus (au 31 juillet de l'année). "
            "Pour un enfant domicilié à Genève, un courrier de convocation est envoyé au "
            "domicile début février ; en l'absence de courrier à la mi-février, il faut "
            "téléphoner à la direction générale de l'enseignement obligatoire (DGEO, tél. "
            "022 327 04 00). Les inscriptions ont ensuite lieu dans les écoles fin février ou "
            "début mars, au centre d'inscription indiqué sur la convocation ; l'enfant est ensuite "
            "scolarisé à l'école proche de son domicile. La présence de l'enfant et d'un parent est "
            "obligatoire le jour de l'inscription. Il faut apporter le bulletin d'inscription "
            "joint à la convocation, les documents d'identité de l'enfant et des deux parents, et "
            "la preuve d'affiliation à l'assurance-maladie de l'enfant."
        ),
        "pages_sources": [
            "https://www.ge.ch/inscrire-mon-enfant-ecole-primaire",
            "https://www.ge.ch/inscrire-mon-enfant-ecole-primaire/premiere-annee-primaire-1p-enfant-domicilie-geneve",
            "https://www.ge.ch/inscrire-mon-enfant-ecole-primaire/dates-lieux-inscriptions-rentree-scolaire",
        ],
    },
    {
        # Question fournie par l'auteur, remplaçant GeTax. Le permis de circulation est
        # délivré à l'immatriculation du véhicule (office cantonal des véhicules).
        "id": 16,
        "question": "Comment obtenir un permis de circulation pour mon véhicule ?",
        "registre": "courant",
        "collectivite": "État",
        "theme": "permis-circulation",
        "type": "avec_reponse",
        "reponse_reference": (
            "Le permis de circulation est délivré lors de l'immatriculation du véhicule, à "
            "1227 Carouge (tél. +41 22 388 30 30, courriel vehicules@etat.ge.ch). Le "
            "véhicule doit être immatriculé dans le canton où il est garé la nuit. Il faut "
            "fournir une attestation d'assurance RC (transmise par l'assureur par voie "
            "électronique), le permis de circulation original ou le rapport d'expertise 13.20A, "
            "la formule de demande d'immatriculation et une pièce d'identité du détenteur. Les "
            "personnes non domiciliées à Genève ajoutent une déclaration du lieu de stationnement."
        ),
        "pages_sources": [
            "https://www.ge.ch/immatriculer-vehicule-obtenir-carte-grise",
        ],
    },
    {
        "id": 17,
        "question": "Comment calculer ma future rente AVS ?",
        "registre": "courant",
        "collectivite": "hors périmètre",
        "theme": "rente-avs",
        "type": "hors_perimetre",
        "reponse_reference": (
            "Le calcul d'une future rente AVS ne relève pas du canton de Genève, mais de "
            "l'assurance-vieillesse et survivants (AVS), gérée au niveau fédéral. Le système ne "
            "dispose pas de cette information dans le corpus genevois et doit le reconnaître, en "
            "orientant la personne vers sa caisse de compensation AVS ou le portail ch.ch pour "
            "une estimation de rente."
        ),
        "pages_sources": [],
    },
    {
        "id": 18,
        "question": "Comment obtenir un permis de séjour dans le canton de Vaud ?",
        "registre": "courant",
        "collectivite": "hors périmètre",
        "theme": "permis-sejour-vaud",
        "type": "hors_perimetre",
        "reponse_reference": (
            "L'octroi d'un permis de séjour dans le canton de Vaud ne relève pas du corpus "
            "genevois. Le système doit reconnaître qu'il ne couvre que Genève et orienter la "
            "personne vers les autorités vaudoises (canton de Vaud, vd.ch)."
        ),
        "pages_sources": [],
    },
    {
        "id": 19,
        "question": "Quels sont les horaires de la ligne 12 des TPG ?",
        "registre": "courant",
        "collectivite": "hors périmètre",
        "theme": "horaires-tpg",
        "type": "hors_perimetre",
        "reponse_reference": (
            "Les horaires d'une ligne des Transports publics genevois (TPG) ne figurent pas dans "
            "le corpus des démarches administratives. Le système doit le reconnaître et orienter "
            "la personne vers les TPG (tpg.ch)."
        ),
        "pages_sources": [],
    },
    {
        # Question hors périmètre inventée à l'étape 6.1 : le corpus traite l'arrivée À Genève,
        # jamais les visas sortants vers un autre pays. Thème vérifié absent du corpus.
        "id": 20,
        "question": "Comment obtenir un visa pour travailler à l'étranger ?",
        "registre": "courant",
        "collectivite": "hors périmètre",
        "theme": "visa-travail-etranger",
        "type": "hors_perimetre",
        "reponse_reference": (
            "L'obtention d'un visa de travail pour un autre pays ne relève pas des démarches "
            "administratives genevoises. Le système doit reconnaître qu'il ne couvre que Genève "
            "et orienter la personne vers la représentation diplomatique (ambassade ou consulat) "
            "du pays de destination."
        ),
        "pages_sources": [],
    },
]
