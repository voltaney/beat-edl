# Build the beat-edl Windows app (onedir) with PyInstaller via uv.
#
#   pwsh packaging/build.ps1
#
# Produces dist/beat-edl/beat-edl.exe alongside its dependencies.

$ErrorActionPreference = "Stop"

# Run from the repository root regardless of where the script is invoked.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

uv sync
uv run pyinstaller packaging/beat-edl.spec --noconfirm

Write-Host "Built: $(Join-Path $root 'dist/beat-edl/beat-edl.exe')"
