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

# Zielordner für EPUB-Dateien
output_dir="epub"
mkdir -p "$output_dir"

# Titel aus YAML oder Dateiname extrahieren
title=$(awk '/^title:/ {gsub(/^title:[[:space:]]*/, "", $0); print; exit}' "$file")
[ -z "$title" ] && title="$(basename "$file" .md)"
safe_title=$(echo "$title" | tr ' ' '_' | tr -cd '[:alnum:]_')
timestamp=$(date "+%Y-%m-%d_%H-%M")
output_file="${output_dir}/${safe_title}_${timestamp}.epub"

# Optionaler Lua-Filter
lua_filter="Skripte/filter_author_to_variable.lua"

# Coverbild prüfen
cover_path="09_Images/cover_drogentaxi.png"
if [ -f "$cover_path" ]; then
  cover_arg="--epub-cover-image=$cover_path"
else
  echo "⚠️  Kein Coverbild gefunden unter '$cover_path'."
  cover_arg=""
fi

# Pandoc-Konvertierung ohne Inhaltsverzeichnis
pandoc "$file" \
  -o "$output_file" \
  --from=markdown+hard_line_breaks \
  --lua-filter="$lua_filter" \
  $cover_arg \
  --standalone

echo "✅ EPUB erstellt: $output_file"
