# src/generation/questions_mise_au_point_pilote.py

"""
Questions de mise au point de l'étape 2 (consigne de génération)
─────────────────────────────────────────────────────────────────────────────

Responsabilité
──────────────
Porter les 8 questions servant à mettre au point la consigne : 6 tirées du corpus
pilote (permis de séjour) et 2 hors corpus. Chaque question porte son origine, pour
que la grille de lecture attende, ou non, une réponse fondée sur les extraits.

Distinction essentielle
───────────────────────
Ce jeu de mise au point n'est PAS le jeu d'évaluation du chapitre 7, qui doit
arriver vierge à la Partie 3. Il ne sert qu'à régler la consigne.
"""

# origine : "corpus" (réponse attendue depuis les extraits) ou "hors-corpus"
# (réponse attendue : ignorance avouée et orientation, sans rien inventer).
QUESTIONS = [
    {"texte": "Après combien d'années de séjour puis-je demander un permis C ?", "origine": "corpus"},
    {"texte": "Comment renouveler mon permis B qui arrive à échéance ?", "origine": "corpus"},
    {"texte": "Est-ce que je peux travailler pendant mes études à Genève ?", "origine": "corpus"},
    {"texte": "Quel permis faut-il pour travailler comme indépendant à Genève ?", "origine": "corpus"},
    {"texte": "C'est où pour déposer ma demande de permis ?", "origine": "corpus"},
    {"texte": "Comment faire venir ma famille à Genève ?", "origine": "corpus"},
    {"texte": "Quels sont les horaires de la déchetterie de ma commune ?", "origine": "hors-corpus"},
    {"texte": "Comment renouveler ma carte d'identité ?", "origine": "hors-corpus"},
]
