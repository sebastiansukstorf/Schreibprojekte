#!/bin/bash

# Absoluten Pfad zur Projekt-Root ermitteln (Skript-Ordner = Skripte)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# .env laden (aus Projekt-Root)
set -a
source "$PROJECT_ROOT/.env"
set +a

# Dateiname abfragen
read -p "📄 Gib den Namen der Markdown-Datei in 03_Content/ ein (z. B. 101.md): " dateiname

# Python-Skript aufrufen
python3 "$SCRIPT_DIR/lektorat.py" "$dateiname"
