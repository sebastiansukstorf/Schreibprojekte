"""Interaktiver Einstieg für projekt- und umfangsbezogene Manuskriptprüfungen."""

from __future__ import annotations

import json
import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from manuskript.hlx_lektorat import run_hlx_lektorat
from manuskript.korrektorat import run_korrektorat
from manuskript.nachtlauf import manuscript_files
from manuskript.redaktion import numeric_stem, run_redaktion
from manuskript.sagte_lektorat import run_sagte_lektorat
from manuskript.woerterbuch import review_unknown_words
from manuskript.wortarten_lektorat import run_wortarten_lektorat


@dataclass(frozen=True)
class ProjectChoice:
    name: str
    root: Path
    config: Path | None


def _conf_value(path: Path, name: str) -> str | None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith(f"{name}="):
            values = shlex.split(raw.split("=", 1)[1])
            return values[0] if values else ""
    return None


def discover_projects(projects_root: Path, config_dir: Path) -> tuple[ProjectChoice, ...]:
    records: dict[Path, ProjectChoice] = {}
    if config_dir.is_dir():
        for conf in sorted(config_dir.glob("*.conf")):
            raw_project = _conf_value(conf, "PROJECT")
            if not raw_project:
                continue
            root = Path(raw_project).expanduser().resolve()
            if not (root / "03_Content").is_dir():
                continue
            raw_config = _conf_value(conf, "CONFIG")
            config = Path(raw_config).expanduser().resolve() if raw_config else None
            records[root] = ProjectChoice(root.name, root, config)
    if projects_root.is_dir():
        candidates = [projects_root] if (projects_root / "03_Content").is_dir() else projects_root.iterdir()
        for candidate in candidates:
            if not candidate.is_dir() or not (candidate / "03_Content").is_dir():
                continue
            root = candidate.resolve()
            local_config = root / ".manuskript.json"
            records.setdefault(root, ProjectChoice(root.name, root, local_config if local_config.is_file() else None))
    return tuple(sorted(records.values(), key=lambda item: item.name.casefold()))


def choose(items: tuple, prompt: str, label: Callable[[object], str], input_fn=input, output_fn=print):
    if not items:
        raise ValueError("Keine Auswahlmöglichkeiten gefunden.")
    for number, item in enumerate(items, 1):
        output_fn(f"  {number}. {label(item)}")
    while True:
        raw = input_fn(f"{prompt} [1–{len(items)}; q=Ende]: ").strip().casefold()
        if raw == "q":
            raise KeyboardInterrupt
        if raw.isdigit() and 1 <= int(raw) <= len(items):
            return items[int(raw) - 1]
        output_fn("Bitte eine angezeigte Nummer wählen.")


