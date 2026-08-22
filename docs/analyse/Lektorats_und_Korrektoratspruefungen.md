# Lektorats- und Korrektoratsprüfungen

## Zweck und Abgrenzung

Die Prüfwerkzeuge erzeugen Markdown-Protokolle zu einer ausgewählten Manuskriptdatei. Sie verändern
den Ausgangstext nicht. Vorschläge sind redaktionelle Hinweise und werden nie automatisch in das
Manuskript übernommen.

Dabei werden zwei Arbeitsbereiche getrennt:

- **Korrektorat** prüft regelgebundene Fragen wie Rechtschreibung und Zeichensetzung.
- **Lektorat** beurteilt stilistische Entscheidungen im Kontext der Szene und der persönlichen
  Schreibvereinbarungen.

Die stilistische Grundlage bilden [Action Writing](../methoden/Action_Writing.md), die
[Zehn Regeln für wildes Denken und klare Form](../methoden/Zehn_Regeln_fuer_wildes_Denken_und_klare_Form.md)
und [Elmore Leonards Schreibregeln](DE_Elmore%20Leonard-%2010%20Rules%20Of%20Writing.md).

## Gemeinsame Sicherheitsregeln

Für alle Prüfungen gilt:

1. Eingabe ist eine einzelne Markdown-Datei.
2. Das Manuskript wird ausschließlich gelesen.
3. Das Ergebnis wird außerhalb von `03_Content` gespeichert.
4. Jeder Hinweis enthält eine Zeilennummer und die unveränderte Originalstelle.
5. Modellantworten werden, soweit möglich, lokal auf Format, Zeilennummern und erfundene
   Fundstellen geprüft.
6. Figurenrede, Eigennamen und bewusste Regelabweichungen benötigen immer eine menschliche
   Entscheidung.

## Übersicht

| Prüfung | CLI-Befehl | Technik | Standardausgabe |
| --- | --- | --- | --- |
| Sprecherzuordnung mit „sagte“ | `manuskript lektorat DATEI` | Ollama | `lektorat/szene/<name>-sagte-lektorat.md` |
| H–L–X-Erklärprüfung | `manuskript lektorat-hlx DATEI` | Ollama | `lektorat/szene/<name>-hlx-lektorat.md` |
| Adjektive und Adverbien | `manuskript lektorat-wortarten DATEI` | Ollama; POS-Vorfilterung geplant | `lektorat/szene/<name>-adjektive-adverbien-lektorat.md` |
| Rechtschreibung, Grammatik und Zeichensetzung | `manuskript korrektorat DATEI` | LanguageTool | `lektorat/szene/<name>-korrektorat.md` |
| vollständige Szenendiagnose | `manuskript lektorat-szene DATEI` | Ollama | `lektorat/szene/<name>_lektorat.md` |
| Teil-/Aktdiagnose | `manuskript lektorat-teil PROJEKT` | Ollama | `lektorat/teile/<teil>_lektorat.md` |
| Gesamtromandiagnose | `manuskript lektorat-gesamt PROJEKT` | Ollama | `lektorat/gesamt/roman_lektorat.md` |

## „sagte“-Lektorat

### Ziel

Die Prüfung sucht Sprecherzuordnungen mit „sagte“ oder „sagten“. Sie empfiehlt `STREICHEN`, wenn
der Sprecher bereits durch Redewechsel, Anrede, Handlung oder Kontext eindeutig ist. `BEHALTEN`
wird nur bei einer konkreten Verwechslungsgefahr empfohlen. Synonyme wie „fauchte“ oder „zischte“
werden nicht vorgeschlagen.

### Aufruf

```bash
uv run manuskript lektorat ../MeinProjekt/03_Content/101.md
```

### Arbeitsweise

Die Fundstellen werden lokal per regulärem Ausdruck vorgefiltert und mit wenigen Kontextzeilen in
Pakete gegliedert. Nur diese Ausschnitte werden an Ollama gesendet. Ein Bericht kann paketweise
fortgesetzt werden. Die lokal gelesene Originalzeile wird nach der Modellantwort ergänzt.

### Grenzen

- Sprecherklarheit bleibt eine Kontextentscheidung.
- Ungewöhnliche Dialoggestaltung kann zu Fehlurteilen führen.
- Die Prüfung untersucht keine anderen Redeverben und keine allgemeine Dialogqualität.

