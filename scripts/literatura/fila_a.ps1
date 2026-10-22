# Fila do A' (docs/decisoes.md, 2026-10-22): triagem -> (só se passar) série na metade fixa -> 6c na metade fixa.
# Cada passo grava <passo>.log e, se terminar bem, <passo>.ok em outputs/runs_v2/fila/; passos com .ok são pulados.
# Uso (da raiz): powershell -ExecutionPolicy Bypass -File scripts/literatura/fila_a.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
$env:PYTHONPATH = '.'; $env:PYTHONIOENCODING = 'utf-8'; $env:OPENBLAS_NUM_THREADS = '1'
$uv = "$env:USERPROFILE\.local\bin\uv.exe"
$log = 'outputs\runs_v2\fila'
New-Item -ItemType Directory -Force $log | Out-Null
function Note($m) {
    $line = "[$(Get-Date -Format s)] $m`r`n"
    for ($i = 0; $i -lt 60; $i++) {
        try { [IO.File]::AppendAllText((Join-Path $PWD "$log\fila_a.log"), $line, (New-Object Text.UTF8Encoding $false)); return }
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
Note "fila do A' iniciada"
Step a2_triagem { & $uv run python scripts/v2/triagem_a.py 10 }
$verdict = Get-Content "$log\a2_triagem.log" -Encoding utf8 | Select-String -Pattern 'passa na triagem|PARA \(regra' | Select-Object -Last 1
Note "triagem: $verdict"
if ($verdict -notmatch 'passa na triagem') { Note "A' parado na triagem; fila encerrada"; exit 0 }
Step a2_serie { & $uv run python scripts/v2/serie_a_metade.py 11 }
Step a2_6c { & $uv run python scripts/v2/rodada_6c_dev.py a_central eval_6c_b1 - --metade 6 }
Note "fila do A' concluída"
