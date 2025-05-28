#!/bin/bash

echo "🔧 Setup gestartet..."

# Wechsle ins Verzeichnis des Skripts
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# 1. Ausführbarkeitsrechte für Skripte setzen
echo "🛠 Setze Ausführbarkeitsrechte für Shell-Skripte..."
chmod +x Skripte/*.sh

# 2. Prüfe auf Python
if command -v python3 &>/dev/null; then
    echo "✅ Python ist installiert: $(python3 --version)"
else
    echo "❌ Python ist nicht installiert. Bitte installiere Python 3."
fi

# 3. Prüfe auf Pandoc
if command -v pandoc &>/dev/null; then
    echo "✅ Pandoc ist installiert: $(pandoc --version | head -n 1)"
else
    echo "❌ Pandoc ist nicht installiert. Bitte installiere Pandoc."
fi

# 4. Prüfe ob Referenz-DOCX vorhanden ist
if [ -f "Vorlage/Normseite.docx" ]; then
    echo "✅ Referenz-Dokument gefunden: Vorlage/Normseite.docx"
else
    echo "⚠️  Referenz-Dokument fehlt: Vorlage/Normseite.docx"
fi

echo "✅ Setup abgeschlossen."
