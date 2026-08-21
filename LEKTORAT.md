# Lektorat und Korrektorat

## Ziel

`Schreibprojekte` soll einen mehrstufigen Lektorats- und Korrektoratsprozess für literarische Manuskripte bereitstellen. Grundlage bleiben die Markdown-Dateien des Manuskripts. Die Werkzeuge dürfen sie lesen und analysieren, verändern den Originaltext aber nicht automatisch.

Die Architektur besteht aus drei Ebenen:

1. **Datei-/Szenenlektorat** – Prüfung einer einzelnen neuen oder geänderten Markdown-Datei
2. **Teil-/Aktlektorat** – Prüfung eines vollständigen Romanteils
3. **Gesamtromanlektorat** – Prüfung des abgeschlossenen Romans

## Grundprinzipien

### Markdown bleibt das Original

Die Manuskriptdateien sind die maßgebliche Quelle. Sie bleiben unverändert. Befunde, Diagnosen und Empfehlungen werden separat unter `lektorat/` gespeichert.

### Diagnose vor Umschreibung

Jeder Befund trennt:

1. **Fundstelle**
2. **Diagnose**
3. **Relevanz**
4. **Begründung**
5. **Empfehlung**
6. **Querverweise**, falls vorhanden

Das System schreibt nicht ungefragt Ersatzprosa. Es unterstützt die Entscheidung des Autors, statt den Roman automatisch umzuschreiben.

### Literarischen Stil schützen

Formale Regeln sind nicht mit Stilnormierung gleichzusetzen. Kurze Sätze, Ellipsen, Satzfragmente, hohe Dialogdichte, ungewöhnliche Wortwahl sowie sparsame Beschreibung, Exposition oder Innensicht können beabsichtigt sein. Sie dürfen nicht allein wegen ihrer Form als Fehler gelten.

Für stilistische Bewertungen soll ein projektspezifisches Stilprofil herangezogen werden. Insbesondere müssen Sprecher nicht fortlaufend durch „sagte er“ oder vergleichbare Redebegleitsätze markiert werden. Redebegleitsätze werden nach Klarheit, Rhythmus und Wirkung beurteilt, nicht nach ihrer bloßen Häufigkeit.

### Erst fachlich prüfen, dann automatisieren

Der redaktionelle Prozess und seine Prüfkriterien werden zunächst definiert und getestet. Erst nach fachlicher Validierung werden einzelne Module automatisiert.

# Ebene 1 – Datei-/Szenenlektorat

## Zweck und Auslösung

Diese Ebene untersucht eine einzelne neue oder geänderte Manuskriptdatei als sprachlichen Text und als dramatische Einheit.

> **Leitfrage:** Funktioniert diese einzelne Szene sprachlich, stilistisch und dramaturgisch?

Das Datei-/Szenenlektorat ist der wichtigste Kandidat für einen späteren automatischen Nachtprozess. Ob der Text von Hand geschrieben, direkt in Obsidian erfasst, diktiert oder aus einer Audioaufnahme transkribiert wurde, spielt nach seiner Überführung in Markdown keine Rolle mehr.

Die Prüfung erfolgt in sieben spezialisierten Modulen.

## 1. Korrektorat

Prüfung auf handwerkliche Fehler:

- Orthografie und Tippfehler
- Groß- und Kleinschreibung
- Grammatik und Satzbau
- Kasus und Kongruenz
- unbeabsichtigte Tempusfehler
- Zeichensetzung, insbesondere Kommas, Punkte, Gedankenstriche und Auslassungspunkte
- mögliche Diktat- und Transkriptionsfehler

Die reine Form typografischer Anführungszeichen ist keine Prüfung des Nachtlaufs. Gerade oder
uneinheitliche Anführungszeichen dürfen im Markdown stehen; beim DOCX-Export normalisiert Pandoc
sie zu deutschen Paaren (`„…“` beziehungsweise `‚…‘`). Inhaltlich notwendige Zeichensetzung rund
um die wörtliche Rede, etwa Kommas und Satzschlusszeichen, bleibt Teil des Korrektorats.

