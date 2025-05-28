# ✍️ Meine Schreibprojekte mit Mardown to docx

Dieses Repository bietet ein Skript-basiertes Setup zur Konvertierung von Markdown-Dateien (`*.md`) in ein formatiertes `.docx`-Dokument – inklusive:
- Seitenumbrüchen zwischen Kapiteln
- Sichtbaren Absatzumbrüchen
- Einbindung einer benutzerdefinierten DOCX-Vorlage ("Normseite")
- Metadaten aus YAML-Datei (`titlepage.yml`)

## 🔧 Voraussetzungen

- [Pandoc](https://pandoc.org/installing.html)
- Python 3 mit Pandoc-Filtersupport
- Lua (für Lua-Filter)
- Optional: `python-docx` (für weiterführende DOCX-Verarbeitung)

## 📂 Struktur

- `Content/`: Kapitel als `*.md`
- `Metadaten/titlepage.yml`: Metadaten inkl. `title:`
- `Vorlage/Normseite.docx`: Formatierte Referenzdatei
- `Skripte/convert-to-docx.sh`: Führt alles zusammen

## ▶️ Verwendung

```bash
bash Skripte/convert-to-docx.sh
