# Schreibprojekte auf Mac, NAS und Homeserver

## Aufgabenverteilung

| System | Aufgabe |
| --- | --- |
| Mac, iPad, iPhone | Schreiben und manuelles Überarbeiten in Obsidian |
| NAS | Zentrale, dauerhafte Ablage der Vaults unter `/volume1/schreiben` |
| Nextcloud | Geschützter WebDAV-Zugang von außerhalb des Heimnetzes |
| Homeserver | Lektoratsläufe mit Schreibprojekte, Ollama und LanguageTool |
| GitHub | Versionsverwaltung des Werkzeugs und der einzelnen Schreibprojekte |

Die Markdown-Manuskripte liegen nur einmal zentral auf dem NAS. Der Homeserver bindet denselben
Bestand über NFS unter `/mnt/nfs/schreiben` ein. Er schreibt ausschließlich separate Berichte in
den jeweiligen Projektordner `lektorat/`; Dateien unter `03_Content/` werden nicht verändert.

## Speicher- und Synchronisationswege

```text
Mac / iPad / iPhone
        │  Obsidian + Remotely Save
        ▼
Nextcloud-WebDAV
        │  externer Speicher /mnt/schreiben
        ▼
NAS /volume1/schreiben
        ▲
        │  NFS /mnt/nfs/schreiben
        │
Homeserver: Schreibprojekte + Ollama + LanguageTool
```

Nextcloud verwendet den externen Speicher `schreiben`, der im App- und Cron-Container als
`/mnt/schreiben` eingebunden ist. Der WebDAV-Endpunkt für Remotely Save lautet:

```text
https://nextcloud.sukstorf.de/remote.php/dav/files/sebastian/schreiben
```

Jeder lokale Obsidian-Vault verwendet darunter genau seinen eigenen Basisordner, zum Beispiel
`Homestories`, `Sturmausläufer` oder `Testprojekt`. Der Projektname darf nicht zugleich an den
WebDAV-Endpunkt angehängt und als Remotely-Save-Basisordner eingetragen werden; andernfalls entsteht
eine Verschachtelung wie `Homestories/Homestories`.

## Homeserver-Installation

```text
/home/sebastian/schreiben/Schreibprojekte   Werkzeug-Repository
/home/sebastian/schreiben/config            Server-Konfigurationen
/home/sebastian/schreiben/backups           Migrationssicherungen
/mnt/nfs/schreiben/Homestories              Homestories auf dem NAS
```

`uv` liegt unter `/home/sebastian/.local/bin/uv`. Ollama ist nur lokal über
`http://127.0.0.1:11434` erreichbar. Für Homestories wird `llama3.1:8b` verwendet. LanguageTool
läuft im Container `languagetool` und ist wegen der bestehenden OnlyOffice-Belegung von Port 8081
nur über `http://127.0.0.1:8082` erreichbar. Diese Dienste werden nicht öffentlich freigegeben.

Die maschinenspezifische Homestories-Konfiguration liegt außerhalb des Vaults:

```text
/home/sebastian/schreiben/config/Homestories.json
```

## Tägliche Befehle für Homestories

Zuerst am Homeserver anmelden:

```bash
ssh schreibserver
```

Eine einzelne Szene vollständig prüfen:

```bash
cd /home/sebastian/schreiben/Schreibprojekte
/home/sebastian/.local/bin/uv run manuskript lektorat-szene /mnt/nfs/schreiben/Homestories/03_Content/101.md --config /home/sebastian/schreiben/config/Homestories.json
```

Den manuellen Nachtlauf bedienen:

```bash
homestories-lektorat start
homestories-lektorat status
homestories-lektorat log
```

`start` führt alle Datei-/Szenenprüfungen für die konfigurierten Markdown-Dateien unter
`03_Content` im Hintergrund aus. `status` meldet, ob der Prozess läuft. `log` zeigt das aktuelle
Log fortlaufend; `Ctrl+C` beendet nur die Anzeige. Teil-/Akt- und Gesamtromanlektorat bleiben
bewusste Einzelstarts.

## Ergebnisstruktur

Alle neuen Berichte verwenden ausschließlich die kleingeschriebene Struktur:

```text
lektorat/
├── szene/
├── teile/
├── gesamt/
└── logs/
```

Auf einem standardmäßig nicht zwischen Groß- und Kleinschreibung unterscheidenden Mac dürfen
`Lektorat` und `lektorat` nicht nebeneinander verwendet werden. Alte Ordner `Lektorat/` und
`Korrektorat/` müssen vor einer Konsolidierung gesichert und in `lektorat/` überführt werden.

## Sichere Änderungen an der Ordnerstruktur

Vor serverseitigen Umbenennungen oder Verschiebungen innerhalb eines Vaults:

1. Remotely Save auf Mac, iPad und iPhone pausieren.
2. Die betroffenen Ordner außerhalb des Vaults sichern.
3. NAS- und lokale Struktur getrennt prüfen.
4. Die Änderung auf dem NAS ausführen.
5. Bei Bedarf den Nextcloud-Dateicache für den Projektpfad neu einlesen.
6. Zuerst nur auf dem Mac manuell synchronisieren und auf Konfliktordner prüfen.
7. Erst danach iPad, iPhone und automatische Synchronisierung wieder aktivieren.

Ein Ordnername wie `*_Conflict` oder `*_ADMIN_*_Conflict` ist ein Warnsignal. In diesem Fall die
Synchronisierung erneut pausieren und zuerst beide Stände vergleichen. Konfliktordner nicht
ungeprüft löschen.

## Aktualisierung des Werkzeugs

Der Homeserver verwendet derzeit den Branch `server/lektorat`, weil die Lektorats- und
Nachtlauffunktionen noch nicht in `origin/main` enthalten sind. Nach der Veröffentlichung des
aktuellen Stands kann das Repository regulär aktualisiert werden:

```bash
cd /home/sebastian/schreiben/Schreibprojekte
git fetch origin
git switch main
git pull --ff-only
/home/sebastian/.local/bin/uv sync --frozen
```

Vor dem Wechsel muss geprüft werden, dass `main` die Befehle `lektorat-szene` und
`lektorat-nacht` tatsächlich enthält.
