#!/usr/bin/env pwsh
# Builds the ontology documentation with WIDOCO in Docker.
# Usage: .\scripts\build-docs_windows.ps1 [-OntologyFile path\to\ontology]
# Requires: Docker Desktop. No Java installation needed.

param(
    [string]$OntologyFile = "ontology/rooftop_activation_ontology.rdf",
    [string]$OutDir       = "site",
    [string]$LangCode     = "en",
    [string]$Image        = "ghcr.io/dgarijo/widoco:v1.4.25"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker not found on PATH."
}
docker info *> $null
if ($LASTEXITCODE -ne 0) { Write-Error "Docker is installed but not running. Start Docker Desktop." }

if (-not (Test-Path $OntologyFile)) {
    Write-Error "Ontology file not found: $OntologyFile"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# Docker paths always use forward slashes, including on Windows.
$OntInContainer = "/data/" + ($OntologyFile -replace '\\', '/')
$OutInContainer = "/data/" + ($OutDir -replace '\\', '/')

$dockerArgs = @(
    "run", "--rm",
    "-v", "$($PWD.Path):/data",
    "-w", "/data",
    $Image,
    "-ontFile", $OntInContainer,
    "-outFolder", $OutInContainer,
    "-getOntologyMetadata",
    "-uniteSections",
    "-includeAnnotationProperties",
    "-lang", $LangCode,
    "-rewriteAll",
    "-webVowl",
    "-htaccess",
    "-licensius",
    "-oops"
)

& docker @dockerArgs
if ($LASTEXITCODE -ne 0) { Write-Error "WIDOCO exited with code $LASTEXITCODE" }

Copy-Item $OntologyFile -Destination $OutDir -Force
New-Item -ItemType File -Force -Path (Join-Path $OutDir ".nojekyll") | Out-Null

Write-Host ""
Write-Host "Done. Preview with:"
Write-Host "  python -m http.server 8000 --directory $OutDir"
Write-Host "  then open http://localhost:8000"
