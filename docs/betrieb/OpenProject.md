# Lektoratsbefunde in OpenProject

## Zielbild

`Homestories` bleibt ein dauerhaftes OpenProject-Projekt. Für jede neue Arbeitsrunde wird eine
Version angelegt. Ein Nachtlauf des abgeschlossenen Stands 4 erzeugt beispielsweise Aufgaben für
die Version `Überarbeitung 5`.

```text
OpenProject-Projekt Homestories
└── Version Überarbeitung 5
    ├── Szene 101 – Überarbeitung 5
    │   ├── [101:12] Zeichensetzung prüfen
    │   ├── [101:38] H–L–X prüfen
    │   └── [101:71] Perspektive prüfen
    └── Szene 102 – Überarbeitung 5
        └── …
```

Die Aufgaben enthalten Originalpfad, Zeile, unverändertes Zitat, Diagnose, Empfehlung,
Dateiprüfsumme und Laufkennung. Sie verändern das Manuskript nicht.

## Revisionsgebundener Nachtlauf

```bash
homestories-lektorat start 4 5
```

`4` ist der gerade abgeschlossene und geprüfte Textstand. `5` ist die OpenProject-Zielversion für
die anschließende Überarbeitung. Der Lauf schreibt nicht in die allgemeinen Szenenberichte,
sondern in ein unveränderliches Verzeichnis:

```text
lektorat/ueberarbeitungen/4/20260816-220000-a1b2c3d4/
├── manifest.json
├── szene/
├── findings.jsonl
└── zusammenfassung.md
```

`manifest.json` enthält SHA-256-Prüfsummen aller berücksichtigten Manuskriptdateien. Beim Start wird
außerdem unter `lektorat/.arbeitskopien/` eine temporäre, von Obsidian ausgeblendete Momentaufnahme
angelegt. Alle Prüfungen lesen ausschließlich diese Momentaufnahme und sehen damit garantiert
denselben Stand. Nach einem regulären Lauf wird sie entfernt. Anschließend werden die Originale
erneut geprüft. Wurde währenddessen geschrieben oder synchronisiert, erhält der Lauf den Status
`attention` und darf nicht nach OpenProject übertragen werden.

## Welche Befunde werden Aufgaben?

- Korrektorat: Rechtschreibung, Grammatik und Zeichensetzung
- „sagte“-Prüfung: nur `STREICHEN`
- H–L–X: nur `H` und `X`; korrekte `L`-Zeilen entfallen
- Wortarten: nur `STREICHEN` und `ERSETZEN`
- Szenenlektorat: die ausdrücklich ausgegebenen Befunde der sieben Module

Standardmäßig werden nur Befunde ab Relevanz `mittel` und höchstens 25 Aufgaben pro Szene
übernommen. Die vollständigen Berichte bleiben unabhängig von dieser Begrenzung erhalten.

## Vorschau und Synchronisierung

Nach einem erfolgreichen Nachtlauf zuerst nur die Vorschau erzeugen:

```bash
homestories-lektorat preview 4
```

Die Vorschau verändert OpenProject nicht. Sie zählt Aufgaben nach Szene und Prüfart und liegt
zusätzlich als `openproject-vorschau.md` im Laufverzeichnis.

Erst nach der Kontrolle synchronisieren:

```bash
homestories-lektorat sync 4
```

Jeder Aufgabenbefund enthält eine nicht veränderliche Kennung `LKT-…`. Vor dem Anlegen werden
vorhandene Arbeitspakete abgefragt. Derselbe Lauf kann deshalb erneut synchronisiert werden, ohne
doppelte Befundaufgaben anzulegen. Szenen-Sammelaufgaben erhalten eine eigene Kennung `LKTSZ-…`.

## Konfiguration

Die projektbezogenen, nicht geheimen Einstellungen gehören in die Serverkonfiguration:

```json
{
  "openproject": {
    "base_url": "https://projects.sukstorf.de",
    "auth_scheme": "basic",
    "project_identifier": "homestories",
    "project_name": "Homestories",
    "create_project_if_missing": true,
    "version_prefix": "Überarbeitung",
    "work_package_type": "Aufgabe",
    "minimum_relevance": "mittel",
    "max_tasks_per_scene": 25
  }
}
```

`project_identifier` ist die stabile, kleingeschriebene OpenProject-Kennung. Das Projekt wird nur
angelegt, wenn es noch nicht existiert. Danach werden neue Überarbeitungen als Versionen desselben
Projekts geführt.

## API-Zugang sicher hinterlegen

Für den Import wird ein eigener OpenProject-Benutzer mit den minimal benötigten Projekt- und
Arbeitspaketrechten empfohlen. Sein API-Token wird weder im Chat noch im Vault oder Git abgelegt.

Auf dem Homeserver:

```bash
mkdir -p /home/sebastian/.config/schreibprojekte
chmod 700 /home/sebastian/.config/schreibprojekte
nano /home/sebastian/.config/schreibprojekte/openproject.env
chmod 600 /home/sebastian/.config/schreibprojekte/openproject.env
```

Inhalt:

```text
OPENPROJECT_URL=https://projects.sukstorf.de
OPENPROJECT_API_TOKEN=HIER_DAS_API_TOKEN
```

Der Server-Wrapper liest diese Datei erst für `sync`. Vorschau und Nachtlauf benötigen keinen
OpenProject-Zugang.

## Fehler- und Sicherheitsregeln

- Nur Läufe mit Status `complete` und unverändertem Quellen-Digest dürfen synchronisiert werden.
- Ein OpenProject-Ausfall beeinflusst die abgeschlossenen Lektoratsberichte nicht.
- Zeilennummer und Originalzitat werden gemeinsam gespeichert, weil Zeilen bei der nächsten
  Überarbeitung wandern können.
- OpenProject-Aufgaben sind Arbeitsaufträge, keine automatischen Textänderungen.
- Ein erneuter Lauf für denselben Textstand erhält ein neues Laufverzeichnis; identische Befunde
  bleiben über ihren Fingerprint erkennbar.

Technische Grundlage ist die OpenProject API v3 mit Projekten, Versionen, Arbeitspaketen und
Elternbeziehungen. Die eingerichtete OpenProject-Version 14.6.3 akzeptiert den API-Token über Basic
Auth mit dem festen Benutzernamen `apikey`; der Token bleibt dabei das Passwort der API-Anfrage.
