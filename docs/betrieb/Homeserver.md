# Schreibprojekte auf Mac, NAS und Homeserver

## Aufgabenverteilung

| System | Aufgabe |
| --- | --- |
| Mac, iPad, iPhone | Schreiben und manuelles Überarbeiten in Obsidian |
| NAS | Zentrale, dauerhafte Ablage der Vaults unter `/volume1/schreiben` |
| Nextcloud | Geschützter WebDAV-Zugang von außerhalb des Heimnetzes |
| Homeserver | Lektoratsläufe mit Schreibprojekte, Ollama und LanguageTool |
| GitHub | Versionsverwaltung des Werkzeugs und der lokalen Schreibprojekt-Repositories |

Auf Mac, iPad und iPhone existieren lokale Obsidian-Arbeitskopien. Remotely Save gleicht sie mit
dem zentralen NAS-Vault ab. Git wird auf dem Mac im lokalen Projekt-Repository verwendet; die
Git-Verwaltungsdaten `.git` werden nicht in den NAS-Vault kopiert. Der Homeserver bindet den
NAS-Bestand über NFS unter `/mnt/nfs/schreiben` ein. Er schreibt ausschließlich separate Berichte
in den jeweiligen Projektordner `lektorat/`; Dateien unter `03_Content/` werden nicht verändert.

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
/mnt/nfs/schreiben/eheversprechen           Pilotprojekt Eheversprechen auf dem NAS
```

`uv` liegt unter `/home/sebastian/.local/bin/uv`. Ollama ist nur lokal über
`http://127.0.0.1:11434` erreichbar. Für Homestories wird `llama3.1:8b` verwendet. LanguageTool
läuft im Container `languagetool` und ist wegen der bestehenden OnlyOffice-Belegung von Port 8081
nur über `http://127.0.0.1:8082` erreichbar. Diese Dienste werden nicht öffentlich freigegeben.
OpenProject 14.6.3 wird über seine API v3 und Basic-Token-Authentifizierung angesprochen.

Die maschinenspezifische Homestories-Konfiguration liegt außerhalb des Vaults:

```text
/home/sebastian/schreiben/config/Homestories.json
```

Für den Pilotlauf liegt `eheversprechen` als Inhaltskopie ohne `.git` auf dem NAS. Versteckte
`.env`-Dateien gehören weder in den NAS-Vault noch in Obsidian; maschinenspezifische Geheimnisse
liegen ausschließlich mit Modus `600` unter `/home/sebastian/.config/schreibprojekte/`.

## Pilotprojekt Eheversprechen

`eheversprechen` erprobt den vollständigen Ablauf zunächst mit einer kürzeren Erzählung. Die acht
aktuellen Manuskriptdateien heißen `101.md` bis `108.md`. Parallel vorhandene Sicherungsfassungen
`_101.md` bis `_108.md` bleiben unverändert erhalten, werden aber durch das Muster `_*.md` vom
Nachtlauf ausgeschlossen. Der geprüfte Überarbeitungsstand ist `2`.

Der Projekttitel wird nicht aus dem Ordnernamen geraten, sondern aus
`Metadaten/titlepage.yml` gelesen: `Ein unmögliches Eheversprechen`. Vor dem ersten Lauf werden
Dateiauswahl, Metadaten, Snapshot und OpenProject-Vorschau kontrolliert. Ein automatischer Timer
wird für diesen Pilotversuch nicht aktiviert.

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

Den revisionsgebundenen Nachtlauf und die OpenProject-Übergabe bedienen:

```bash
homestories-lektorat start 4 5
homestories-lektorat status
homestories-lektorat log
homestories-lektorat resume 4
homestories-lektorat preview 4
homestories-lektorat sync 4
```

`start 4 5` prüft den abgeschlossenen Stand 4 und bereitet Aufgaben für Überarbeitung 5 vor.
`status` meldet, ob der Prozess läuft. `log` zeigt das aktuelle Log fortlaufend; `Ctrl+C` beendet
nur die Anzeige. Nach einem Prozess-, Container- oder Serverabbruch setzt `resume 4` denselben
Lauf auf seiner eingefrorenen Arbeitskopie fort und überspringt fertige Prüfungen. `preview`
verändert OpenProject nicht; erst `sync` legt Aufgaben an. Details stehen
unter [Lektoratsbefunde in OpenProject](OpenProject.md). Teil-/Akt- und Gesamtromanlektorat bleiben
bewusste Einzelstarts.

Der selbst gehostete Dienst `https://ntfy.sukstorf.de` sendet Statusmeldungen des Nachtlaufs an
das private Topic `schreibprojekte`. Details zu Portainer-Stack, iPhone-App und Token stehen unter
[Push-Benachrichtigungen mit ntfy](Benachrichtigungen.md).

## Automatische Wiederaufnahme mit systemd

Produktive Nachtläufe werden als persistente `systemd`-Benutzerdienste ausgeführt. Dafür muss
einmalig `sudo loginctl enable-linger sebastian` gesetzt sein. Eine Zustandsdatei unter
`~/.config/schreibprojekte/<projekt>-run.env` hält Projekt, Konfiguration, geprüften Stand und
Zielüberarbeitung fest. Sie enthält keine API-Token.

Der Dienst startet nach einem Prozessfehler nach 60 Sekunden denselben Stand mit `resume` neu. Er
versucht höchstens fünf Dienststarts innerhalb von sechs Stunden. Ein Serverneustart startet einen
noch aktiven Stand erneut; ein vollständig abgeschlossener Lauf entfernt seine Zustandsdatei und
läuft beim nächsten Boot nicht nochmals. `systemctl --user stop` ist ein bewusster Stopp und löst
keinen automatischen Neustart aus.

```bash
systemctl --user status schreibprojekte-lektorat@eheversprechen.service
journalctl --user -u schreibprojekte-lektorat@eheversprechen.service -f
systemctl --user stop schreibprojekte-lektorat@eheversprechen.service
```

Die Wiederaufnahme erfolgt an sicheren Berichtsgrenzen: fertige `.md`-Berichte werden
übersprungen, die zuletzt unvollständige `.partial`-Prüfung wird erneut ausgeführt. Nach wiederholt
fehlgeschlagenen Versuchen bleibt der Zustand erhalten und kann nach Fehlerbehebung erneut
gestartet werden.

Die allgemeine Bedienung erfolgt mit `lektorat-dienst PROJEKT BEFEHL`. Ein projektspezifischer
Kurzname darf denselben Aufruf kapseln. Für `eheversprechen-lektorat` sind damit beispielsweise
folgende Befehle vorgesehen:

```bash
eheversprechen-lektorat start 2 3
eheversprechen-lektorat status
eheversprechen-lektorat log
eheversprechen-lektorat stop
eheversprechen-lektorat resume 2
```

`stop` ist eine bewusste Pause und behält die Zustandsdatei. Ein unerwarteter Fehler führt dagegen
automatisch nach 60 Sekunden zu einem neuen Versuch. Die Projektkonfiguration liegt in
`~/.config/schreibprojekte/eheversprechen.conf` und enthält mindestens:

```bash
PROJECT=/mnt/nfs/schreiben/eheversprechen
CONFIG=/home/sebastian/schreiben/config/Eheversprechen.json
```

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
