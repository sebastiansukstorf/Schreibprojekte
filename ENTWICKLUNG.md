# Schreibprojekte – Entwicklungsdokumentation

Stand: 11. August 2026

## Dokumentationsrahmen

Dieses Dokument fasst ausschließlich Meta-Informationen zu Organisation, Werkzeugen, Arbeitsabläufen und Entwicklungsentscheidungen der Schreibprojekte zusammen. Inhaltliche Angaben zu Manuskripten, Figuren, Handlung oder einzelnen Textpassagen gehören nicht hierher.

## Ziel

Eine einfache, robuste und langfristig lesbare Schreibumgebung.

## Grundprinzipien

- Markdown (`.md`) ist das maßgebliche Originalformat.
- Die Texte müssen unabhängig von Obsidian, VS Code, GitHub oder anderen Programmen lesbar bleiben.
- Obsidian ist der leichte, ablenkungsarme Schreibeditor.
- VS Code ist die technische Werkbank.
- WebDAV/Nextcloud sichert den laufenden Arbeitsstand auf der NAS.
- GitHub dient zusätzlich der Versionierung und Sicherung.
- Code und Manuskripte werden strikt getrennt.
- Gemeinsame Funktionalität existiert nur einmal im Repository `Schreibprojekte`.
- Projektspezifischer Code wird nicht in einzelne Manuskripte kopiert.

## Manuskriptstruktur

Ein Schreibprojekt besteht im Kern aus normalen Markdown-Dateien.

### Entwicklungsmethode

- Die Texte werden nach der Schneeflockenmethode entwickelt.
- Die dramaturgische Grundstruktur folgt der Dreiaktstruktur.
- Der erste Akt umfasst 10 Szenen.
- Der zweite Akt umfasst 20 Szenen.
- Der dritte Akt umfasst 10 Szenen.
- Auslösendes Moment, Plot Point I, Midpoint und Plot Point II dienen als zentrale dramaturgische Orientierungspunkte.

### Poetologisches Leitmotiv

> Wild im Denken. Klar in der Form.

Freie Einfälle und klare Gestaltung bilden keinen Widerspruch, sondern zwei aufeinanderfolgende Bewegungen des Schreibprozesses. Die Struktur soll das kreative Material nicht domestizieren. Sie hilft dabei, es zu bewahren, auszuwählen und in eine lesbare Form zu bringen.

Die daraus abgeleiteten persönlichen Arbeitsgrundsätze stehen in [Zehn Regeln für wildes Denken und klare Form](docs/methoden/Zehn_Regeln_fuer_wildes_Denken_und_klare_Form.md).

Für die konkrete Szenen- und Dialogarbeit gilt ergänzend die Methode [Action Writing](docs/methoden/Action_Writing.md). Sie verbindet dialoggetriebenes Erzählen nach Higgins mit der Präzision und erzählerischen Ökonomie Leonards. Die Gewichtung beschreibt dabei eine stilistische Entscheidungsregel und keinen rechnerischen Dialoganteil.

Beispiel:

    03_Content/
        050.md
        100.md
        101.md
        ...
        200.md
        ...
        300.md
        ...
        400.md
    Metadaten/
        titlepage.yml
    docx/

### Nummerierung

- `000–099`: Vorspann
- `100–199`: erster Teil
- `200–299`: zweiter Teil
- `300–399`: dritter Teil
- `400–499`: Nachspann
- Die drei Hauptbereiche entsprechen der Drei-Akt-Struktur.
- Der Dateiname bestimmt die technische Reihenfolge.
- Die sichtbare Kapitelnummer oder Überschrift steht als Markdown-Überschrift in der Datei, z. B. `# 1`.

## Architektur

### Schreiben

Obsidian bearbeitet direkt die Markdown-Dateien des jeweiligen Vaults.

### Entwicklung

VS Code verwendet einen Multi-Root-Workspace mit:

