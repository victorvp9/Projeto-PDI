# Fila da rodada no dev (GSR train + valid, 115 clipes), em ordem, parando na primeira falha:
#   serie -> d3 -> d1 -> d2 -> base_b1 (6c com temporal.bidirectional: false) -> confere_base -> c_bidirecional
# Cada passo retoma dos caches: rodar de novo continua de onde parou. Log em outputs/runs_v2/fila/.
# Pausar/continuar: powershell -ExecutionPolicy Bypass -File pausa.ps1 pausar|continuar
# Uso (da raiz): powershell -ExecutionPolicy Bypass -File scripts/literatura/fila_dev.ps1 [trabalhadores do 6c]
param([int]$w6c = 8)
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
$env:PYTHONPATH = '.'; $env:PYTHONIOENCODING = 'utf-8'; $env:OPENBLAS_NUM_THREADS = '1'
$uv = "$env:USERPROFILE\.local\bin\uv.exe"
$log = 'outputs\runs_v2\fila'
New-Item -ItemType Directory -Force $log | Out-Null
# o log pode estar aberto por quem o lê (vigilância): tenta de novo em vez de derrubar a fila
# (em 21/10 a fila parou depois da série por um Add-Content com o arquivo em uso)
function Note($m) {
    $line = "[$(Get-Date -Format s)] $m`r`n"
    for ($i = 0; $i -lt 60; $i++) {
        try { [IO.File]::AppendAllText((Join-Path $PWD "$log\fila.log"), $line, (New-Object Text.UTF8Encoding $false)); return }
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
    if ($code) { Note "FALHA $name (código $code); veja $log\$name.log"; Restore-Config; exit 1 }
    New-Item "$log\$name.ok" -ItemType File | Out-Null
    Note "fim $name"
}

# a base do C é o 6c do B1: temporal.bidirectional: false só durante o passo base_b1.
# Troca de bytes exata ("true " e "false" têm o mesmo tamanho); confere que só isso mudou.
function Set-Bidir($v) {
    & $uv run python -c "import sys; p='config_v2.yaml'; s=open(p,'rb').read(); a,b=(b'bidirectional: true ',b'bidirectional: false') if sys.argv[1]=='false' else (b'bidirectional: false',b'bidirectional: true '); n=s.count(a); assert n in (0,1), n; open(p,'wb').write(s.replace(a,b))" $v
    if ($LASTEXITCODE) { throw "não consegui trocar temporal.bidirectional para $v" }
}
# só desfaz a troca feita por esta execução (o C foi recusado em 21/10 e o commit passou a ter false)
$script:flipped = $false
function Restore-Config {
    if ($script:flipped) { Set-Bidir 'true'; $script:flipped = $false }
    git diff --quiet -- config_v2.yaml
    if ($LASTEXITCODE) { Note "ATENÇÃO: config_v2.yaml difere do commit depois de restaurar" } else { Note "config_v2.yaml igual ao commit" }
}

Note "fila iniciada (6c com $w6c trabalhadores)"
Step serie { & $uv run python -m src_v2.run --detect-series --splits train valid --clip-step 1 }
Step d3 { & $uv run python scripts/literatura/d3_centro_ancoras.py outputs/runs_v2/literatura serie }
Step d1 { & $uv run python scripts/literatura/d1_lente.py outputs/runs_v2/literatura 25 }
Step d2 { & $uv run python scripts/literatura/d2_centro.py outputs/runs_v2/literatura gt 5 }
if (-not (Test-Path "$log\base_b1.ok")) { Set-Bidir 'false'; $script:flipped = $true }
Step base_b1 { & $uv run python -m src_v2.run --propagate-eval --splits train valid --clip-step 1 --workers $w6c }
Restore-Config
Step confere_base { & $uv run python scripts/literatura/confere_base_b1.py }
# base = a tabela do B1 recalculada aqui (confere_base): Δ do teto sem misturar máquinas
Step c_bidirecional { & $uv run python scripts/v2/rodada_6c_dev.py c_bidirecional eval_6c_b1 outputs/runs_v2/base_b1_local/por_jogo.csv $w6c }
Note "fila concluída"
