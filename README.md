# Schreibprojekte

Zentrale Werkzeugbasis für Markdown-Manuskripte und deren Export als formatierte DOCX-Dateien. Konkrete Manuskripte werden in getrennten Projektordnern geführt.

Der Export umfasst Kapitelreihenfolge, Seiten- und Absatzumbrüche, Metadaten sowie die gemeinsame Normseitenvorlage.

## Voraussetzungen

- Python 3.11 oder neuer
- `uv`
- Pandoc

Einrichtung:

```bash
uv sync
```

## Struktur

- `src/manuskript/`: Python-CLI
- `Skripte/`: aktive Shell-Aufrufe für den DOCX-Export
- `ressourcen/`: Normseitenvorlage und Pandoc-Filter
- `projektvorlage/`: empfohlene Struktur neuer Manuskripte
- `docs/`: allgemeine Schreib- und Analysemethoden
- `werkzeuge/`: optionale Vorlese- und Vorlagenpflegewerkzeuge
- `tests/`: automatisierte Tests

## Erwartete Projektstruktur

```text
MeinProjekt/
├── 03_Content/
│   ├── 100.md
│   ├── 101.md
│   └── ...
├── Metadaten/
│   └── titlepage.yml
└── docx/
```

## Verwendung

### Gesamtes Manuskript exportieren

```bash
uv run manuskript docx ../MeinProjekt
```

Ohne Projektpfad wird die Quelle aus `.manuskript.json` verwendet. Ein eigener Zielordner kann angegeben werden:

```bash
uv run manuskript docx ../MeinProjekt --output docx/versuche
```

Für eine einzelne Datei:

```bash
uv run manuskript single ../MeinProjekt/03_Content/100.md
```

### Konfiguration anzeigen

```bash
uv run manuskript config
```

Die CLI liest standardmäßig `.manuskript.json` im Repository:

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

### Direkter Aufruf

```bash
bash Skripte/convert-to-docx.sh ../MeinProjekt
```
