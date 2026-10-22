# Depois do A' aceito (docs/decisoes.md, 2026-10-22): série do A' na outra metade e o 6c dela, e a tabela da
# nova base (B1 + A') nos 115 clipes do dev. Passos com .ok em outputs/runs_v2/fila/ são pulados.
# Uso (da raiz): powershell -ExecutionPolicy Bypass -File scripts/literatura/fila_a_outra.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
$env:PYTHONPATH = '.'; $env:PYTHONIOENCODING = 'utf-8'; $env:OPENBLAS_NUM_THREADS = '1'
$uv = "$env:USERPROFILE\.local\bin\uv.exe"
$log = 'outputs\runs_v2\fila'
New-Item -ItemType Directory -Force $log | Out-Null
function Note($m) {
    $line = "[$(Get-Date -Format s)] $m`r`n"
    for ($i = 0; $i -lt 60; $i++) {
        try { [IO.File]::AppendAllText((Join-Path $PWD "$log\fila_a_outra.log"), $line, (New-Object Text.UTF8Encoding $false)); return }
        catch { Start-Sleep -Milliseconds 500 }
    }
}
function Step($name, [scriptblock]$cmd) {
    if (Test-Path "$log\$name.ok") { Note "pula $name (já concluído)"; return }
    Note "início $name"
    $ErrorActionPreference = 'Continue'
    & $cmd *>&1 | ForEach-Object { "$_" } | Add-Content "$log\$name.log" -Encoding utf8
    $code = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($code) { Note "FALHA $name (código $code)"; exit 1 }
    New-Item "$log\$name.ok" -ItemType File | Out-Null
    Note "fim $name"
}
Note "fila da outra metade iniciada"
Step a2_serie_outra { & $uv run python scripts/v2/serie_a_metade.py --outra 11 }
Step a2_base_completa { & $uv run python scripts/literatura/base_a_completa.py 6 }
Note "fila da outra metade concluída"
