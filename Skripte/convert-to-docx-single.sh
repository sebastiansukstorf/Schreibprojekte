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
mkdir -p "$output_dir"

# YAML-Header (title, subtitle, author) extrahieren
title=$(awk '/^title:/ {gsub(/^title:[[:space:]]*/, "", $0); print; exit}' "$file")
subtitle=$(awk '/^subtitle:/ {gsub(/^subtitle:[[:space:]]*/, "", $0); print; exit}' "$file")
author=$(awk '/^author:/ {gsub(/^author:[[:space:]]*/, "", $0); print; exit}' "$file")

# Fallbacks
[ -z "$title" ] && title="Ohne_Titel"
[ -z "$subtitle" ] && subtitle=""
[ -z "$author" ] && author=""

# Sicherer Dateiname
safe_title=$(echo "$title" | tr ' ' '_')
timestamp=$(date "+%Y-%m-%d_%H-%M")
output_file="${output_dir}/${safe_title}_${timestamp}.docx"

# Pfad zur DOCX-Vorlage
reference_doc="Vorlage/Erzaehlung.docx"

# Optionaler Lua-Filter (falls du author aus dem Fließtext entfernen willst)
lua_filter="Skripte/filter_author_to_variable.lua"

# Konvertierung mit Pandoc
pandoc "$file" \
  -o "$output_file" \
  --from=markdown+hard_line_breaks \
  --metadata title="$title" \
  --metadata subtitle="$subtitle" \
  --metadata author="$author" \
  --reference-doc="$reference_doc" \
  --lua-filter="$lua_filter" \
  --standalone

echo "Erstellt: $output_file"
