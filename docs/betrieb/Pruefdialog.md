# Interaktiver Prüfungsdialog

Der Prüfungsdialog ist vom Nachtlauf unabhängig. Er dient für bewusst gestartete Einzelprüfungen
und für die Pflege lernender Wörterbücher. Er verändert Manuskripte nur bei einer ausdrücklich
bestätigten Wörterbuch-Ersetzung.

```bash
schreibprojekte-dialog
```

Auf dem Homeserver wird der Starter einmalig in den persönlichen Suchpfad verlinkt:

```bash
ln -sfn /home/sebastian/schreiben/Schreibprojekte/Skripte/schreibprojekte-dialog /home/sebastian/.local/bin/schreibprojekte-dialog
```

Alternativ aus dem Werkzeug-Repository:

```bash
uv run manuskript dialog
```

## Auswahlfolge

Der Dialog fragt nacheinander Projekt, Umfang und Prüfung ab. Projekte werden aus
`~/.config/schreibprojekte/*.conf` und dem Schreibprojekte-Ordner erkannt. Als Umfang stehen der
gesamte Roman, ein Teil/Akt und eine einzelne Markdown-Datei zur Auswahl.

Bei einem Teil/Akt gelten die Hunderterbereiche der Dateinamen: `100–199` ist Akt 1, `200–299`
Akt 2 und so weiter. Das Teil-/Aktlektorat steht nur bei diesem Umfang, das Gesamtromanlektorat nur
beim gesamten Projekt zur Auswahl. Datei-/Szenenprüfungen können auf eine Datei oder nacheinander
auf alle Dateien des gewählten Bereichs angewendet werden.

## Lernendes Wörterbuch

Die Wörterbuchprüfung ruft LanguageTool direkt für den gewählten aktuellen Umfang auf. Sie
benötigt weder einen Nachtlauf noch eine Überarbeitungsnummer. Gleiche unbekannte Schreibweisen
werden mit sämtlichen Fundstellen gebündelt. Für jeden Begriff stehen zur Auswahl:

- `p`: als korrektes Projektwort bestätigen;
- `g`: als projektübergreifendes persönliches Wort bestätigen;
- `e`: nach Vorschau und zweiter Bestätigung an allen vollständigen Wortfundstellen ersetzen;
  die Ersetzung darf auch eine kurze Wortgruppe wie `zu viele` sein;
- `o`: offen lassen;
- `q`: Dialog beenden.

Die Wörterbücher liegen unter:

```text
~/.config/schreibprojekte/woerterbuch.txt
PROJEKT/woerterbuch/projekt.txt
```

Das normale Korrektorat und der Nachtlauf lesen beide Wörterbücher automatisch. Bestätigte Wörter
werden daher in späteren Läufen nicht erneut als unbekannt gemeldet.

Vor einer Ersetzung prüft das Werkzeug, dass sich die betroffenen Dateien seit der aktuellen
LanguageTool-Prüfung nicht geändert haben. Es ersetzt nur vollständige, exakt gleich geschriebene
Wörter. Sicherungen und Protokolle werden separat abgelegt:

```text
PROJEKT/lektorat/woerterbuch/sicherungen/<zeitpunkt>/
PROJEKT/lektorat/woerterbuch/anwendung-<zeitpunkt>.md
```

Eine Ersetzung ist ein bewusster Manuskripteingriff. Nach der Kontrolle sollte sie im jeweiligen
Projekt als eigener Git-Commit gespeichert werden.

## Abweichende Speicherorte

```bash
schreibprojekte-dialog --projects-root /pfad/zu/schreiben
schreibprojekte-dialog --config-dir /pfad/zu/config
```
