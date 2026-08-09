#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/.." && pwd)"
cd "$REPO_ROOT"
mkdir -p "$REPO_ROOT/docx"

if [ ! -f "Metadaten/titlepage.yml" ]; then
  echo "❌ Metadaten-Datei fehlt: Metadaten/titlepage.yml"
  exit 1
fi

if [ -f "$PWD/Metadaten/titlepage.yml" ]; then
  METADATA_FILE="$PWD/Metadaten/titlepage.yml"
elif [ -f "$REPO_ROOT/Metadaten/titlepage.yml" ]; then
  METADATA_FILE="$REPO_ROOT/Metadaten/titlepage.yml"
else
  echo "❌ Metadaten-Datei fehlt. Erwartet unter: $PWD/Metadaten/titlepage.yml"
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "$METADATA_FILE")/.." && pwd)"
TITLE=$(grep '^title:' "$METADATA_FILE" | sed 's/title:[[:space:]]*//;s/ /_/g')
TIMESTAMP=$(date +"%Y%m%d_%H_%M")
mkdir -p "$PROJECT_ROOT/docx"
OUTFILE="$PROJECT_ROOT/docx/${TITLE}_AUSZUG_${TIMESTAMP}.docx"

TMPFILE=$(mktemp)
cat > "$TMPFILE"

uv run --python 3.13 pandoc "$TMPFILE" \
  --from=markdown+hard_line_breaks \
  --lua-filter=Skripte/insert-visible-dummy-parabreak.lua \
  --filter=Skripte/insert-pagebreaks.py \
  --metadata-file=Metadaten/titlepage.yml \
  --reference-doc=Vorlage/Normseite.docx \
  -o "$OUTFILE"

rm "$TMPFILE"
echo "✅ Markierter Text exportiert nach: $OUTFILE"
