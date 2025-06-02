# Logitec MX Vertical Tastenbelegung

Um **VS Code Keybindings mit den Hardware-Tasten deiner Logitech MX Vertical Maus** zu nutzen, kannst du die Tasten der Maus so konfigurieren, dass sie bestimmte Tastenkombinationen (Shortcuts) ausführen, die in VS Code verwendet werden. Hier ist eine Schritt-für-Schritt-Anleitung:

---

### 🔧 Schritt 1: Logitech Options oder Logi Options+ installieren

Je nach deiner Maus und Logitech-Softwaregeneration brauchst du:

* [**Logitech Options**](https://support.logi.com/hc/articles/360025297913) (älter)
* [**Logi Options+**](https://www.logitech.com/de-de/software/logi-options-plus.html) (neuer, MX Vertical wird unterstützt)

---

### 🎛️ Schritt 2: Maus-Tasten konfigurieren

1. Öffne **Logitech Options(+)**
2. Wähle die **MX Vertical** Maus aus
3. Klicke auf die Taste, die du neu belegen möchtest (z. B. Vor- oder Zurück-Taste)
4. Wähle „**Tastenkombination zuweisen**“ (oder „Benutzerdefinierte Tastenkombination“)
5. Gib die Tastenkombination ein, die du in **VS Code verwenden möchtest**

   * Beispiel: Für „Format Document“ → `Shift + Alt + F`
   * Beispiel: Für „Terminal öffnen“ → `` Ctrl + ` ``

Optional kannst du auch **programmspezifische Belegungen** einrichten:

* In Logitech Options+: Wähle **„Anwendungsspezifische Einstellungen hinzufügen“**
* Wähle **Visual Studio Code**
* Weise **nur für VS Code** die gewünschte Funktion zu

---

### ⌨️ Schritt 3: VS Code Shortcuts prüfen oder anpassen

1. Öffne VS Code
2. Gehe zu `Datei` → `Einstellungen` → `Tastenkombinationen` (`Ctrl + K Ctrl + S`)
3. Finde den Befehl, den du steuern möchtest
4. Prüfe, welche Tastenkombination diesem zugewiesen ist
5. Optional: Ändere sie, damit sie besser zur Mausbelegung passt

---

### ✅ Beispiel

**Ziel:** Die „Zurück“-Taste soll das Terminal in VS Code öffnen.

* In Logitech Options+: „Zurück“-Taste → Tastenkombination: `` Ctrl + ` ``
* In VS Code: Befehl „Terminal: Neues Terminal“ hat genau diese Tastenkombination → funktioniert sofort

---

### 🧠 Tipp: Tastensimulation testen

* Öffne einen Texteditor und klicke auf die konfigurierte Taste
* Prüfe, ob die richtige Tastenkombination eingegeben wird
* Falls nicht, Software/OS prüfen (manchmal blockieren Sicherheitstools die Emulation)

---

Wenn du magst, kannst du mir sagen, welche Funktionen du genau in VS Code auf die Maus legen willst – dann gebe ich dir konkrete Shortcut-Zuordnungen.
