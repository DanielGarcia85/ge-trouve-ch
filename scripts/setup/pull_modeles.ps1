# scripts/setup/pull_modeles.ps1
#
# Téléchargement des modèles Ollama du projet — un poste, une fois.
# Responsabilité : tirer les trois modèles utilisés par Ge-Trouve, aux tags épinglés,
# depuis la bibliothèque Ollama. Les commandes `ollama pull` sont identiques sous Windows
# et sous Ubuntu : ce script resservira au déploiement sur le VPS. Ne configure rien
# d'autre (ni Ollama lui-même, ni le venv Python).

$modeles = @(
    "gemma4:12b",            # LLM rédacteur (Q4_K_M, 7,6 Go)
    "llama3.1:8b",           # repli et juge d'évaluation (Q4_K_M, 4,9 Go)
    "qwen3-embedding:0.6b"   # embeddings (Q8_0, 639 Mo)
)

foreach ($modele in $modeles) {
    Write-Output "== ollama pull $modele =="
    ollama pull $modele
    Write-Output ""
}

Write-Output "Modeles installes :"
ollama list
