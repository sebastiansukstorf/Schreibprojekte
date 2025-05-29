#!/bin/bash

# Pfad ins Projektverzeichnis
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.."
mkdir -p docx

# Metadaten prüfen
if [ ! -f "Metadaten/titlepage.yml" ]; then
  echo "❌ Metadaten-Datei fehlt: Metadaten/titlepage.yml"
  exit 1
fi

# Titel & Zeitstempel für Dateiname
TITLE=$(grep '^title:' Metadaten/titlepage.yml | sed 's/title:[[:space:]]*//;s/ /_/g')
TIMESTAMP=$(date +"%Y%m%d_%H_%M")
OUTFILE="docx/${TITLE}_AUSZUG_${TIMESTAMP}.docx"

# Eingabe aus STDIN (markierter Text aus VS Code)
TMPFILE=$(mktemp)
cat > "$TMPFILE"

# Konvertierung
pandoc "$TMPFILE" \
  --from=markdown+hard_line_breaks \
  --lua-filter=Skripte/insert-visible-dummy-parabreak.lua \
  --filter=Skripte/insert-pagebreaks.py \
  --metadata-file=Metadaten/titlepage.yml \
  --reference-doc=Vorlage/Normseite.docx \
  -o "$OUTFILE"

rm "$TMPFILE"
echo "✅ Markierter Text exportiert nach: $OUTFILE"
