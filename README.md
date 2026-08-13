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
eingerichtet werden; eine projektlokale `keybindings.json` wird von VS Code nicht geladen.

Die Prüfung filtert die Fundstellen samt Dialogumgebung zunächst lokal vor und sendet nur diese
Ausschnitte an eine Ollama-Instanz. Der vollständige Text wird nicht übertragen. Der Bericht nennt
zu jeder Zeilennummer auch die unveränderte zitierte Textstelle. Sie wird lokal aus der Markdown-
Datei übernommen und nicht vom Modell erzeugt.

Die Ollama-Adresse, das Modell und die Zahl der Kontextzeilen stehen in `.manuskript.json`:

```json
{
  "lektorat": {
    "provider": "ollama",
    "base_url": "http://127.0.0.1:11434",
    "model": "qwen3:4b",
    "context_lines": 4,
    "batch_size": 4
  }
}
```

### Erklärungen mit H–L–X prüfen

Das H–L–X-Lektorat beurteilt alle inhaltlichen Zeilen danach, ob eine Information besser szenisch
vermittelt werden sollte (H), als knapper notwendiger Satz bestehen bleibt (L) oder Dialog,
Handlung beziehungsweise Reaktion nur noch einmal erklärt (X). Das Manuskript bleibt unverändert;
der Bericht landet als `Lektorat/<dateiname>-hlx-lektorat.md` im Projekt.

```bash
uv run manuskript lektorat-hlx ../MeinProjekt/03_Content/101.md
```

Optional kann in `.manuskript.json` ein eigener Abschnitt `hlx_lektorat` mit `base_url`, `model`,
`context_lines` und `batch_size` angelegt werden. Fehlt er, verwendet die Prüfung die allgemeine
Konfiguration aus `lektorat`.

Auf einem Apple-Silicon-Rechner mit 16 GB ist `qwen3:4b` zwar schneller, hält das verlangte
strukturierte Ausgabeformat aber nicht zuverlässig ein. Für dieses Lektorat ist deshalb
`qwen3:8b` voreingestellt. Das Modell bleibt zwischen den Paketen 15 Minuten im Speicher. Als
anderer lokaler Server kann LM Studio verwendet werden,
seine OpenAI-kompatible Schnittstelle benötigt jedoch eine eigene Anbindung und bietet bei demselben
Modell keinen grundsätzlichen Qualitätsvorteil gegenüber Ollama.

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