## H–L–X-Lektorat

### Ziel

Die Prüfung setzt das H–L–X-System aus Action Writing um:

- **H – Higgins:** Eine abstrakt berichtete Information könnte durch Dialog, Handlung oder Reaktion
  vermittelt werden.
- **L – Leonard:** Der Satz ist notwendig, knapp und konkret.
- **X – Erklärung:** Der Erzähler wiederholt eine Information, die Dialog oder Handlung bereits
  vermittelt haben.

### Aufruf

```bash
uv run manuskript lektorat-hlx ../MeinProjekt/03_Content/101.md
```

### Grenzen

Die Kategorien verlangen semantischen Kontext und werden deshalb von einem Sprachmodell beurteilt.
Konkrete Handlungen, Dialog und notwendige räumliche Orientierung sollen nicht allein aus Gründen
der Kürze gestrichen werden. Der Bericht ist eine Diagnose, keine Änderungsanweisung.

## Adjektiv- und Adverb-Lektorat

### Ziel

Die Prüfung sucht stilistisch auffällige Adjektive und Adverbien. Der Maßstab lautet nicht
„vollständig vermeiden“, sondern „sparsam und präzise verwenden“:

- bloße Verstärker und erklärende Wertungen möglichst streichen,
- schwache Kombinationen durch ein präziseres Substantiv oder Verb ersetzen,
- konkrete, unterscheidende Details erhalten,
- Wörter innerhalb wörtlicher Rede vor automatischer Glättung schützen,
- Adverbien an Redeverben besonders kritisch prüfen.

Die möglichen Urteile sind `STREICHEN`, `ERSETZEN` und `BEHALTEN`.

### Aufruf

```bash
uv run manuskript lektorat-wortarten ../MeinProjekt/03_Content/101.md
```

### Aktueller Stand und bekannte Grenze

Derzeit erkennt und bewertet Ollama die Wortarten im Kontext. Die lokale Validierung verwirft
Phrasen, erfundene Wörter, unzulässige Zeilennummern, wahrscheinliche Substantive und Treffer, die
ausschließlich in wörtlicher Rede stehen. Dennoch ist die Wortartenerkennung eines generativen
Modells weniger zuverlässig und langsamer als ein linguistischer Tagger.

Die vorgesehene Weiterentwicklung ist daher zweistufig:

1. LanguageTool bestimmt lokal deterministisch die `ADJ`- und `ADV`-Kandidaten.
2. Ollama bewertet nur noch diese Kandidaten mit kurzem Kontext stilistisch.

Dadurch sollen Laufzeit, erfundene Fundstellen und unnötige Wiederholungen deutlich sinken.

## Korrektorat für Rechtschreibung, Grammatik und Zeichensetzung

### Normative und technische Grundlage

