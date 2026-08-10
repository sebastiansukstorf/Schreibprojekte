#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PARENT_DIR = REPO_ROOT.parent
DEFAULT_CONFIG = REPO_ROOT / ".manuskript.json"


def load_config(config_path: Path | None = None) -> dict:
    config_path = config_path or DEFAULT_CONFIG
    if not config_path.exists():
        return {}
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return {}


def detect_default_source(repo_root: Path | None = None) -> Path:
    repo_root = repo_root or REPO_ROOT
    for candidate in [repo_root / "Testprojekt", repo_root.parent / "Testprojekt", repo_root / "03_Content", repo_root]:
        if candidate.exists():
            if candidate.name == "03_Content":
                return candidate.parent
            return candidate
    return (repo_root.parent / "Testprojekt").resolve()


def resolve_target(raw_path: str | None, cwd: Path | None = None, repo_root: Path | None = None) -> Path:
    repo_root = repo_root or REPO_ROOT
    cwd_value = cwd or Path(os.environ.get("PWD") or Path.cwd())
    if not cwd_value.is_absolute():
        cwd_value = (repo_root / cwd_value).resolve()

    if raw_path is None:
        config = load_config()
        if config.get("source"):
            source_value = config["source"]
            source_path = Path(source_value).expanduser()
            if not source_path.is_absolute():
                source_path = (repo_root / source_value).resolve()
            return source_path
        return detect_default_source(repo_root)

    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = (cwd_value / path).resolve()
    return path


def resolve_output_target(raw_path: str | None, repo_root: Path | None = None, source_dir: Path | None = None) -> str | None:
    if raw_path is None:
        return None

    repo_root = repo_root or REPO_ROOT
    base_dir = source_dir or repo_root
    if base_dir.name == "03_Content":
        base_dir = base_dir.parent
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return str(path)
    return str((base_dir / path).resolve())


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="manuskript",
        description="Werkzeuge für die Markdown-basierte Schreibumgebung",
    )
    subparsers = parser.add_subparsers(dest="command")

    export_parser = subparsers.add_parser("export", help="Exportiere Markdown-Dateien als DOCX")
    export_subparsers = export_parser.add_subparsers(dest="export_command")

    docx_parser = export_subparsers.add_parser("docx", help="Exportiere Markdown-Dateien als DOCX")
    docx_parser.add_argument(
        "source",
        nargs="?",
        help="Pfad zum Quellordner oder einer Markdown-Datei (optional)",
    )
    docx_parser.add_argument(
        "--output",
        help="Optionaler Zielordner oder Zielpfad für die DOCX-Ausgabe",
    )
    docx_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )

    single_parser = export_subparsers.add_parser("single", help="Exportiere eine einzelne Markdown-Datei als DOCX")

    top_docx_parser = subparsers.add_parser("docx", help="Alias für `manuskript export docx`")
    top_docx_parser.add_argument(
        "source",
        nargs="?",
        help="Pfad zum Quellordner oder einer Markdown-Datei (optional)",
    )
    top_docx_parser.add_argument(
        "--output",
        help="Optionaler Zielordner oder Zielpfad für die DOCX-Ausgabe",
    )
    top_docx_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )

    top_single_parser = subparsers.add_parser("single", help="Alias für `manuskript export single`")
    top_single_parser.add_argument("path", help="Pfad zur Markdown-Datei")
    top_single_parser.add_argument(
        "--output",
        help="Optionaler Zielordner oder Zielpfad für die DOCX-Ausgabe",
    )
    top_single_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )
    single_parser.add_argument("path", help="Pfad zur Markdown-Datei")

    config_parser = subparsers.add_parser("config", help="Zeige die verwendete Konfiguration an")
    config_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )
    single_parser.add_argument(
        "--output",
        help="Optionaler Zielordner oder Zielpfad für die DOCX-Ausgabe",
    )
    single_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )

    args = parser.parse_args()
    config_path = Path(args.config).expanduser()
    if not config_path.is_absolute():
        config_path = (REPO_ROOT / config_path).resolve()

    if args.command == "docx":
        source_dir = resolve_target(args.source, repo_root=REPO_ROOT)
        if not source_dir.exists():
            print(f"❌ Quellordner nicht gefunden: {source_dir}", file=sys.stderr)
            return 1

        script = REPO_ROOT / "Skripte" / "convert-to-docx.sh"
        if not script.exists():
            print(f"❌ Export-Skript nicht gefunden: {script}", file=sys.stderr)
            return 1

        command = [str(script), str(source_dir)]
        output_value = resolve_output_target(args.output or load_config(config_path).get("output"), REPO_ROOT, source_dir)
        if output_value:
            command.append(output_value)
        subprocess.run(command, cwd=REPO_ROOT, check=True)
        return 0

    if args.command == "single":
        input_path = Path(args.path).expanduser()
        if not input_path.exists():
            print(f"❌ Datei nicht gefunden: {input_path}", file=sys.stderr)
            return 1

        script = REPO_ROOT / "Skripte" / "convert-to-docx-single.sh"
        if not script.exists():
            print(f"❌ Export-Skript nicht gefunden: {script}", file=sys.stderr)
            return 1

        command = [str(script), str(input_path)]
        output_value = resolve_output_target(args.output or load_config(config_path).get("output"), REPO_ROOT, input_path.parent)
        if output_value:
            command.append(output_value)
        subprocess.run(command, cwd=REPO_ROOT, check=True)
        return 0

    if args.command == "config":
        cfg = load_config(config_path)
        print(json.dumps({"config": str(config_path), "source": cfg.get("source"), "output": cfg.get("output")}, indent=2))
        return 0

    if args.command == "export":
        if args.export_command == "docx":
            source_dir = resolve_target(args.source, repo_root=REPO_ROOT)
            if not source_dir.exists():
                print(f"❌ Quellordner nicht gefunden: {source_dir}", file=sys.stderr)
                return 1

            script = REPO_ROOT / "Skripte" / "convert-to-docx.sh"
            if not script.exists():
                print(f"❌ Export-Skript nicht gefunden: {script}", file=sys.stderr)
                return 1

            command = [str(script), str(source_dir)]
            output_value = resolve_output_target(args.output or load_config(config_path).get("output"), REPO_ROOT, source_dir)
            if output_value:
                command.append(output_value)
            subprocess.run(command, cwd=REPO_ROOT, check=True)
            return 0

        if args.export_command == "single":
            input_path = Path(args.path).expanduser()
            if not input_path.exists():
                print(f"❌ Datei nicht gefunden: {input_path}", file=sys.stderr)
                return 1

            script = REPO_ROOT / "Skripte" / "convert-to-docx-single.sh"
            if not script.exists():
                print(f"❌ Export-Skript nicht gefunden: {script}", file=sys.stderr)
                return 1

            command = [str(script), str(input_path)]
            output_value = resolve_output_target(args.output or load_config(config_path).get("output"), REPO_ROOT, input_path.parent)
            if output_value:
                command.append(output_value)
            subprocess.run(command, cwd=REPO_ROOT, check=True)
            return 0

        parser.print_help()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
