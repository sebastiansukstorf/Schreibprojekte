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

### „sagte“ in Dialogen lektorieren

Die ausgewählte Markdown-Datei wird ausschließlich darauf geprüft, ob Sprecherzuordnungen mit
„sagte“ nötig sind. Das Manuskript bleibt unverändert; das Ergebnis wird standardmäßig als
`Lektorat/<dateiname>-sagte-lektorat.md` im Projekt abgelegt.

```bash
uv run manuskript lektorat ../MeinProjekt/03_Content/100.md
```

In VS Code kann die Aufgabe `Lektorat starten` über `Tasks: Run Task` für die aktuell geöffnete
Markdown-Datei aufgerufen werden. Ein Tastenkürzel muss in den globalen VS-Code-Tastenkürzeln
eingerichtet werden; eine projektlokale `keybindings.json` wird von VS Code nicht geladen. Die
Funktion nutzt die lokal angemeldete Codex-CLI und benötigt daher eine Internetverbindung.

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
