#!/bin/bash

# ✅ Datei muss übergeben werden
if [ -z "$1" ]; then
  echo "❌ Bitte gib eine .md-Datei an."
  exit 1
fi

MD_FILE="$1"

# 📁 Zielordner sicherstellen
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.."
mkdir -p docx

# 📛 Dateiname ohne Pfad und Erweiterung extrahieren
BASENAME=$(basename "$MD_FILE" .md)
TIMESTAMP=$(date +"%Y%m%d_%H_%M")
OUTFILE="docx/${BASENAME}_${TIMESTAMP}.docx"

# 📤 Konvertieren mit YAML-Header der Datei
pandoc "$MD_FILE" \
  --from=markdown+hard_line_breaks \
  --lua-filter=Skripte/insert-visible-dummy-parabreak.lua \
  --filter=Skripte/insert-pagebreaks.py \
  --reference-doc=Vorlage/Normseite.docx \
  -o "$OUTFILE"

echo "✅ Exportiert nach: $OUTFILE"
