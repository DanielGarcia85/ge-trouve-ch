# scripts/mesures/releve_poste.ps1
#
# Relevé du poste — état des lieux matériel et logiciel.
# Responsabilité : afficher machine, CPU, RAM, OS et versions des outils
# (Python, Ollama, git), pour renseigner les blocs « Poste » et « Versions »
# du journal des mesures. Ne mesure aucune performance. À relancer sur chaque poste.

$os = Get-CimInstance Win32_OperatingSystem
$cpu = (Get-CimInstance Win32_Processor).Name
$ramInstalled = [math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum / 1GB, 0)
$ramVisible = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
$diskFree = [math]::Round((Get-Volume C).SizeRemaining / 1GB, 1)

Write-Output "Machine        : $env:COMPUTERNAME"
Write-Output "LOCAL_PC_VENV  : $env:LOCAL_PC_VENV"
Write-Output "CPU            : $cpu"
Write-Output "RAM installee  : $ramInstalled Go"
Write-Output "RAM disponible : $ramVisible Go"
Write-Output "Disque C libre : $diskFree Go"
Write-Output "OS             : $($os.Caption) ($($os.Version))"
Write-Output "Python         : $(python --version 2>&1)"
Write-Output "Ollama         : $(ollama --version 2>&1)"
Write-Output "git            : $(git --version)"
