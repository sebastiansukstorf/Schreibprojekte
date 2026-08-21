#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/.." && pwd)"
cd "$REPO_ROOT"
mkdir -p "$REPO_ROOT/docx"

INPUT="${1:-}"
if [ -z "$INPUT" ]; then
  echo "❌ Bitte eine Markdown-Datei angeben."
  exit 1
fi

if [ ! -f "$INPUT" ]; then
  echo "❌ Eingabedatei nicht gefunden: $INPUT"
  exit 1
fi

SOURCE_DIR=$(cd "$(dirname "$INPUT")" && pwd)
METADATA_FILE="$SOURCE_DIR/Metadaten/titlepage.yml"
if [ ! -f "$METADATA_FILE" ]; then
  METADATA_FILE="$SOURCE_DIR/../Metadaten/titlepage.yml"
fi
if [ ! -f "$METADATA_FILE" ]; then
  echo "❌ Metadaten-Datei fehlt: $METADATA_FILE"
  exit 1
fi
TITLE=$(awk '/^title:/ {gsub(/^title:[[:space:]]*/, "", $0); gsub(/[[:space:]]+/, "_"); print; exit}' "$METADATA_FILE")
[ -z "$TITLE" ] && TITLE="Export"
SOURCE_NAME=$(basename "$SOURCE_DIR")
SAFE_SOURCE_NAME=$(echo "$SOURCE_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_-]/_/g; s/_\+/_/g; s/^_//; s/_$//')
TIMESTAMP=$(date +"%Y%m%d_%H_%M")

if [ -n "${2:-}" ]; then
  OUTPUT_TARGET="${2}"
  if [[ "$OUTPUT_TARGET" == /* ]]; then
    RESOLVED_OUTPUT="$OUTPUT_TARGET"
  else
    RESOLVED_OUTPUT="$REPO_ROOT/$OUTPUT_TARGET"
  fi

  if [[ "$OUTPUT_TARGET" == *.docx ]]; then
    OUTFILE="$RESOLVED_OUTPUT"
    mkdir -p "$(dirname "$OUTFILE")"
  else
    TARGET_DIR="$RESOLVED_OUTPUT"
    mkdir -p "$TARGET_DIR"
    OUTFILE="${TARGET_DIR}/${TITLE}_${TIMESTAMP}.docx"
  fi
else
  TARGET_DIR="$SOURCE_DIR/docx"
  mkdir -p "$TARGET_DIR"
  OUTFILE="${TARGET_DIR}/${TITLE}_${TIMESTAMP}.docx"
fi

if [ -d "$TARGET_DIR" ]; then
  find "$TARGET_DIR" -maxdepth 1 -type f -name '*.docx' -delete
fi

TEMPLATE="ressourcen/Normseite.docx"

uv run --python 3.13 pandoc "$INPUT" \
  --from=markdown+hard_line_breaks+smart \
  --lua-filter=ressourcen/filter/german-quotes.lua \
  --lua-filter=ressourcen/filter/insert-visible-dummy-parabreak.lua \
  --filter=ressourcen/filter/insert-pagebreaks.py \
  --metadata-file="$METADATA_FILE" \
  --reference-doc="$TEMPLATE" \
  -o "$OUTFILE"

echo "✅ Exportiert nach: $OUTFILE"
