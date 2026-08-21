# Lektoratsbefunde in OpenProject

## Verifizierter Ist-Stand

- Instanz: `https://projects.sukstorf.de`
- OpenProject: 14.6.3, API v3
- dauerhaftes Projekt: `Homestories`, ID 6, Kennung `homestories`, nicht öffentlich
- Arbeitspakettyp: `Aufgabe`
- Authentifizierung: API-Token über Basic Auth mit Benutzername `apikey`
- Token-Datei: `/home/sebastian/.config/schreibprojekte/openproject.env`, Dateimodus `600`
- Cloudflare: API-Aufrufe verwenden den eindeutigen User-Agent `Schreibprojekte/0.1 OpenProject-API`

Die Verbindung, Projektsuche, Typabfrage und Projektanlage wurden mit dem produktiven Python-Client
erfolgreich geprüft. Versionen und Befundaufgaben werden erst nach einem abgeschlossenen
Revisionslauf und bestätigter Vorschau erzeugt.

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

## Projektübergreifendes Zielmodell

Die OpenProject-Struktur wird nicht auf Homestories fest verdrahtet. Für jedes Schreibprojekt gilt:

```text
OpenProject-Projekt <title aus Metadaten/titlepage.yml>
└── Version Überarbeitung <Stand>
    └── Kapitel <Kapitelnummer oder Kapitelbezeichnung>
        └── Datei <Dateinummer>
            ├── Prüfschritt: Korrektorat
            │   └── einzelne zeilenbezogene Befunde
            ├── Prüfschritt: sagte
            │   └── einzelne zeilenbezogene Befunde
            ├── Prüfschritt: H–L–X
            │   └── einzelne zeilenbezogene Befunde
            ├── Prüfschritt: Wortarten
            │   └── einzelne zeilenbezogene Befunde
            └── Prüfschritt: Szenenlektorat
                └── einzelne modulbezogene Befunde
```

Die Version bildet den Überarbeitungsstand ab. Kapitel, Datei und Prüfschritt sind hierarchische
Arbeitspakete; konkrete Befunde bleiben die kleinsten bearbeitbaren Aufgaben. Hat ein kurzer Text
nur ein Kapitel, wird trotzdem eine eindeutige Kapitelebene angelegt, damit alle Projekte dieselbe
Struktur verwenden.

Projektname und Autor stammen aus den Projektmetadaten. Ordnername, Dateiname und YAML-Titel werden
vor dem Sync validiert; fehlende oder widersprüchliche Angaben stoppen nur die OpenProject-Übergabe,
nicht die lokalen Lektoratsberichte.

Kontextmerkmale aus der inhaltlichen Prüfung werden bevorzugt in einem benutzerdefinierten
OpenProject-Feld `Lektorats-Tags` gespeichert. Das Skript muss das Feld über das API-Schema des
Arbeitspakettyps ermitteln. Existiert es nicht, werden die Tags nachvollziehbar in die Beschreibung
geschrieben. Geeignete Angaben sind unter anderem Figur, Ort, Perspektive, Prüfmodul, Relevanz und
Art des Eingriffs.

Jede Ebene erhält eine stabile Herkunftskennung. Ein erneuter Sync aktualisiert vorhandene
Kapitel-, Datei-, Prüfschritt- und Befundaufgaben und legt keine Dubletten an. OpenProject-Ausfälle
dürfen weder Manuskript noch lokale Lektoratsergebnisse beeinflussen.

## Pilot: Ein unmögliches Eheversprechen

Der erste projektübergreifende Test verwendet das lokale/NAS-Projekt `eheversprechen`:

- Projekttitel aus `Metadaten/titlepage.yml`: `Ein unmögliches Eheversprechen`
- geprüfter Überarbeitungsstand: `2`
- aktuelle Dateien: `101.md` bis `108.md`
- ausgeschlossene Sicherungsfassungen: `_*.md`
- OpenProject-Projekt wird nur angelegt, wenn die Vorschau vollständig und der Lauf konsistent ist
- OpenProject-Benachrichtigungen sollen beim ersten Sync nach Möglichkeit unterdrückt werden

