# Rodada única do GSR test, v2 exploratória (test já visto no v1), com o v2 congelado (tag v2-final; docs/decisoes.md 2026-10-23).
# Passos com .ok em outputs/runs_v2/fila/ são pulados; a fila para na primeira falha. Log em outputs/runs_v2/fila/fila_test.log.
# Uso (da raiz): powershell -ExecutionPolicy Bypass -File scripts/literatura/fila_test.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
$env:PYTHONPATH = '.'; $env:PYTHONIOENCODING = 'utf-8'; $env:OPENBLAS_NUM_THREADS = '1'
$uv = "$env:USERPROFILE\.local\bin\uv.exe"
$log = 'outputs\runs_v2\fila'
New-Item -ItemType Directory -Force $log | Out-Null
function Note($m) {
    $line = "[$(Get-Date -Format s)] $m`r`n"
    for ($i = 0; $i -lt 60; $i++) {
        try { [IO.File]::AppendAllText((Join-Path $PWD "$log\fila_test.log"), $line, (New-Object Text.UTF8Encoding $false)); return }
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
# o método tem de ser o congelado: src_v2 e config_v2 iguais à tag v2-final e sem alteração pendente
git diff --quiet v2-final -- src_v2 config_v2.yaml
if ($LASTEXITCODE) { Note "FALHA: src_v2/config_v2 diferem da tag v2-final"; exit 1 }
if (git status --porcelain -- src_v2 config_v2.yaml scripts/v2) { Note "FALHA: alteração sem commit em src_v2/config_v2/scripts/v2"; exit 1 }
Note "fila do test iniciada (v2-final)"
$zip = 'data\_zips\test.zip'
$sha = 'ac40080fadaebf3474477889576662de7970cae0cb375d7cd22d96f49aeefbfd'
Step t_download {
    New-Item -ItemType Directory -Force data\_zips, data\SoccerNet-GSR\test | Out-Null
    curl.exe -L -C - -sS -o $zip "https://huggingface.co/datasets/SoccerNet/SN-GSR-2024/resolve/3cc710eb6d53a23350a3d2863311c1c0a2e645d7/test.zip"
    $h = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
    if ($h -ne $sha) { "SHA-256 diferente: $h"; cmd /c exit 1 } else { "SHA-256 confere: $h"; cmd /c exit 0 }
}
Step t_extrai {
    tar -xf $zip -C data\SoccerNet-GSR\test
    $n = (Get-ChildItem data\SoccerNet-GSR\test -Directory).Count
    $bad = @(Get-ChildItem data\SoccerNet-GSR\test -Directory | Where-Object { (Get-ChildItem "$($_.FullName)\img1" -Filter *.jpg).Count -ne 750 -or -not (Test-Path "$($_.FullName)\Labels-GameState.json") }).Count
    "clipes $n, incompletos $bad"
    if ($n -eq 49 -and $bad -eq 0) { Remove-Item $zip; cmd /c exit 0 } else { cmd /c exit 1 }
}
Step t_serie { & $uv run python -m src_v2.run --detect-series --splits test --clip-step 1 }
Step t_confere_v1 { & $uv run python scripts/v2/rodada_test_v2/confere_v1_test.py }
Step t_6c { & $uv run python -m src_v2.run --propagate-eval --splits test --clip-step 1 --workers 6 }
# pedido de Victor: nos clipes sem H nova do A' e sem recusa do B1, 6c, teto e aceitas iguais aos do v1; senão a fila para aqui
Step t_confere_v1_6c { & $uv run python scripts/v2/rodada_test_v2/confere_v1_6c.py }
Step t_extras { & $uv run python scripts/v2/rodada_test_v2/extras_test_v2.py 8 }
Step t_tabelas { & $uv run python scripts/v2/rodada_test_v2/tabelas_test_v2.py test }
Note "fila do test concluída"
