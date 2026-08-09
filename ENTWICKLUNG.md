# Schreibprojekte – Entwicklungsdokumentation

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

Beispiel:

    metadata.yaml
    050.md
    100.md
    101.md
    102.md
    ...
    200.md
    201.md
    ...
    300.md
    301.md
    ...
    400.md

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

`Schreibprojekte` wird die zentrale Werkzeugbasis.

Geplant:

- `uv` für Python und Python-Abhängigkeiten
- Pandoc für Markdown → DOCX
- bestehender Lua-Filter
- bestehende Normseiten-DOCX mit Kopf- und Fußzeile
- Lektorat und Textanalyse

Pandoc wird beibehalten. Die bereits funktionierende Pandoc-/Lua-/Normseitenlogik soll zunächst nicht verändert werden.

EPUB wird nicht mehr unterstützt.

## Geplante CLI

Zunächst:

    manuskript docx

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
- [ ] bestehenden DOCX-Workflow dokumentieren

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

## Entwicklungsregel

Erst testen, dann vereinfachen.

Funktionierende Pandoc-, Filter- oder Normseitenfunktionalität wird nicht neu implementiert, solange dafür kein konkreter Grund besteht.