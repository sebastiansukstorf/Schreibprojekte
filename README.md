# ✍️ Meine Schreibprojekte mit Markdown zu DOCX

Dieses Repository bietet ein Skript-basiertes Setup zur Konvertierung von Markdown-Dateien (`*.md`) in ein formatiertes `.docx`-Dokument – inklusive:
- Seitenumbrüchen zwischen Kapiteln
- Sichtbaren Absatzumbrüchen
- Einbindung einer benutzerdefinierten DOCX-Vorlage ("Normseite")
- Metadaten aus der YAML-Datei (`titlepage.yml`)

## 🔧 Voraussetzungen

- [Pandoc](https://pandoc.org/installing.html)
- Python 3 mit Pandoc-Filtersupport
- Lua (für Lua-Filter)
- Optional: `python-docx` (für weiterführende DOCX-Verarbeitung)

## 📂 Struktur

- `03_Content/`: Kapitel als `*.md` im jeweiligen Schreibprojekt
- `Metadaten/titlepage.yml`: Metadaten inkl. `title:`
- `Vorlage/Normseite.docx`: Formatierte Referenzdatei
- `Skripte/convert-to-docx.sh`: Führt alles zusammen
- `docx/`: erzeugte DOCX-Ausgaben im jeweiligen Projektordner

## ▶️ Verwendung

### Zentrale CLI

```bash
uv run manuskript docx
```

Optional mit explizitem Quell- oder Zielordner:

```bash
uv run manuskript docx ../Testprojekt --output docx/versuche
```

Für eine einzelne Datei:

```bash
uv run manuskript single ../Testprojekt/100.md
```

Die aktuell verwendete Konfiguration anzeigen:

```bash
uv run manuskript config
```

### Konfiguration

Die CLI liest standardmäßig die Datei `.manuskript.json` im Repository:

```json
{
  "source": "../Testprojekt",
  "output": "docx"
}
```

Alternativ kann eine andere Konfigurationsdatei verwendet werden:

```bash
uv run manuskript docx --config /pfad/zur/konfiguration.json
```

### Direktes Skript

```bash
bash Skripte/convert-to-docx.sh ../Testprojekt
```