Literarische Ellipsen und bewusst unvollständige Sätze sind nicht automatisch Grammatikfehler. Unsichere Befunde werden als Verdacht gekennzeichnet und nicht stillschweigend korrigiert.

Unbekannte Wörter können unabhängig vom Nachtlauf im interaktiven Prüfungsdialog gebündelt
bearbeitet werden. Bestätigte persönliche und projektspezifische Wörter werden getrennt gespeichert
und von späteren Korrektoratsläufen ausgefiltert. Eine projektweite Ersetzung erfolgt nur nach
Vorschau und ausdrücklicher Bestätigung; sie wird gesichert und protokolliert.

## 2. Dialogformalia

Separate formale Prüfung der wörtlichen Rede:

- Zeichensetzung bei vorangestellten, eingeschobenen und nachgestellten Redebegleitsätzen
- Sprecher- und Absatzwechsel
- eindeutige Sprecherzuordnung
- Häufung, Wiederholung oder unnötige Verwendung von „sagte“-Konstruktionen und anderen Sprechverben
- Verhältnis von Redebegleitsatz, Handlung und direkter Rede

Redebegleitsätze werden nur empfohlen, wenn sie Orientierung, Rhythmus, Handlung oder Subtext tatsächlich verbessern.

## 3. Stillektorat

Prüfung sprachlicher Auffälligkeiten unter Berücksichtigung des projektspezifischen Stilprofils:

- unbeabsichtigte Wortwiederholungen
- auffällige Wiederholungen von Satzanfängen
- Füllwörter
- schwache oder unpräzise Verben
- unnötige Adjektive und Adverbien
- Pleonasmen und sprachliche Redundanzen
- unnötige Erklärungen
- uneinheitlicher Ton oder Rhythmus
- unbeabsichtigte Abweichungen von der Figuren- oder Erzählerstimme

Auffälligkeiten werden beschrieben und gewichtet. Eine statistische Häufung ist ein Prüfhinweis, noch kein Fehler.

## 4. Dialoglektorat

Der Dialog wird zusätzlich dramaturgisch geprüft:

- Sind die Figurenstimmen unterscheidbar?
- Sagen Figuren einander Dinge, die beide bereits wissen?
- Wird Information nur für den Leser ausgesprochen?
- Gibt es erklärenden oder unnatürlich vollständigen Dialog?
- Sind Begrüßungen, Verabschiedungen oder Gesprächsschleifen verzichtbar?
- Hat der Dialog Subtext?
- Verfolgen die Beteiligten erkennbare, möglicherweise gegensätzliche Ziele?
- Wer kontrolliert das Gespräch, und verändert sich das Machtverhältnis?
- Erklärt der Erzähler anschließend noch einmal, was der Dialog bereits gezeigt hat?

## 5. Szenenlektorat

Die Datei wird als dramatische Einheit betrachtet:

- **Einstieg:** Beginnt die Szene möglichst spät und mit einem wirksamen Impuls?
- **Ziel:** Will mindestens eine Figur etwas Konkretes?
- **Konflikt:** Was verhindert oder erschwert dieses Ziel?
- **Dynamik:** Entwickelt sich die Situation oder bleibt sie statisch?
- **Wendung:** Gibt es einen Umschlag, eine Enthüllung oder relevante Veränderung?
- **Ausgang:** Ist am Ende etwas anders als am Anfang?
- **Ende:** Verlässt der Text die Szene an einer wirkungsvollen Stelle?
- **Funktion:** Welchen Beitrag leistet die Szene zu Plot, Figur, Beziehung, Thema oder Atmosphäre?

Die wichtigsten Ergebnisse dieses Prüfschritts werden zusätzlich als YAML-Header des erzeugten
Szenenlektoratsberichts gespeichert: Einstieg, Ziel, Konflikt, Dynamik, Wendung, Ausgang, Ende und
Funktion. Die Manuskriptdatei selbst bleibt unverändert.

