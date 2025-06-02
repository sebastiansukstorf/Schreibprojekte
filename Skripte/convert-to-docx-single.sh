#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.."
mkdir -p docx

INPUT="$1"
if [ ! -f "$INPUT" ]; then
  echo "❌ Eingabedatei nicht gefunden: $INPUT"
  exit 1
fi

TITLE=$(awk '/^title:/ {gsub(/^title:[[:space:]]*/, "", $0); gsub(/[[:space:]]+/, "_"); print; exit}' "$INPUT")
[ -z "$TITLE" ] && TITLE="Export"

TIMESTAMP=$(date +"%Y%m%d_%H_%M")
OUTFILE="docx/${TITLE}_${TIMESTAMP}.docx"
TEMPLATE="Vorlage/Erzaehlung.docx"

pandoc "$INPUT" \
  --from=markdown+hard_line_breaks \
  --lua-filter=Skripte/insert-visible-dummy-parabreak.lua \
  --filter=Skripte/insert-pagebreaks.py \
  --reference-doc="$TEMPLATE" \
  --metadata-file= \
  -o "$OUTFILE"

echo "✅ Exportiert nach: $OUTFILE"
