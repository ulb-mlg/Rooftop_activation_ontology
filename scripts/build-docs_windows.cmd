@echo off
REM Builds the ontology documentation with WIDOCO in Docker.
REM Usage: scripts\build-docs.cmd [path\to\ontology]
REM Requires: Docker Desktop running. No Java, no PowerShell.
setlocal enabledelayedexpansion

set "ONTOLOGY_FILE=%~1"
if "%ONTOLOGY_FILE%"=="" set "ONTOLOGY_FILE=ontology\rooftop_activation_ontology.rdf"
set "OUT_DIR=site"
set "LANG_CODE=en"
set "IMAGE=ghcr.io/dgarijo/widoco:v1.4.25"

REM Work from the repository root, which is the parent of the scripts folder.
pushd "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo Docker not found on PATH.
  goto :fail
)

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker is installed but not running. Start Docker Desktop and try again.
  goto :fail
)

if not exist "%ONTOLOGY_FILE%" (
  echo Ontology file not found: %ONTOLOGY_FILE%
  goto :fail
)

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

REM Docker needs forward slashes, so convert the Windows paths.
set "HOST_DIR=%CD:\=/%"
set "ONT_IN=%ONTOLOGY_FILE:\=/%"
set "OUT_IN=%OUT_DIR:\=/%"

echo Running WIDOCO from %IMAGE% ...
docker run --rm -v "%HOST_DIR%:/data" "%IMAGE%" -ontFile "/data/%ONT_IN%" -outFolder "/data/%OUT_IN%" -getOntologyMetadata -uniteSections -includeAnnotationProperties -lang %LANG_CODE% -rewriteAll -webVowl -htaccess -licensius -oops

if errorlevel 1 (
  echo WIDOCO failed.
  goto :fail
)

copy /Y "%ONTOLOGY_FILE%" "%OUT_DIR%\" >nul
type nul > "%OUT_DIR%\.nojekyll"

echo.
echo Done. Preview with:
echo   python -m http.server 8000 --directory %OUT_DIR%
echo   then open http://localhost:8000
popd
endlocal
exit /b 0

:fail
popd
endlocal
exit /b 1