import pyttsx3
import re

def remove_markdown(text):
    """Entfernt einfache Markdown-Syntax aus dem Text"""
    text = re.sub(r'#.*', '', text)  # Überschriften entfernen
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Fett
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Kursiv
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)   # Bilder
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)    # Links
    text = re.sub(r'`{1,3}.*?`{1,3}', '', text)   # Code
    text = re.sub(r'>.*', '', text)               # Zitate
    text = re.sub(r'-|\*|\+|\d+\.', '', text)     # Listenpunkte
    return text.strip()

def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_text = file.read()
    clean_text = remove_markdown(raw_text)

    engine = pyttsx3.init()
    engine.setProperty('rate', 160)  # Lesegeschwindigkeit
    engine.say(clean_text)
    engine.runAndWait()

if __name__ == "__main__":
    path = input("Pfad zur Markdown-Datei: ")
    read_markdown_file(path)