## 6. Perspektivlektorat

Prüfung der erzählerischen Vermittlung:

- konsistente Erzählperspektive und Distanz
- ungewollte Perspektivwechsel
- Wissen und Wahrnehmungsmöglichkeiten der Perspektivfigur
- stimmige Innensicht
- Verhältnis von Wahrnehmung, Handlung und Erklärung
- unnötige Erzählererklärungen
- präzise Prüfung von „Show, don't tell“: Muss der Leser etwas erleben, oder ist eine knappe Mitteilung an dieser Stelle funktional besser?

## 7. Kontinuitätslektorat

Prüfung anhand des verfügbaren Projektkontexts beziehungsweise einer späteren Story Bible:

- Figurenwissen und zeitgerechter Informationsstand
- Alter, Aussehen, Beruf, Beziehungen und Biografie
- Orte, Wege und räumliche Verhältnisse
- Zeitablauf, Tageszeiten und Chronologie
- Gegenstände, Verletzungen, Kleidung und andere Zustände
- Anschluss an vorherige Szenen
- Widersprüche zu etablierten Ereignissen oder Regeln der erzählten Welt

Kontinuitätsaussagen ohne ausreichenden Projektkontext werden als unsicher gekennzeichnet.

## Ausgabe

```text
lektorat/
└── szene/
    └── 205_lektorat.md
```

Der Bericht ordnet die Befunde nach den sieben Modulen und priorisiert sie nach Relevanz. Korrektorat und Lektorat bleiben unterscheidbar; das Manuskript wird nicht verändert.

# Ebene 2 – Teil-/Aktlektorat

## Zweck und Auslösung

Nach Abschluss oder größerer Überarbeitung eines Romanteils werden alle zugehörigen Szenen gemeinsam betrachtet. Bei einer entsprechenden Manuskriptnummerierung können beispielsweise `100–199`, `200–299` und `300–399` den drei Hauptteilen entsprechen.

> **Leitfrage:** Funktioniert dieser Teil des Romans als zusammenhängende dramatische Einheit?

Das Teil-/Aktlektorat wird bewusst und meilensteinbezogen angestoßen, nicht bei jeder Dateiänderung.

## Prüffelder

### Dramaturgie

- Aufbau und Funktion des Aktes
- Spannungsverlauf und Eskalation
- Tempo und Szenenfolge
- Wendepunkte
- Vorbereitung und Einlösung von Erwartungen

### Figuren

- Entwicklung und Motivation
- Beziehungen und Konflikte
- konsistentes Verhalten
- unterscheidbare Figurenstimmen
- Veränderung innerhalb des Teils

### Plot, Kausalität und Kontinuität

- nachvollziehbare Ursache-Wirkungs-Beziehungen
- Lücken, Widersprüche und unverdiente Wendungen
- zeitliche, räumliche und inhaltliche Konsistenz
- Informationsverteilung und Wissensstände

### Szenenverbund

- Funktion jeder Szene im Teil
- Wiederholungen und Redundanzen zwischen Szenen
- fehlende Zwischenschritte
- unnötige, verschiebbare oder zusammenlegbare Szenen
- Qualität der Übergänge

## Ausgabe

```text
lektorat/
├── szene/
│   ├── 201_lektorat.md
│   ├── 202_lektorat.md
│   └── ...
└── teile/
    └── teil_2_lektorat.md
```

Der Bericht wiederholt nicht bloß die Szenenberichte, sondern diagnostiziert die Wirkung ihres Zusammenspiels.

# Ebene 3 – Gesamtromanlektorat

## Zweck und Auslösung

Nach Fertigstellung des Manuskripts oder nach einer größeren Gesamtüberarbeitung wird der Roman als zusammenhängendes Werk analysiert.

> **Leitfrage:** Funktioniert das Manuskript als Roman – strukturell, erzählerisch, stilistisch und inhaltlich?

