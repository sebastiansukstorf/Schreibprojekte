#!/bin/bash

# Pfad zum docx-Ordner relativ zum Skriptverzeichnis
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCX_DIR="$DIR/../docx"

# Prüfen, ob der Ordner existiert
if [ ! -d "$DOCX_DIR" ]; then
  echo "❌ Ordner nicht gefunden: $DOCX_DIR"
  exit 1
fi

# Dateien älter als 1 Tag löschen
find "$DOCX_DIR" -name "*.docx" -type f -mtime +0 -exec rm {} \;

echo "✅ Alle DOCX-Dateien, die älter als ein Tag sind, wurden gelöscht."