Normative Grundlage ist das
[Amtliche Regelwerk der deutschen Rechtschreibung 2024](https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf).
Die technische Prüfung übernimmt das offene
[LanguageTool](https://github.com/languagetool-org/languagetool) über dessen HTTP-API.

Die Python-Anbindung verwendet ausschließlich Module der Standardbibliothek: `urllib`, `json`,
`re`, `dataclasses` und `pathlib`.

### Aufruf

```bash
uv run manuskript korrektorat ../MeinProjekt/03_Content/101.md
```

### Arbeitsweise

Markdown-Steuerzeichen und Codebereiche werden maskiert, ohne Zeichenpositionen oder Zeilen zu
verschieben. Aus der LanguageTool-Antwort werden Rechtschreib-, Grammatik- und
Zeichensetzungsregeln übernommen. Allgemeine Stilmeldungen bleiben außerhalb dieses eng geführten
Korrektorats.

Das Protokoll enthält:

- Zeile und Spalte,
- Kategorie,
- Meldung,
- unveränderte Manuskriptzeile,
- bis zu fünf Ersatzvorschläge,
- LanguageTool-Regel-ID.

### Grenzen

- Eigennamen, Ortsnamen und erfundene Bezeichnungen erzeugen häufig Wörterbuchhinweise.
- Gerade Anführungszeichen können zu Hinweisen auf ungepaarte Zeichen führen.
- LanguageTool-Vorschläge sind keine verbindlichen Korrekturen.
- Ein lokaler LanguageTool-Server muss erreichbar sein; standardmäßig wird Port `8081` verwendet.

## Konfiguration

Beispiel für eine vollständig lokale Konfiguration:

```json
{
  "lektorat": {
    "provider": "ollama",
    "base_url": "http://127.0.0.1:11434",
    "model": "qwen3:8b",
    "context_lines": 3,
    "batch_size": 4
  },
  "hlx_lektorat": {
    "context_lines": 2,
    "batch_size": 8
  },
  "wortarten_lektorat": {
    "model": "qwen3:8b",
    "batch_size": 16
  },
  "korrektorat": {
    "base_url": "http://127.0.0.1:8081",
    "language": "de-DE"
  }
}
```

`hlx_lektorat` und `wortarten_lektorat` übernehmen Ollama-Adresse und Modell aus `lektorat`, wenn
sie dort nicht gesondert angegeben sind.

## Drei redaktionelle Ebenen

Die vollständige Szenenprüfung führt die sieben fachlichen Module Korrektorat, Dialogformalia,
Stil, Dialog, Szenenfunktion, Perspektive und Kontinuität in einem einheitlichen Bericht zusammen.
Teil-/Akt- und Gesamtromanlektorat zoomen bewusst auf die Makroebene heraus. Jeder Modellbericht
muss eine Kurzdiagnose sowie die für seine Ebene festgelegten Modulüberschriften enthalten; die
Antwort wird vor dem Schreiben entsprechend validiert.

Alle Befunde folgen dem Schema Fundstelle, Diagnose, Relevanz, Begründung, Empfehlung und
Querverweise. Über `--context` kann eine Story Bible eingebunden werden. Ohne ausreichenden Kontext
müssen Kontinuitätsaussagen als unsicher gekennzeichnet werden.

Der Szenenbericht erhält zusätzlich YAML-Frontmatter mit Einstieg, Ziel, Konflikt, Dynamik,
Wendung, Ausgang, Ende und Funktion der Szene. Diese Metadaten werden aus dem fünften Prüfmodul
abgeleitet und nur in den Bericht geschrieben; die Manuskriptdatei bleibt unverändert.

## Geplante Mac-/Homeserver-Architektur

Die empfohlene Aufgabenverteilung lautet:

1. Der Mac liest das Manuskript und steuert die Prüfung.
2. LanguageTool erkennt lokal Wortarten beziehungsweise prüft Rechtschreibung und Zeichensetzung.
3. Nur vorgefilterte Fundstellen mit kurzem Kontext gehen über das Heimnetz an Ollama.
4. Ollama auf dem Homeserver trifft die semantische Stilentscheidung.
5. Der Mac validiert die Antwort und schreibt den Bericht in das Schreibprojekt.

Vorteile:

- Manuskriptdateien und Berichte bleiben auf dem Mac.
- Das Netzwerk überträgt nur kleine Textpakete.
- Die rechenintensive Modellinferenz läuft auf dem Homeserver.
- Die regelbasierte Wortartenerkennung entlastet das Modell.
- Fehlgeschlagene Pakete sollen später einzeln fortgesetzt werden können.

Beispiel für Ollama auf dem Homeserver:

```json
{
  "wortarten_lektorat": {
    "base_url": "http://HOMESERVER-IP:11434",
    "model": "qwen3:8b",
    "batch_size": 20
  }
}
```

Ollamas Port `11434` darf nicht ungeschützt aus dem Internet erreichbar sein. Im Heimnetz sollte
der Zugriff durch Firewallregeln auf den Mac begrenzt werden; für Zugriffe von außen ist ein VPN
vorzuziehen.

## Empfohlene Reihenfolge pro Text

1. Rechtschreibung und Zeichensetzung (`korrektorat`)
2. Sprecherzuordnung (`lektorat`)
3. Erklärende Doppelungen (`lektorat-hlx`)
4. Adjektive und Adverbien (`lektorat-wortarten`)
5. Menschliche Gesamtlektüre von Rhythmus, Figurenstimme und Szenenwirkung

Die Reihenfolge verhindert, dass stilistische Modellurteile mit einfachen orthografischen Fehlern
vermischt werden. Kein Einzelbericht ersetzt die abschließende Lektüre des vollständigen Textes.
