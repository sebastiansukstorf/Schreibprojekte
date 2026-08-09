#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCX_DIR="$DIR/../docx"

if [ -d "$DOCX_DIR" ]; then
  find "$DOCX_DIR" -type f -name "*.docx" -mtime +0 -exec rm {} \;
  echo "✅ Alte DOCX-Dateien aus $DOCX_DIR gelöscht."
else
  echo "❌ Ordner nicht gefunden: $DOCX_DIR"
fi
