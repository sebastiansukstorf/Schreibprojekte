#!/bin/bash

# Datei als Argument übergeben
file="$1"

# Überprüfen, ob eine Datei angegeben wurde
if [ -z "$file" ]; then
  echo "Bitte gib eine Markdown-Datei an."
  exit 1
fi

# Prüfen, ob Datei existiert
if [ ! -f "$file" ]; then
  echo "Datei nicht gefunden: $file"
  exit 1
fi

# Zielordner für DOCX-Dateien
output_dir="docx"

# Ordner anlegen, falls er nicht existiert
mkdir -p "$output_dir"

# YAML-Header (title und subtitle) extrahieren
title=$(awk '/^title:/ {gsub(/^title:[[:space:]]*/, "", $0); print; exit}' "$file")
subtitle=$(awk '/^subtitle:/ {gsub(/^subtitle:[[:space:]]*/, "", $0); print; exit}' "$file")

# Fallback, falls Metadaten nicht gesetzt sind
[ -z "$title" ] && title="Ohne_Titel"
[ -z "$subtitle" ] && subtitle=""

# Leerzeichen durch Unterstriche für Dateiname ersetzen
safe_title=$(echo "$title" | tr ' ' '_')

# Zeitstempel im Format YYYY-MM-DD_HH-MM
timestamp=$(date "+%Y-%m-%d_%H-%M")

# Ziel-Dateiname mit Zeitstempel
output_file="${output_dir}/${safe_title}_${timestamp}.docx"

# Pfad zur Word-Vorlage
reference_doc="Vorlage/Erzaehlung.docx"

# Konvertierung mit pandoc inkl. Metadaten und Vorlage
pandoc "$file" \
  -o "$output_file" \
  --from=markdown+hard_line_breaks \
  --lua-filter=Skripte/insert-visible-dummy-parabreak.lua \
  --metadata title="$title" \
  --metadata subtitle="$subtitle" \
  --reference-doc="$reference_doc" \
  --standalone

echo "Erstellt: $output_file"
