#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DOCX_DIR="$DIR/../docx"
EPUB_DIR="$DIR/../epub"

# Prüfen und löschen
for FOLDER in "$DOCX_DIR" "$EPUB_DIR"; do
  if [ -d "$FOLDER" ]; then
    find "$FOLDER" -type f \( -name "*.docx" -o -name "*.epub" \) -mtime +0 -exec rm {} \;
    echo "✅ Alte Dateien aus $FOLDER gelöscht."
  else
    echo "❌ Ordner nicht gefunden: $FOLDER"
  fi
done
