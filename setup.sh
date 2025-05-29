#!/bin/bash

# 🔧 Skripte ausführbar machen
chmod +x Skripte/convert-to-docx.sh
chmod +x Skripte/convert-to-docx-single.sh
chmod +x Skripte/convert-text-to-docx.sh

# 📁 DOCX-Zielordner anlegen, falls nicht vorhanden
mkdir -p docx

# 🧪 Prüfen, ob pandoc vorhanden ist
if ! command -v pandoc &> /dev/null; then
  echo "❌ Pandoc ist nicht installiert. Bitte installiere es mit 'brew install pandoc' oder über https://pandoc.org/installing.html"
  exit 1
fi

# 🐍 Prüfen, ob python vorhanden ist
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 ist nicht installiert. Bitte installiere es über https://www.python.org/downloads/"
  exit 1
fi

# ✅ Alles bereit
echo "✅ Setup abgeschlossen. Du kannst nun die Tasks in VS Code ausführen."
