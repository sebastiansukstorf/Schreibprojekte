#!/bin/bash

# Lese markierten Text von stdin
TEXT=$(cat)

if [[ -z "$TEXT" ]]; then
  echo "❌ Kein Text übergeben. Bitte markierten Text an das Skript senden." >&2
  exit 1
fi

# Rufe Python inline auf
python3 - <<EOF
import pyttsx3
import re

def clean_markdown(text):
    text = re.sub(r'#.*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'`{1,3}.*?`{1,3}', '', text)
    text = re.sub(r'>.*', '', text)
    text = re.sub(r'-|\*|\+|\d+\.', '', text)
    return text.strip()

text = """$TEXT"""
clean = clean_markdown(text)

engine = pyttsx3.init()
engine.setProperty('rate', 160)

# Versuche deutsche Stimme auf macOS zu setzen
preferred_voices = [
    "com.apple.speech.synthesis.voice.anna",
    "com.apple.speech.synthesis.voice.yannick"
]
preferred_ids = [v.lower() for v in preferred_voices]

voices = engine.getProperty('voices')
selected = None

for voice in voices:
    if voice.id.lower() in preferred_ids:
        engine.setProperty('voice', voice.id)
        selected = voice.name
        break

if selected:
    print(f"✅ Stimme gesetzt: {selected}")
else:
    print("⚠️  Keine deutsche Stimme gefunden. Verwende Standardsprache.")

engine.say(clean)
engine.runAndWait()
EOF
