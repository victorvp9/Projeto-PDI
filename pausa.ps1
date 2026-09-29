# Congela (pausar) ou retoma (continuar) todos os processos `python -m src.run` e os
# trabalhadores do pool deles. Congelado, o processo não usa CPU e mantém o estado na
# memória: sobrevive a suspender/hibernar o Windows, NÃO a reiniciar ou desligar.
# Uso: powershell -ExecutionPolicy Bypass -File pausa.ps1 pausar|continuar|estado
param([Parameter(Mandatory)][ValidateSet('pausar', 'continuar', 'estado')]$acao)
Add-Type @"
using System; using System.Runtime.InteropServices;
public static class Proc {
    [DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr h);
    [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr h);
}
"@
$all = Get-CimInstance Win32_Process -Filter "Name='python.exe'"
$roots = @($all | Where-Object { $_.CommandLine -match 'src\.run' -and $_.CommandLine -notmatch 'spawn_main' })
$ids = @($roots.ProcessId)
foreach ($r in $roots) { $ids += @($all | Where-Object { $_.CommandLine -match "parent_pid=$($r.ProcessId)\b" } | ForEach-Object ProcessId) }
foreach ($r in $roots) { "{0}  {1}" -f $r.ProcessId, ($r.CommandLine -replace '.*src\.run', 'src.run') }
if (-not $ids) { "nenhum processo src.run rodando"; exit }
# Conta as threads suspensas de um processo (0 = rodando ou esperando normalmente)
function Suspended($p) { $p.Refresh(); @($p.Threads | Where-Object { $_.WaitReason -eq 'Suspended' }).Count }

$procs = @($ids | ForEach-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue } | Where-Object { $_ })
foreach ($p in $procs) {
    if ($acao -eq 'pausar' -and (Suspended $p) -eq 0) { [void][Proc]::NtSuspendProcess($p.Handle) }   # nunca suspende duas vezes
    if ($acao -eq 'continuar') {
        # a suspensão é um contador: retoma até não sobrar thread suspensa (em 29/09 um
        # processo ficou congelado depois de um único `continuar` e travou o pool inteiro)
        for ($k = 0; $k -lt 10 -and (Suspended $p) -gt 0; $k++) { [void][Proc]::NtResumeProcess($p.Handle) }
    }
}
$stuck = @($procs | Where-Object { (Suspended $_) -gt 0 })
"{0}: {1} processos; {2} congelados, {3} rodando" -f $acao, $procs.Count, $stuck.Count, ($procs.Count - $stuck.Count)
if ($acao -ne 'pausar' -and $stuck) { "   ainda congelados: " + (($stuck | ForEach-Object Id) -join ', ') }
