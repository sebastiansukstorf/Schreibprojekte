# Changelog

All notable changes to this project are documented in this file.

## Unveröffentlicht

- Ein vom Nachtlauf unabhängiger Prüfungsdialog wählt Projekt, Gesamtroman/Teil/Datei und Prüfung.
  Seine lernenden persönlichen und projektspezifischen Wörterbücher filtern bestätigte Begriffe
  auch in späteren Korrektoratsläufen; bestätigte Ersetzungen werden gesichert und protokolliert.
- Weniger Ollama-Aufrufe im Nachtlauf: Die „sagte“-Prüfung bündelt standardmäßig acht Fundstellen
  bei drei Kontextzeilen, die Wortartenprüfung sechzehn Fundstellen pro Paket.
- Der Nachtlauf ignoriert rein typografische Anführungszeichen-Hinweise; der DOCX-Export setzt
  deutsche Anführungszeichen, ohne die Markdown-Manuskripte zu verändern.
- OpenProject bündelt „sagte“-Kandidaten und generische Tippfehler szenenweise, verwirft
  erzählerische „sagte“-Verwendungen und schneidet bei deaktivierter Obergrenze keine Befunde ab.
- Der Standardnachtlauf ist über `nachtlauf.checks` konfigurierbar; H‑L‑X bleibt als bewusst
  aktivierte Zusatzprüfung verfügbar und ist standardmäßig ausgeschlossen.
- Nachtläufe können als persistente systemd-Benutzerdienste nach Prozess- und Serverabbrüchen
  automatisch am gespeicherten Überarbeitungsstand fortgesetzt werden.
- H–L–X-Prüfungen fordern ausgelassene Zielzeilen einzeln nach.
- „sagte“-Teilergebnisse werden bei geänderter Modell- oder Paketkonfiguration sauber neu erzeugt.
- Doppelte Pflichtüberschriften in Modellantworten des Szenenlektorats werden verlustfrei
  zusammengeführt und erneut validiert.

## release-20260810-91a13b8 - 2026-08-10

- chore: ensure Widmung style and update berschrift1 spacing scripts (commit 91a13b8)
