[CmdletBinding()]
param(
    [string]$System   = "",
    [string]$Model    = $(if ($env:OLLAMA_MODEL)    { $env:OLLAMA_MODEL }    else { "0xIbra/supergemma4-26b-uncensored-gguf-v2:Q4_K_M" }),
    [string]$Endpoint = $(if ($env:OLLAMA_ENDPOINT) { $env:OLLAMA_ENDPOINT } else { "http://localhost:11434" }),
    [double]$Temp     = $(if ($env:OLLAMA_TEMP)     { [double]$env:OLLAMA_TEMP } else { 0.2 }),
    [string]$Enabled  = $(if ($env:OLLAMA_ENABLED)  { $env:OLLAMA_ENABLED }  else { "true" })
)

$ErrorActionPreference = "Stop"

# Plugin userConfig ollama_enabled = false → no-op, stdout 비움
if ($Enabled -eq "false" -or $Enabled -eq "0") {
    [Console]::Error.WriteLine("gemma.ps1: ollama_enabled=false, skipping delegation")
    exit 3  # distinct exit code: caller recognizes "intentionally disabled"
}

$prompt = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($prompt)) {
    [Console]::Error.WriteLine("gemma.ps1: empty prompt on stdin")
    exit 2
}

$fullPrompt = if ($System) { "$System`n`n$prompt" } else { $prompt }

$body = @{
    model   = $Model
    prompt  = $fullPrompt
    stream  = $false
    options = @{ temperature = $Temp }
} | ConvertTo-Json -Compress -Depth 5

$scriptStart = Get-Date
$status = "ok"
$evalCount = $null
$promptEvalCount = $null
$exitCode = 0

try {
    $resp = Invoke-RestMethod -Uri "$Endpoint/api/generate" `
                              -Method Post `
                              -Body $body `
                              -ContentType "application/json" `
                              -TimeoutSec 300
} catch {
    [Console]::Error.WriteLine("gemma.ps1: Ollama request failed — $($_.Exception.Message)")
    $status = "error"
    $exitCode = 1
}

if ($status -eq "ok" -and -not $resp.response) {
    [Console]::Error.WriteLine("gemma.ps1: no 'response' field in Ollama reply")
    $status = "error"
    $exitCode = 1
}

if ($status -eq "ok") {
    [Console]::Out.Write($resp.response)
    if ($resp.eval_count)        { $evalCount = [int]$resp.eval_count }
    if ($resp.prompt_eval_count) { $promptEvalCount = [int]$resp.prompt_eval_count }
}

# --- Telemetry (optional — Project 가 $env:VP_TELEMETRY_SCRIPT 를 설정한 경우에만) ---
# Plugin 은 telemetry 구현을 번들하지 않음. 계측이 필요한 Project 는
# hook_recorder.py 같은 스크립트 경로를 VP_TELEMETRY_SCRIPT 로 노출.
try {
    $recorder = $env:VP_TELEMETRY_SCRIPT
    if ($recorder -and (Test-Path $recorder)) {
        $durationMs = [int]((Get-Date) - $scriptStart).TotalMilliseconds
        $metaObj = @{
            status      = $status
            duration_ms = $durationMs
            model       = $Model
            exit_code   = $exitCode
        }
        if ($null -ne $evalCount)       { $metaObj.eval_count = $evalCount }
        if ($null -ne $promptEvalCount) { $metaObj.prompt_eval_count = $promptEvalCount }
        $metaJson = $metaObj | ConvertTo-Json -Compress
        $metaJson | python $recorder gemma_call 2>$null | Out-Null
    }
} catch {
    # 텔레메트리 실패는 조용히 무시
}

exit $exitCode
