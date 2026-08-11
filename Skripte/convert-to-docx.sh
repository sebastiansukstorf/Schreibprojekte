#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/.." && pwd)"
cd "$REPO_ROOT"

SOURCE_DIR="${1:-../Testprojekt}"
SOURCE_DIR="$(cd "$SOURCE_DIR" 2>/dev/null && pwd)"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "❌ Quellordner nicht gefunden: $SOURCE_DIR"
  exit 1
fi

METADATA_FILE="$SOURCE_DIR/Metadaten/titlepage.yml"
if [ ! -f "$METADATA_FILE" ] && [ -d "$SOURCE_DIR/.." ]; then
  METADATA_FILE="$SOURCE_DIR/../Metadaten/titlepage.yml"
fi
if [ ! -f "$METADATA_FILE" ]; then
  echo "❌ Metadaten-Datei fehlt: $METADATA_FILE"
  exit 1
fi

TITLE=$(grep '^title:' "$METADATA_FILE" | sed 's/title:[[:space:]]*//;s/ /_/g')
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
  PROJECT_DIR="$SOURCE_DIR"
  if [ "$(basename "$SOURCE_DIR")" = "03_Content" ]; then
    PROJECT_DIR="$(dirname "$SOURCE_DIR")"
  fi

  TARGET_DIR="$PROJECT_DIR/docx"
  mkdir -p "$TARGET_DIR"
  OUTFILE="${TARGET_DIR}/${TITLE}_${TIMESTAMP}.docx"
fi

if [ -d "$TARGET_DIR" ]; then
  find "$TARGET_DIR" -maxdepth 1 -type f -name '*.docx' -delete
fi

CONTENT_DIR="$SOURCE_DIR"
if [ -d "$SOURCE_DIR/03_Content" ]; then
  CONTENT_DIR="$SOURCE_DIR/03_Content"
fi

TMPFILE=$(mktemp)
for f in "$CONTENT_DIR"/[0-9]*.md; do
  if [ -f "$f" ]; then
    cat "$f"
    echo -e "\n"
  fi
 done > "$TMPFILE"

if [ ! -s "$TMPFILE" ]; then
  echo "❌ Keine Markdown-Dateien im Quellordner gefunden: $SOURCE_DIR"
  exit 1
fi

uv run --python 3.13 pandoc "$TMPFILE" \
  --from=markdown+hard_line_breaks \
  --lua-filter=ressourcen/filter/insert-visible-dummy-parabreak.lua \
  --filter=ressourcen/filter/insert-pagebreaks.py \
  --metadata-file="$METADATA_FILE" \
  --reference-doc=ressourcen/Normseite.docx \
  -o "$OUTFILE"

rm "$TMPFILE"
echo "✅ Exportiert nach: $OUTFILE"
echo "📁 Quelle: $SOURCE_DIR"
