"""Interaktive, vom Nachtlauf unabhängige Pflege unbekannter Wörter."""

from __future__ import annotations

import hashlib
import re
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from manuskript.korrektorat import finding_kind, language_tool_check, mask_markdown, offset_to_line_column


WORD = re.compile(r"^[^\W\d_]+(?:[-’'][^\W\d_]+)*$", re.UNICODE)


@dataclass(frozen=True)
class Occurrence:
    file: Path
    line: int
    column: int
    word: str
    context: str
    replacements: tuple[str, ...]


def project_dictionary(project: Path) -> Path:
    return project.resolve() / "woerterbuch" / "projekt.txt"


def personal_dictionary() -> Path:
    return Path.home() / ".config" / "schreibprojekte" / "woerterbuch.txt"


def load_words(*paths: Path) -> set[str]:
    words: set[str] = set()
    for path in paths:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if value and not value.startswith("#"):
                words.add(value.casefold())
    return words


def add_word(path: Path, word: str) -> None:
    existing = load_words(path)
    if word.casefold() in existing:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    values = [] if not path.is_file() else [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    values.append(word)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text("\n".join(sorted(set(values), key=str.casefold)) + "\n", encoding="utf-8")
    temporary.replace(path)


def collect_unknown_words(
    files: tuple[Path, ...], *, base_url: str, language: str,
    dictionary_paths: tuple[Path, ...], progress: Callable[[str], None] = print,
) -> tuple[dict[str, list[Occurrence]], dict[Path, str]]:
    known = load_words(*dictionary_paths)
    grouped: dict[str, list[Occurrence]] = defaultdict(list)
    digests: dict[Path, str] = {}
    for index, source in enumerate(files, 1):
        progress(f"[{index}/{len(files)}] Wörter prüfen: {source.name}")
        content = source.read_text(encoding="utf-8")
        digests[source] = hashlib.sha256(content.encode("utf-8")).hexdigest()
        checked = mask_markdown(content)
        response = language_tool_check(checked, base_url=base_url, language=language)
        lines = content.splitlines()
        for match in response.get("matches", []):
            if finding_kind(match) != "Rechtschreibung":
                continue
            offset = int(match.get("offset", 0))
            length = max(1, int(match.get("length", 1)))
            if content[offset : offset + length] != checked[offset : offset + length]:
                continue
            word = content[offset : offset + length].strip()
            if not WORD.fullmatch(word) or word.casefold() in known:
                continue
            line, column = offset_to_line_column(content, offset)
            replacements = tuple(
                str(item["value"]) for item in match.get("replacements", [])[:5]
                if isinstance(item, dict) and item.get("value")
            )
            grouped[word].append(Occurrence(
                source, line, column, word,
                lines[line - 1].strip() if 0 < line <= len(lines) else "",
                replacements,
            ))
    return dict(sorted(grouped.items(), key=lambda item: item[0].casefold())), digests


def replace_word(
    project: Path, occurrences: list[Occurrence], old: str, new: str,
    digests: dict[Path, str], *, now: datetime | None = None,
) -> tuple[int, Path]:
    affected = sorted({item.file for item in occurrences})
    for source in affected:
        current = hashlib.sha256(source.read_bytes()).hexdigest()
        if current != digests[source]:
            raise RuntimeError(f"Datei wurde seit der Prüfung verändert: {source}")
    stamp = (now or datetime.now().astimezone()).strftime("%Y%m%d-%H%M%S")
    backup_root = project / "lektorat" / "woerterbuch" / "sicherungen" / stamp
    pattern = re.compile(rf"(?<!\w){re.escape(old)}(?!\w)")
    changed = 0
    log_lines = ["# Wörterbuch-Ersetzungen", "", f"Zeitpunkt: {stamp}", ""]
    for source in affected:
        content = source.read_text(encoding="utf-8")
        updated, count = pattern.subn(new, content)
        if not count:
            continue
        relative = source.relative_to(project)
        backup = backup_root / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup)
        temporary = source.with_suffix(source.suffix + ".tmp")
        temporary.write_text(updated, encoding="utf-8")
        temporary.replace(source)
        digests[source] = hashlib.sha256(updated.encode("utf-8")).hexdigest()
        changed += count
        log_lines.append(f"- `{relative}`: {count} × `{old}` → `{new}`")
    log = project / "lektorat" / "woerterbuch" / f"anwendung-{stamp}.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return changed, log


def review_unknown_words(
    project: Path, files: tuple[Path, ...], config: dict,
    *, input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print,
) -> None:
    settings = config.get("korrektorat", {})
    project_path = project_dictionary(project)
    personal_path = personal_dictionary()
    grouped, digests = collect_unknown_words(
        files,
        base_url=settings.get("base_url", "http://127.0.0.1:8081"),
        language=settings.get("language", "de-DE"),
        dictionary_paths=(personal_path, project_path),
        progress=output_fn,
    )
    if not grouped:
        output_fn("Keine unbekannten Wörter gefunden.")
        return
    keys = list(grouped)
    for index, key in enumerate(keys, 1):
        items = grouped[key]
        shown = items[0].word
        output_fn(f"\nUnbekannter Begriff {index}/{len(keys)}: {shown} ({len(items)} Vorkommen)")
        for item in items[:8]:
            output_fn(f"  {item.file.relative_to(project)}:{item.line}  {item.context}")
        if len(items) > 8:
            output_fn(f"  … {len(items) - 8} weitere Fundstellen")
        suggestions = tuple(dict.fromkeys(value for item in items for value in item.replacements))[:8]
        if suggestions:
            output_fn("  Vorschläge: " + ", ".join(f"{number}={value}" for number, value in enumerate(suggestions, 1)))
        choice = input_fn("[p] Projektwort, [g] persönliches Wort, [e] überall ersetzen, [o] offen, [q] beenden: ").strip().casefold()
        if choice == "q":
            return
        if choice in {"p", "g"}:
            add_word(project_path if choice == "p" else personal_path, shown)
            output_fn(f"✓ Aufgenommen: {shown}")
            continue
        if choice != "e":
            continue
        replacement = input_fn("Korrekte Schreibweise oder Nummer des Vorschlags: ").strip()
        if replacement.isdigit() and 1 <= int(replacement) <= len(suggestions):
            replacement = suggestions[int(replacement) - 1]
        if not replacement or not WORD.fullmatch(replacement):
            output_fn("Ungültige Ersetzung; Begriff bleibt offen.")
            continue
        confirm = input_fn(f"{len(items)} Fundstellen `{shown}` → `{replacement}` wirklich ändern? [j/N]: ").strip().casefold()
        if confirm != "j":
            continue
        count, log = replace_word(project, items, shown, replacement, digests)
        add_word(project_path, replacement)
        output_fn(f"✓ {count} Vorkommen geändert. Protokoll: {log}")