Das Gesamtromanlektorat wird bewusst angestoßen. Es kann frühere Berichte berücksichtigen, muss seine Aussagen aber aus der vollständigen Romanfassung ableiten.

## Prüffelder

### Gesamtplot

- Kausalität der Gesamthandlung
- Hauptplot und Nebenhandlungen
- offene, unnötige oder nicht eingelöste Handlungsstränge
- Vorbereitung wichtiger Ereignisse
- Auflösung zentraler Konflikte

### Struktur und Spannung

- Funktion der drei Teile beziehungsweise Akte
- auslösendes Ereignis und zentrale Wendepunkte
- Mittelpunkt, Krise, Höhepunkt und Schluss
- Spannungsbogen und Tempowechsel
- Gewichtsverteilung zwischen den Teilen

### Figurenbögen

- Ausgangslage, Ziele und innere Konflikte
- nachvollziehbare Entwicklung
- Beziehungen und ihre Veränderungen
- Entscheidungen im Höhepunkt
- Zustand der Figuren am Ende

### Setups, Payoffs, Motive und Themen

- eingeführte und eingelöste Erwartungen
- Foreshadowing und Rückbezüge
- wiederkehrende Motive und ihre Entwicklung
- thematische Kohärenz
- unbeabsichtigte Wiederholungen oder Widersprüche

### Anfang, Ende und Gesamtwirkung

- Versprechen und Sog des Romananfangs
- Verhältnis von Anfang und Ende
- emotionale und inhaltliche Wirkung des Schlusses
- Nachvollziehbarkeit der Gesamtentwicklung
- Konsistenz von Perspektive, Ton und Stil

## Ausgabe

```text
lektorat/
├── szene/
├── teile/
│   ├── teil_1_lektorat.md
│   ├── teil_2_lektorat.md
│   └── teil_3_lektorat.md
└── gesamt/
    └── roman_lektorat.md
```

Die Gesamtdiagnose priorisiert Probleme nach Wirkung und Dringlichkeit. Aus ihr können konkrete Aufträge für ein erneutes Teil-/Akt- oder Datei-/Szenenlektorat abgeleitet werden.

# Gesamtarchitektur

```text
Markdown-Manuskript
        │
        ▼
Datei-/Szenenlektorat
Korrektorat → Dialogformalia → Stil → Dialog → Szene → Perspektive → Kontinuität
        │
        ▼
Teil-/Aktlektorat
Dramaturgie → Figuren → Kausalität → Kontinuität → Szenenverbund
        │
        ▼
Gesamtromanlektorat
Gesamtplot → Struktur → Figurenbögen → Setups/Payoffs → Motive → Gesamtwirkung
```

Die Ebenen wiederholen einander nicht, sondern vergrößern den Betrachtungsrahmen: Szene, Teil/Akt und Gesamtroman. Nur die erste Ebene ist für eine spätere regelmäßige Automatisierung vorgesehen. Teil- und Gesamtlektorat bleiben bewusst ausgelöste Meilensteinprüfungen.

## Ausführung

```bash
# einzelne Szene
uv run manuskript lektorat-szene ../MeinProjekt/03_Content/205.md

# zweiter Teil anhand numerischer Dateinamen
uv run manuskript lektorat-teil ../MeinProjekt --start 200 --end 299 --label teil_2

# vollständiger Roman
uv run manuskript lektorat-gesamt ../MeinProjekt
```

Optional bindet `--context PFAD` eine Story Bible oder einen Kontextordner ein. Gleichnamige
Shell-Skripte unter `Skripte/` und Aufgaben in `.vscode/tasks.json` stellen dieselben Aufrufe bereit.

## Manueller Nachtlauf

```bash
Skripte/lektorat-nacht.sh ../MeinProjekt
```

