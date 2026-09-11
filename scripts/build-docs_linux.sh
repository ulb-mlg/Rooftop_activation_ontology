#!/usr/bin/env bash
# Builds the ontology documentation with WIDOCO in Docker.
# Usage: ./scripts/build-docs_linux.sh [path/to/ontology]
# Requires: Docker. No Java installation needed.
set -euo pipefail

ONTOLOGY_FILE="${1:-ontology/rooftop_activation_ontology.rdf}"
OUT_DIR="site"
LANG_CODE="en"
IMAGE="ghcr.io/dgarijo/widoco:v1.4.25"

command -v docker >/dev/null 2>&1 || { echo "Docker not found on PATH." >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo "Docker is installed but not running." >&2; exit 1; }

if [ ! -f "$ONTOLOGY_FILE" ]; then
  echo "Ontology file not found: $ONTOLOGY_FILE" >&2
  exit 1
fi

# The container runs as an unprivileged user, so create the output folder on the
# host first and run as the current user to avoid root-owned output.
mkdir -p "$OUT_DIR"

USER_FLAG=()
if [ "$(uname -s)" = "Linux" ]; then
  USER_FLAG=(--user "$(id -u):$(id -g)")
fi

docker run --rm "${USER_FLAG[@]}" \
  -v "$(pwd):/data" \
  -w /data \
  "$IMAGE" \
  -ontFile "/data/$ONTOLOGY_FILE" \
  -outFolder "/data/$OUT_DIR" \
  -getOntologyMetadata \
  -uniteSections \
  -includeAnnotationProperties \
  -lang "$LANG_CODE" \
  -rewriteAll \
  -webVowl \
  -htaccess \
  -licensius \
  -oops

cp "$ONTOLOGY_FILE" "$OUT_DIR/"
touch "$OUT_DIR/.nojekyll"

echo
echo "Done. Preview with:"
echo "  python -m http.server 8000 --directory $OUT_DIR"
echo "  then open http://localhost:8000"
