# scripts/mesures/releve_ram.ps1
#
# Relevé RAM — instantané de la mémoire système et des modèles chargés.
# Responsabilité : afficher RAM totale/utilisée/libre et la sortie de `ollama ps`
# (modèles résidents et leur taille). À appeler à chaque état mesuré. Ne mesure aucun débit.

$os = Get-CimInstance Win32_OperatingSystem
$totalGo = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$freeGo = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
$usedGo = [math]::Round($totalGo - $freeGo, 1)

Write-Output "RAM totale   : $totalGo Go"
Write-Output "RAM utilisee : $usedGo Go"
Write-Output "RAM libre    : $freeGo Go"
Write-Output ""
Write-Output "ollama ps :"
ollama ps
