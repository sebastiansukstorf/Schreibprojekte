from openai import OpenAI
import os
import sys

# Client mit API-Key aus Umgebungsvariable erstellen
client = OpenAI()

# Dateiname per CLI oder Eingabe
if len(sys.argv) > 1:
    input_filename = sys.argv[1]
else:
    input_filename = input("🔍 Gib den Namen der Markdown-Datei an (z. B. '101.md'): ").strip()

# Pfade definieren
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(project_root, "03_Content", input_filename)
rules_path = os.path.join(project_root, "04_Analyse", "DE_Elmore Leonard- 10 Rules Of Writing.md")

# Dateien prüfen
if not os.path.exists(input_path):
    print(f"❌ Datei '{input_path}' nicht gefunden.")
    exit(1)
if not os.path.exists(rules_path):
    print(f"❌ Regeln-Datei '{rules_path}' nicht gefunden.")
    exit(1)

# Inhalte einlesen
with open(input_path, "r", encoding="utf-8") as f:
    markdown_text = f.read()
with open(rules_path, "r", encoding="utf-8") as f:
    writing_rules = f.read()

# Prompt vorbereiten
figur_name = "FIGUR"  # Nach Wunsch anpassbar

prompt = (
    f"Du bist in der Rolle eines Lektors und prüfst den folgenden Text anhand der 10 Regeln aus Elmore Leonards 'Rules of Writing'.\n\n"
    f"Diese Regeln sind:\n\n{writing_rules}\n\n"
    f"Aufgabe:\n"
    f"Ergänze narrative Elemente, um den Text nicht zu dialoglastig wirken zu lassen. "
    f"Schreibe den gesamten Text aus der Perspektive von {figur_name}. "
    f"Streiche keinen Originaltext. Ergänze neuen Text *kursiv*.\n\n"
    f"---\n\n"
    f"Text:\n{markdown_text}"
)

# GPT-4-Anfrage
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Du bist ein professioneller Lektor, der nach Elmore Leonards 10 Schreibregeln arbeitet."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=3500
)

# Ausgabe extrahieren
o
