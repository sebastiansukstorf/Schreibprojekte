#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.."
mkdir -p docx

# Metadaten prüfen
if [ ! -f "Metadaten/titlepage.yml" ]; then
  echo "❌ Metadaten-Datei fehlt: Metadaten/titlepage.yml"
  exit 1
fi

# Titel & Zeitstempel
TITLE=$(grep '^title:' Metadaten/titlepage.yml | sed 's/title:[[:space:]]*//;s/ /_/g')
TIMESTAMP=$(date +"%Y%m%d_%H_%M")
OUTFILE="docx/${TITLE}_${TIMESTAMP}.docx"

# Nur nummerische Markdown-Dateien aus 03_Content verarbeiten
TMPFILE=$(mktemp)
for f in 03_Content/[0-9]*.md; do
  if [[ "$f" =~ 03_Content/[0-9]+\.md$ ]]; then
    cat "$f"
    echo -e "\n"
  fi
done > "$TMPFILE"

# 📤 Konvertieren mit Pandoc
pandoc "$TMPFILE" \
  --from=markdown+hard_line_breaks \
  --lua-filter=Skripte/insert-visible-dummy-parabreak.lua \
  --metadata-file=Metadaten/titlepage.yml \
  --reference-doc=Vorlage/Normseite.docx \
  -o "$OUTFILE"

rm "$TMPFILE"
echo "✅ Exportiert nach: $OUTFILE"