Der manuell gestartete Hintergrundprozess führt für alle Markdown-Dateien unter `03_Content` die
Datei-/Szenenprüfungen aus. Bereits aktuelle Einzelberichte werden übersprungen, Fehler werden
protokolliert und der Lauf wird mit der nächsten Prüfung fortgesetzt. Logs und die letzte
Zusammenfassung liegen unter `lektorat/logs/`. Teil-/Akt- und Gesamtromanlektorat sind nicht Teil
des Nachtlaufs und werden weiterhin bewusst angestoßen.

Der Standardnachtlauf umfasst `korrektorat`, `sagte`, `wortarten` und `szenenlektorat`. H‑L‑X ist
eine optionale Stilprüfung für ausgewählte Szenen oder späte Überarbeitungsstände. Sie wird nicht
mehr automatisch auf jede Manuskriptzeile angewandt, weil der hohe Anteil reiner L-Bestätigungen
Laufzeit erzeugt, ohne daraus Überarbeitungsaufgaben abzuleiten.

## Produktiver Homeserverbetrieb

Im produktiven Aufbau bleiben Schreiben und Überarbeiten auf Mac, iPad und iPhone. Die Vaults
liegen zentral auf dem NAS und werden über Nextcloud-WebDAV mit Obsidian synchronisiert. Der
Homeserver liest denselben Bestand über NFS und erzeugt nur separate Lektoratsberichte.

Für Homestories steht auf dem Homeserver der manuelle Steuerbefehl bereit:

```bash
homestories-lektorat start 4 5
homestories-lektorat status
homestories-lektorat log
homestories-lektorat resume 4
homestories-lektorat preview 4
homestories-lektorat sync 4
```

`start 4 5` prüft den eingefrorenen Stand 4 und kennzeichnet Überarbeitung 5 als Ziel der späteren
OpenProject-Aufgaben. Nach einem Abbruch setzt `resume 4` denselben Lauf fort und überspringt
bereits fertige Prüfungen. `preview` ist immer der letzte nicht schreibende Kontrollschritt vor
`sync`.

Der produktive Nachtlauf kann Start, Wiederaufnahme, abgeschlossene Akte, Abbruch und Abschluss
an das private ntfy-Topic `schreibprojekte` senden. Versandfehler werden nur protokolliert und
unterbrechen keine Prüfung. Einrichtung und Token-Ablage stehen unter
[Push-Benachrichtigungen mit ntfy](docs/betrieb/Benachrichtigungen.md).

Auf dem Homeserver übernimmt ein persistenter `systemd`-Benutzerdienst den produktiven Lauf.
`loginctl enable-linger` hält den Benutzerdienst auch ohne offene SSH-Sitzung aktiv. Bei einem
technischen Fehler oder Serverneustart liest der Dienst den gespeicherten Überarbeitungsstand und
setzt denselben Lauf nach 60 Sekunden fort. Ein bewusstes `stop` bleibt dagegen eine Pause und
löst keinen automatischen Neustart aus.

Die Serverkonfiguration liegt außerhalb des Vaults. Dadurch bleiben Zugangspunkte, Modellwahl und
maschinenspezifische Pfade von den Manuskripten und der Obsidian-Synchronisierung getrennt.

Alle Ebenen verwenden konsequent den kleingeschriebenen Ergebnisordner `lektorat/`. Vor einer
serverseitigen Änderung der Vault-Struktur muss Remotely Save auf allen Geräten pausiert werden.
Das ist besonders auf dem Mac wichtig, weil dort `Lektorat` und `lektorat` nicht zuverlässig als
getrennte Ordner behandelt werden. Die vollständige Betriebs- und Wiederanlaufanleitung steht in
[Schreibprojekte auf Mac, NAS und Homeserver](docs/betrieb/Homeserver.md).

## Überarbeitungsstände und OpenProject

Ein produktiver Nachtlauf gehört immer zu einem ausdrücklich benannten, abgeschlossenen
Überarbeitungsstand. Vor und nach der Prüfung werden SHA-256-Prüfsummen der berücksichtigten
Markdown-Dateien verglichen. Dadurch kann ein während des mehrstündigen Laufs veränderter Textstand
nicht versehentlich als konsistente Diagnose nach OpenProject übertragen werden.

