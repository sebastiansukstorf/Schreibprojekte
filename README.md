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

Die Bedienung, fachlichen Maßstäbe, Grenzen und geplante Homeserver-Architektur aller Prüfungen sind
in [Lektorats- und Korrektoratsprüfungen](docs/analyse/Lektorats_und_Korrektoratspruefungen.md)
zusammenhängend dokumentiert.

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
`lektorat/szene/<dateiname>-sagte-lektorat.md` im Projekt abgelegt.

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
der Bericht landet als `lektorat/szene/<dateiname>-hlx-lektorat.md` im Projekt.

```bash
uv run manuskript lektorat-hlx ../MeinProjekt/03_Content/101.md
```

Optional kann in `.manuskript.json` ein eigener Abschnitt `hlx_lektorat` mit `base_url`, `model`,
`context_lines` und `batch_size` angelegt werden. Fehlt er, verwendet die Prüfung die allgemeine
Konfiguration aus `lektorat`.

### Rechtschreibung und Zeichensetzung prüfen

Das Korrektorat nutzt die offene LanguageTool-HTTP-API und beschränkt den Bericht auf
Rechtschreibung und Zeichensetzung. Stil- und allgemeine Grammatikhinweise werden ausgefiltert.
Standardmäßig wird aus Datenschutzgründen ein lokal laufender LanguageTool-Server erwartet:

```bash
uv run manuskript korrektorat ../MeinProjekt/03_Content/101.md
```

```json
{
  "korrektorat": {
    "base_url": "http://127.0.0.1:8081",
    "language": "de-DE"
  }
}
```

