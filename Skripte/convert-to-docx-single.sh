#!/bin/bash

# 📂 Arbeitsverzeichnis
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.."

# 📄 Eingabedatei prüfen
INPUT="$1"
if [ ! -f "$INPUT" ]; then
  echo "❌ Eingabedatei nicht gefunden: $INPUT"
  exit 1
fi

# 🧠 Titel aus YAML Header extrahieren
TITLE=$(grep '^title:' "$INPUT" | sed 's/title:[[:space:]]*//;s/ /_/g')
if [ -z "$TITLE" ]; then
  TITLE=$(basename "$INPUT" .md)
fi

# 🕒 Zeitstempel & Ausgabe
TIMESTAMP=$(date +"%Y%m%d_%H_%M")
OUTFILE="docx/${TITLE}_${TIMESTAMP}.docx"
mkdir -p docx

# 🐍 Python für Pandoc-Filter
export PANDOC_PYTHON=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3

# 🛠️ Konvertierung
pandoc "$INPUT" \
  --from=markdown+hard_line_breaks \
  --lua-filter=Skripte/insert-visible-dummy-parabreak.lua \
  --filter=Skripte/insert-pagebreaks.py \
  --reference-doc=Vorlage/Normseite.docx \
  -o "$OUTFILE"

echo "✅ Exportiert nach: $OUTFILE"