Die im Ist-Stand vorhandene Homestories-Struktur `Version → Szene → Befund` bleibt produktiv. Die
zusätzlichen Ebenen `Kapitel → Datei → Prüfschritt` sind die mit Eheversprechen zu erprobende
konzeptionelle Erweiterung und dürfen erst nach erfolgreichem Preview-Test synchronisiert werden.

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
denselben Stand. Fertige Berichte werden atomar veröffentlicht; ein abgebrochener Bericht bleibt
als `.md.partial` erkennbar und zählt nicht als abgeschlossen. Die Arbeitskopie wird nur nach einem
vollständig erfolgreichen Lauf entfernt. Anschließend werden die Originale
erneut geprüft. Wurde währenddessen geschrieben oder synchronisiert, erhält der Lauf den Status
`attention` und darf nicht nach OpenProject übertragen werden.

## Abbruch und Wiederaufnahme

Der Start über den Server-Wrapper läuft mit `nohup` und übersteht deshalb eine getrennte
SSH-Verbindung. Fehler einer einzelnen Prüfung werden protokolliert; die übrigen Prüfungen laufen
weiter. Nach einem Prozess-, Container- oder Serverabbruch zuerst den Status prüfen und dann
denselben Stand fortsetzen:

```bash
homestories-lektorat status
homestories-lektorat log
homestories-lektorat resume 4
```

`resume 4` verwendet exakt die beim ursprünglichen Start erzeugte Arbeitskopie. Bereits fertige
Berichte werden übersprungen, fehlende oder nur teilweise geschriebene Berichte erneut ausgeführt.
Es wird dabei weder ein neuer Stand noch eine neue Laufkennung erzeugt. Ein bereits vollständiger
Lauf kann nicht versehentlich fortgesetzt werden. Während des gesamten Laufs sollte
`03_Content` unverändert bleiben, damit der abschließende Prüfsummenvergleich erfolgreich ist.

## Welche Befunde werden Aufgaben?

- Korrektorat: Rechtschreibung, Grammatik und Zeichensetzung
- „sagte“-Prüfung: nur `STREICHEN` bei tatsächlicher wörtlicher Rede; Kandidaten werden pro Szene
  als zeilenspezifische Checkliste gebündelt
- H–L–X: nur `H` und `X`; korrekte `L`-Zeilen entfallen
- Wortarten: nur `STREICHEN` und `ERSETZEN`
- Szenenlektorat: die ausdrücklich ausgegebenen Befunde der sieben Module

Standardmäßig werden nur Befunde ab Relevanz `mittel` übernommen. Konkrete Grammatik-,
Zeichensetzungs- und Rechtschreibbefunde bleiben Einzelaufgaben. Unspezifische Hinweise wie
„Möglicher Tippfehler gefunden“ werden pro Szene als Checkliste gebündelt. Ein Wert von `0` für
`max_tasks_per_scene` deaktiviert die Begrenzung, damit keine Befunde willkürlich abgeschnitten
werden. Die vollständigen Berichte bleiben unabhängig von der Aufgabenauswahl erhalten.

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
    "max_tasks_per_scene": 0,
    "bundle_sagte_per_scene": true,
    "bundle_generic_typos_per_scene": true
  }
}
```

`project_identifier` ist die stabile, kleingeschriebene OpenProject-Kennung. Das Projekt existiert
bereits und wird beim Sync wiederverwendet. Bei weiteren Romanprojekten kann derselbe Client ein
fehlendes, nicht öffentliches Projekt anlegen. Neue Überarbeitungen werden als Versionen des
jeweiligen dauerhaften Projekts geführt.

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
- Metadaten bestimmen den Projekttitel; Geheimnisse und lokale `.env`-Dateien werden nie übertragen.
- Sicherungsfassungen wie `_*.md` müssen explizit von Snapshot und Prüfung ausgeschlossen sein.
- `resume` führt den vorhandenen Lauf fort. Nur ein bewusstes neues `start` für denselben Textstand
  erzeugt ein neues Laufverzeichnis; identische Befunde bleiben über ihren Fingerprint erkennbar.

Technische Grundlage ist die OpenProject API v3 mit Projekten, Versionen, Arbeitspaketen und
Elternbeziehungen. Die eingerichtete OpenProject-Version 14.6.3 akzeptiert den API-Token über Basic
Auth mit dem festen Benutzernamen `apikey`; der Token bleibt dabei das Passwort der API-Anfrage.
Der Client sendet einen eindeutigen `Schreibprojekte`-User-Agent, damit die vorgeschaltete
Cloudflare-Regel legitime API-Aufrufe von anonymen Bot-Anfragen unterscheiden kann.