Der Bericht wird unter `lektorat/szene/<dateiname>-korrektorat.md` abgelegt und
enthält Zeile, Spalte, Originalzeile, Vorschläge und die LanguageTool-Regel-ID. Grundlage ist das
[Amtliche Regelwerk der deutschen Rechtschreibung 2024](https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf);
die technische Prüfung übernimmt das offene [LanguageTool](https://github.com/languagetool-org/languagetool).

### Adjektive und Adverbien lektorieren

Die Wortartenprüfung meldet nur stilistisch erwähnenswerte Adjektive und Adverbien. Sie unterscheidet
zwischen `STREICHEN`, `ERSETZEN` und `BEHALTEN`, zitiert die Originalzeile und gibt einen konkreten
Vorschlag. Figurenstimme und präzise, notwendige Details werden nicht mechanisch geglättet.

```bash
uv run manuskript lektorat-wortarten ../MeinProjekt/03_Content/101.md
```

Der Bericht wird als `lektorat/szene/<dateiname>-adjektive-adverbien-lektorat.md` gespeichert und enthält
außerdem Vorschläge für weitere Lektoratsprüfungen. Eine eigene Modell- und Paketkonfiguration kann
unter `wortarten_lektorat` in `.manuskript.json` hinterlegt werden.

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

### Vollständige Lektoratsarchitektur ausführen

Die drei redaktionellen Ebenen werden mit eigenen Befehlen gestartet. Sie erzeugen strukturierte
Diagnosen und verändern die Manuskriptdateien nicht.

```bash
# einzelne Szene: sieben Prüfmodule
uv run manuskript lektorat-szene ../MeinProjekt/03_Content/205.md

# Teil/Akt anhand numerischer Dateinamen
uv run manuskript lektorat-teil ../MeinProjekt --start 200 --end 299 --label teil_2

# vollständiger Roman
uv run manuskript lektorat-gesamt ../MeinProjekt
```

Mit `--context PFAD` kann eine Story Bible oder ein Ordner mit Markdown-Kontext mitgegeben werden.
Die Ausgaben landen unter `lektorat/szene/`, `lektorat/teile/` und `lektorat/gesamt/`.
Gleichnamige Shell-Skripte unter `Skripte/` sowie VS-Code-Aufgaben stehen ebenfalls bereit.

Szenenberichte beginnen mit einem YAML-Header. Er enthält die im Szenenlektorat ermittelten Angaben
zu Einstieg, Ziel, Konflikt, Dynamik, Wendung, Ausgang, Ende und Funktion. Das Originalmanuskript
wird dafür nicht verändert.

Die gemeinsame Konfiguration kann unter `redaktion` gesetzt und pro Ebene mit `szene_lektorat`,
`teil_lektorat` oder `gesamt_lektorat` überschrieben werden:

```json
{
  "redaktion": {
    "style_profile": "Kurze Sätze und Ellipsen sind erlaubt.",
    "max_manuscript_chars": 300000,
    "max_context_chars": 80000
  }
}
```

Die Zeichenobergrenzen schützen vor einer unbemerkten Überschreitung des Modellkontexts und müssen
zum verwendeten lokalen Modell passen.

### Manuellen Nachtlauf starten

Der Nachtlauf prüft alle Markdown-Dateien unter `03_Content` nacheinander. Pro Datei laufen
Korrektorat, „sagte“-Prüfung, H–L–X, Wortartenprüfung und das vollständige Szenenlektorat. Teil- und
Gesamtromanlektorat gehören bewusst nicht zum Nachtlauf.

```bash
Skripte/lektorat-nacht.sh ../MeinProjekt
```

Das Skript startet den Prozess mit `nohup` im Hintergrund, zeigt Prozess-ID und Logdatei an und
läuft nach dem Schließen des Terminals weiter. Den Fortschritt zeigt beispielsweise:

```bash
tail -f ../MeinProjekt/lektorat/logs/nachtlauf-YYYYMMDD-HHMMSS.log
```

Aktuelle Berichte werden anhand ihres Änderungsdatums übersprungen. Ein abgebrochener Lauf kann
daher mit demselben Befehl fortgesetzt werden. Mit `--force` werden alle Prüfungen wiederholt; mit
`--context PFAD` wird eine Story Bible eingebunden. Die letzte strukturierte Zusammenfassung steht
unter `lektorat/logs/nachtlauf_letzter.md`. Einzelfehler werden protokolliert und stoppen die
restlichen Prüfungen nicht.

Für einen Homeserver müssen Ollama und optional LanguageTool in `.manuskript.json` auf dessen
Adressen zeigen:

```json
{
  "lektorat": {
    "base_url": "http://HOMESERVER-IP:11434",
    "model": "qwen3:8b"
  },
  "korrektorat": {
    "base_url": "http://HOMESERVER-IP:8081",
    "language": "de-DE"
  }
}
```

Die Ports dürfen nicht ungeschützt aus dem Internet erreichbar sein. Im Heimnetz sollte der
Zugriff auf den Manuskriptrechner begrenzt werden; von außen ist ein VPN vorzuziehen.

Projektabhängige Strukturdateien und ein Standardkontext können ebenfalls konfiguriert werden:

```json
{
  "nachtlauf": {
    "exclude": ["050.md", "100.md", "200.md", "300.md", "400.md"],
    "context": "01_Figuren"
  }
}
```

Die Ausschlüsse sind Dateinamen oder Glob-Muster relativ zu `03_Content`. Ein explizites
`--context` beim Start überschreibt den konfigurierten Kontext.
Beim Nachtlauf wird automatisch die `.manuskript.json` im angegebenen Projekt verwendet, sofern
nicht ausdrücklich eine andere Datei mit `--config` gewählt wurde.

### Betrieb mit Mac, NAS, Nextcloud und Homeserver

Die produktive Aufteilung, die WebDAV- und NFS-Pfade, die separate Serverkonfiguration, der
Homestories-Nachtlauf sowie die Regeln für konfliktfreie Ordneränderungen sind unter
[Schreibprojekte auf Mac, NAS und Homeserver](docs/betrieb/Homeserver.md) dokumentiert.

Für die eingerichtete Homestories-Umgebung wird ein abgeschlossener Stand nach der SSH-Anmeldung
beispielsweise mit `homestories-lektorat start 4 5` geprüft. Die erste Zahl benennt den geprüften
Stand, die zweite die Zielüberarbeitung. Status und Log zeigt `homestories-lektorat status`
beziehungsweise `homestories-lektorat log`. Nach einem Abbruch setzt
`homestories-lektorat resume 4` denselben Lauf fort. Ergebnisse liegen ausschließlich unter dem
kleingeschriebenen Projektordner `lektorat/`.

### Überarbeitungsstände nach OpenProject übertragen

Ein Nachtlauf kann mit `--revision STAND --next-revision ZIEL` fest an die Prüfsummen eines
abgeschlossenen Manuskriptstands gebunden werden. Er erzeugt neben den Markdown-Berichten ein
Manifest und normalisierte Befunde in `findings.jsonl`. Erst eine separate Vorschau und ein
bewusster Sync erzeugen daraus hierarchische OpenProject-Arbeitspakete.

```bash
uv run manuskript lektorat-nacht ../MeinProjekt --revision 4 --next-revision 5
uv run manuskript lektorat-nacht ../MeinProjekt --resume 4
uv run manuskript openproject-preview ../MeinProjekt --run 4
uv run manuskript openproject-sync ../MeinProjekt --run 4
```

Der Sync ist idempotent: Bereits übertragene Befunde werden über feste Kennungen erkannt. Nur ein
vollständig erfolgreicher Lauf, dessen Manuskript-Prüfsummen sich während der Ausführung nicht
verändert haben, darf übertragen werden. Konfiguration, Aufgabenmodell und sichere Token-Ablage
beschreibt [Lektoratsbefunde in OpenProject](docs/betrieb/OpenProject.md).

### Direkter Aufruf

```bash
bash Skripte/convert-to-docx.sh ../MeinProjekt
```
