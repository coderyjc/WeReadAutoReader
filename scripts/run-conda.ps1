param(
    [switch]$Debug
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Entry = Join-Path $ProjectRoot "app\Application.py"
$ArgsList = @("run", "-n", "wxreader-py37", "python", $Entry)

if ($Debug) {
    $ArgsList += "--DEBUG"
}

conda @ArgsList