Für die eigentliche Prüfung wird beim Start eine temporäre Momentaufnahme unter
`lektorat/.arbeitskopien/` erzeugt. Alle Module lesen diese Arbeitskopie und damit denselben
eingefrorenen Textstand. Berichte werden zunächst als `.md.partial` geschrieben und erst nach
vollständigem Abschluss atomar veröffentlicht. Die Arbeitskopie wird nur nach einem vollständig
erfolgreichen Abschluss entfernt und steht andernfalls für `resume` bereit.

Eine `.partial`-Datei ist kein freigegebener Bericht. Fertige `.md`-Berichte werden bei einer
Wiederaufnahme übersprungen. Die unvollständige Prüfung wird erneut ausgeführt. Die
„sagte“-Prüfung bindet fortsetzbare Pakete an Modell, Kontextzeilen und Paketgröße; passt diese
Signatur nach einer Konfigurationsänderung nicht mehr, beginnt nur dieser Teilbericht neu.
H–L–X-Pakete mit ausgelassenen Zielzeilen werden zeilenweise nachgeprüft. Doppelt ausgegebene
Pflichtmodule eines Szenenlektorats werden vor der formalen Validierung zusammengeführt, ohne
vorhandene Befunde zu verwerfen.

Die Berichte eines solchen Laufs liegen unter
`lektorat/ueberarbeitungen/<stand>/<laufkennung>/`. Zusätzlich enthält `findings.jsonl` nur
bearbeitbare, normalisierte Befunde. Nicht beanstandete H–L–X-Zeilen, `BEHALTEN`-Urteile und andere
reine Bestätigungen werden nicht zu Aufgaben.

OpenProject wird erst nach einer lokalen Vorschau verändert. `Homestories` bleibt dort ein
dauerhaftes Projekt; jede folgende Überarbeitungsrunde wird als Version geführt. Pro Szene entsteht
eine Sammelaufgabe. Konkrete Grammatik-, Zeichensetzungs- und Rechtschreibbefunde bleiben
zeilenspezifische Unteraufgaben. Unspezifische Tippfehlerhinweise sowie echte
„sagte“-Redebegleitsätze werden jeweils pro Szene in einer Aufgabe mit zeilenspezifischer
Checkliste gebündelt. Rein erzählerische Verwendungen wie `sagte nichts` erzeugen keine Aufgabe.
Eine deaktivierte Szenenobergrenze verhindert, dass Befunde willkürlich abgeschnitten werden.
Feste Befundkennungen verhindern Dubletten bei wiederholter Synchronisierung. Einzelheiten stehen in
[Lektoratsbefunde in OpenProject](docs/betrieb/OpenProject.md).

### Projektübergreifende OpenProject-Hierarchie

Die nächste Ausbaustufe wird mit der kürzeren Erzählung `eheversprechen` und Überarbeitungsstand 2
erprobt. Der OpenProject-Projekttitel stammt aus `Metadaten/titlepage.yml`; darunter folgen die
Version des Überarbeitungsstands sowie hierarchische Arbeitspakete für Kapitel, Datei, Prüfschritt
und einzelne Befunde. Kontextmerkmale werden als `Lektorats-Tags` gespeichert, sofern das
OpenProject-Schema dieses benutzerdefinierte Feld bereitstellt, andernfalls in der Beschreibung.

Für den Pilotlauf zählen nur `03_Content/101.md` bis `108.md` als aktuelle Manuskripte. Die
vorhandenen Sicherungsfassungen `_*.md` bleiben unverändert, sind jedoch vom Lauf auszuschließen.
Vor einem schreibenden OpenProject-Sync stehen immer lokaler Abschluss, unveränderte Prüfsummen und
eine kontrollierte Vorschau. Wiederholte Synchronisierung muss alle Ebenen idempotent aktualisieren.