1. dem jeweiligen Test-/Schreibprojekt
2. dem Repository `Schreibprojekte`

### Werkzeuge

`Schreibprojekte` ist die zentrale Werkzeugbasis:

- `uv` für Python und Python-Abhängigkeiten
- Pandoc für Markdown → DOCX
- Python-CLI unter `src/manuskript`
- Exportskripte unter `Skripte`
- Normseiten-DOCX und Filter unter `ressourcen`
- allgemeine Methoden unter `docs`
- optionale Hilfsmittel unter `werkzeuge`

Pandoc wird beibehalten. Die bereits funktionierende Pandoc-/Lua-/Normseitenlogik soll zunächst nicht verändert werden.

EPUB wird nicht mehr unterstützt.

## CLI

    manuskript docx

Außerdem:

    manuskript single 101.md
    manuskript config

Später:

    manuskript lektorat 101.md

Weitere Analysefunktionen nur bei tatsächlichem Bedarf.

## Sicherheitsprinzip

Die Markdown-Dateien haben Vorrang vor allen Werkzeugen.

`Schreibprojekte` darf Manuskriptdateien lesen und verarbeiten, aber technische Werkzeuge sollen keine Git-Reparaturen oder riskanten Git-Operationen am Manuskript durchführen.

Insbesondere keine automatischen:

- `git reset`
- `git clean`
- `git restore`
- `git checkout`
- automatischen Merge-Versuche

## Testumgebung

`Testprojekt` dient als ungefährliches Testmanuskript.

Es wird verwendet, um Änderungen an `Schreibprojekte` zu testen, bevor bestehende Manuskripte umgestellt werden.

## Vorgehen

### Phase 1 – Grundstruktur

- [x] Test-Vault anlegen
- [x] Multi-Root-Workspace in VS Code anlegen
- [x] `Schreibprojekte` separat klonen
- [x] Entwicklungsdokumentation anlegen
- [x] bestehenden DOCX-Workflow dokumentieren

### Phase 2 – uv und CLI

- [x] `Schreibprojekte` als uv-Projekt einrichten
- [x] zentrale CLI erstellen
- [x] aktuellen Manuskriptordner als Eingabe verwenden
- [x] `manuskript docx` implementieren
- [x] Standardkonfiguration über `.manuskript.json` ergänzen
- [x] optionale `--output`- und `--config`-Parameter ergänzen

### Phase 3 – Pandoc-Test

- [x] Testprojekt als DOCX erzeugen
- [x] bestehenden Lua-Filter verwenden
- [x] bestehende Normseitenvorlage verwenden
- [x] Ergebnis mit bisherigem Export vergleichen
- [x] DOCX-Ausgaben landen im jeweiligen Projektordner (beispielsweise `Testprojekt/docx`)

### Phase 4 – Bereinigung

Erst nach erfolgreichem Test:

- [x] alten duplizierten Workflow entfernen
- [x] EPUB-Funktionalität entfernen
- [x] nicht mehr benötigte Projektstruktur aus `Schreibprojekte` entfernen
- [x] README für die tatsächliche Benutzung überarbeiten

### Phase 5 – Trennung und Vereinfachung

- [x] projektspezifische Inhalte aus `Schreibprojekte` auslagern
- [x] Drogentaxi als eigenes Schreibprojekt unter `Schreiben` anlegen
- [x] allgemeine Methoden unter `docs` zusammenführen
- [x] Ressourcen und Projektvorlagen eindeutig trennen
- [x] veraltete und defekte Skripte entfernen
- [x] Python-CLI nach `src/manuskript` verschieben
- [x] DOCX-Export mit `Homestories` erfolgreich prüfen

## Entwicklungsregel

Erst testen, dann vereinfachen.

Funktionierende Pandoc-, Filter- oder Normseitenfunktionalität wird nicht neu implementiert, solange dafür kein konkreter Grund besteht.