def acts(files: tuple[Path, ...]) -> tuple[int, ...]:
    return tuple(sorted({number // 100 for path in files if (number := numeric_stem(path)) is not None}))


def load_project_config(project: ProjectChoice) -> dict:
    if project.config and project.config.is_file():
        try:
            return json.loads(project.config.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Ungültige Konfiguration: {project.config}: {error}") from error
    return {}


def _setting(config: dict, section: str, name: str, default):
    return config.get(section, {}).get(name, config.get("lektorat", {}).get(name, default))


def run_file_check(check: str, source: Path, config: dict) -> Path:
    if check == "korrektorat":
        return run_korrektorat(
            source, base_url=_setting(config, "korrektorat", "base_url", "http://127.0.0.1:8081"),
            language=_setting(config, "korrektorat", "language", "de-DE"),
        )
    if check == "sagte":
        return run_sagte_lektorat(
            source, base_url=_setting(config, "lektorat", "base_url", "http://127.0.0.1:11434"),
            model=_setting(config, "lektorat", "model", "qwen3:8b"),
            context_lines=int(_setting(config, "lektorat", "context_lines", 3)),
            batch_size=int(_setting(config, "lektorat", "batch_size", 8)),
        )
    if check == "hlx":
        return run_hlx_lektorat(
            source, base_url=_setting(config, "hlx_lektorat", "base_url", "http://127.0.0.1:11434"),
            model=_setting(config, "hlx_lektorat", "model", "qwen3:8b"),
            fallback_model=_setting(config, "hlx_lektorat", "fallback_model", "qwen3:8b"),
            context_lines=int(_setting(config, "hlx_lektorat", "context_lines", 2)),
            batch_size=int(_setting(config, "hlx_lektorat", "batch_size", 8)),
        )
    if check == "wortarten":
        return run_wortarten_lektorat(
            source, base_url=_setting(config, "wortarten_lektorat", "base_url", "http://127.0.0.1:11434"),
            model=_setting(config, "wortarten_lektorat", "model", "qwen3:8b"),
            batch_size=int(_setting(config, "wortarten_lektorat", "batch_size", 16)),
        )
    if check == "szenenlektorat":
        return run_redaktion(
            source, level="szene",
            base_url=_setting(config, "szene_lektorat", "base_url", "http://127.0.0.1:11434"),
            model=_setting(config, "szene_lektorat", "model", "qwen3:8b"),
            style_profile=_setting(config, "szene_lektorat", "style_profile", ""),
        )
    raise ValueError(f"Unbekannte Prüfung: {check}")


def run_dialog(
    *, projects_root: Path | None = None, config_dir: Path | None = None,
    input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print,
) -> int:
    default_root = Path("/mnt/nfs/schreiben") if Path("/mnt/nfs/schreiben").is_dir() else Path(__file__).resolve().parents[3]
    projects_root = (projects_root or Path(os.environ.get("SCHREIBPROJEKTE_ROOT", default_root))).expanduser()
    config_dir = (config_dir or Path.home() / ".config" / "schreibprojekte").expanduser()
    try:
        projects = discover_projects(projects_root, config_dir)
        output_fn("\nSchreibprojekte – interaktiver Prüfungsdialog\n")
        project = choose(projects, "Projekt", lambda item: item.name, input_fn, output_fn)
        config = load_project_config(project)
        all_files = manuscript_files(project.root, exclude=tuple(config.get("nachtlauf", {}).get("exclude", [])))
        scope = choose(
            ("gesamt", "teil", "datei"), "Umfang",
            lambda item: {"gesamt": "ganzer Roman / gesamtes Projekt", "teil": "Teil oder Akt", "datei": "einzelne Datei"}[item],
            input_fn, output_fn,
        )
        selected = all_files
        selected_act = None
        if scope == "teil":
            selected_act = choose(acts(all_files), "Teil/Akt", lambda item: f"Akt {item} ({item * 100}–{item * 100 + 99})", input_fn, output_fn)
            selected = tuple(path for path in all_files if (numeric_stem(path) or -100) // 100 == selected_act)
        elif scope == "datei":
            selected = (choose(all_files, "Datei", lambda item: str(item.relative_to(project.root)), input_fn, output_fn),)

        checks = [
            ("woerterbuch", "Unbekannte Wörter prüfen und Wörterbuch pflegen"),
            ("korrektorat", "Rechtschreibung, Grammatik und Zeichensetzung"),
            ("sagte", "Sprecherführung und ›sagte‹"),
            ("hlx", "H–L–X-Erklärprüfung"),
            ("wortarten", "Adjektive und Adverbien"),
            ("szenenlektorat", "vollständiges Datei-/Szenenlektorat"),
        ]
        if scope == "teil":
            checks.append(("teillektorat", "Teil-/Aktlektorat"))
        if scope == "gesamt":
            checks.append(("gesamtlektorat", "Gesamtromanlektorat"))
        check, title = choose(tuple(checks), "Prüfung", lambda item: item[1], input_fn, output_fn)
        output_fn(f"\nAuswahl: {project.name} · {scope} · {title} · {len(selected)} Datei(en)")
        if input_fn("Prüfung starten? [j/N]: ").strip().casefold() != "j":
            output_fn("Abgebrochen.")
            return 0
        if check == "woerterbuch":
            review_unknown_words(project.root, selected, config, input_fn=input_fn, output_fn=output_fn)
            return 0
        if check in {"teillektorat", "gesamtlektorat"}:
            level = "teil" if check == "teillektorat" else "gesamt"
            start = selected_act * 100 if selected_act is not None else None
            end = start + 99 if start is not None else None
            report = run_redaktion(
                project.root, level=level, start=start, end=end,
                label=f"Akt-{selected_act}" if selected_act is not None else None,
                base_url=_setting(config, f"{level}_lektorat", "base_url", "http://127.0.0.1:11434"),
                model=_setting(config, f"{level}_lektorat", "model", "qwen3:8b"),
                style_profile=_setting(config, f"{level}_lektorat", "style_profile", ""),
            )
            output_fn(f"✓ Bericht: {report}")
            return 0
        for index, source in enumerate(selected, 1):
            output_fn(f"[{index}/{len(selected)}] {source.name}")
            output_fn(f"  ✓ {run_file_check(check, source, config)}")
        return 0
    except KeyboardInterrupt:
        output_fn("\nDialog beendet.")
        return 0
    except (OSError, TypeError, ValueError, RuntimeError) as error:
        output_fn(f"❌ Dialog fehlgeschlagen: {error}")
        return 1
