#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from manuskript.hlx_lektorat import run_hlx_lektorat
from manuskript.korrektorat import run_korrektorat
from manuskript.sagte_lektorat import run_sagte_lektorat
from manuskript.wortarten_lektorat import run_wortarten_lektorat


REPO_ROOT = Path(__file__).resolve().parents[2]
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


def resolve_output_target(raw_path: str | None, repo_root: Path | None = None, source_dir: Path | None = None) -> str:
    repo_root = repo_root or REPO_ROOT
    base_dir = source_dir or repo_root
    if base_dir.name == "03_Content":
        base_dir = base_dir.parent
    if raw_path is None:
        return str(base_dir / "docx")

    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return str(path)
    return str(base_dir / path)


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

    lektorat_parser = subparsers.add_parser(
        "lektorat", help="Prüfe 'sagte' in der wörtlichen Rede einer Markdown-Datei"
    )
    lektorat_parser.add_argument("path", help="Pfad zur ausgewählten Markdown-Datei")
    lektorat_parser.add_argument("--output", help="Optionaler Pfad für den Markdown-Bericht")
    lektorat_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )
    hlx_parser = subparsers.add_parser(
        "lektorat-hlx", help="Prüfe Erklärungen nach dem H-L-X-System"
    )
    hlx_parser.add_argument("path", help="Pfad zur ausgewählten Markdown-Datei")
    hlx_parser.add_argument("--output", help="Optionaler Pfad für den Markdown-Bericht")
    hlx_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )
    korrektur_parser = subparsers.add_parser(
        "korrektorat", help="Prüfe Rechtschreibung und Zeichensetzung mit LanguageTool"
    )
    korrektur_parser.add_argument("path", help="Pfad zur ausgewählten Markdown-Datei")
    korrektur_parser.add_argument("--output", help="Optionaler Pfad für den Markdown-Bericht")
    korrektur_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )
    wortarten_parser = subparsers.add_parser(
        "lektorat-wortarten", help="Prüfe Adjektive und Adverbien nach Leonard und Higgins"
    )
    wortarten_parser.add_argument("path", help="Pfad zur ausgewählten Markdown-Datei")
    wortarten_parser.add_argument("--output", help="Optionaler Pfad für den Markdown-Bericht")
    wortarten_parser.add_argument(
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
    config_path = Path(getattr(args, "config", DEFAULT_CONFIG)).expanduser()
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

    if args.command == "lektorat":
        input_path = Path(args.path).expanduser().resolve()
        output_path = Path(args.output).expanduser().resolve() if args.output else None
        lektorat_config = load_config(config_path).get("lektorat", {})
        try:
            report = run_sagte_lektorat(
                input_path,
                output_path,
                base_url=lektorat_config.get("base_url", "http://127.0.0.1:11434"),
                model=lektorat_config.get("model", "llama3.1:8b"),
                context_lines=int(lektorat_config.get("context_lines", 4)),
                batch_size=int(lektorat_config.get("batch_size", 4)),
            )
        except (TypeError, ValueError, RuntimeError) as error:
            print(f"❌ Lektorat fehlgeschlagen: {error}", file=sys.stderr)
            return 1
        print(f"✅ Lektoratsbericht: {report}")
        return 0

    if args.command == "lektorat-hlx":
        input_path = Path(args.path).expanduser().resolve()
        output_path = Path(args.output).expanduser().resolve() if args.output else None
        config = load_config(config_path)
        common_config = config.get("lektorat", {})
        hlx_config = config.get("hlx_lektorat", {})
        try:
            report = run_hlx_lektorat(
                input_path,
                output_path,
                base_url=hlx_config.get(
                    "base_url", common_config.get("base_url", "http://127.0.0.1:11434")
                ),
                model=hlx_config.get("model", common_config.get("model", "llama3.1:8b")),
                context_lines=int(hlx_config.get("context_lines", 2)),
                batch_size=int(hlx_config.get("batch_size", 8)),
            )
        except (TypeError, ValueError, RuntimeError) as error:
            print(f"❌ H-L-X-Lektorat fehlgeschlagen: {error}", file=sys.stderr)
            return 1
        print(f"✅ H-L-X-Lektoratsbericht: {report}")
        return 0

    if args.command == "korrektorat":
        input_path = Path(args.path).expanduser().resolve()
        output_path = Path(args.output).expanduser().resolve() if args.output else None
        korrektur_config = load_config(config_path).get("korrektorat", {})
        try:
            report = run_korrektorat(
                input_path,
                output_path,
                base_url=korrektur_config.get("base_url", "http://127.0.0.1:8081"),
                language=korrektur_config.get("language", "de-DE"),
            )
        except (TypeError, ValueError, RuntimeError) as error:
            print(f"❌ Korrektorat fehlgeschlagen: {error}", file=sys.stderr)
            return 1
        print(f"✅ Korrektoratsbericht: {report}")
        return 0

    if args.command == "lektorat-wortarten":
        input_path = Path(args.path).expanduser().resolve()
        output_path = Path(args.output).expanduser().resolve() if args.output else None
        config = load_config(config_path)
        common_config = config.get("lektorat", {})
        wortarten_config = config.get("wortarten_lektorat", {})
        try:
            report = run_wortarten_lektorat(
                input_path,
                output_path,
                base_url=wortarten_config.get(
                    "base_url", common_config.get("base_url", "http://127.0.0.1:11434")
                ),
                model=wortarten_config.get(
                    "model", common_config.get("model", "llama3.1:8b")
                ),
                batch_size=int(wortarten_config.get("batch_size", 8)),
            )
        except (TypeError, ValueError, RuntimeError) as error:
            print(f"❌ Wortarten-Lektorat fehlgeschlagen: {error}", file=sys.stderr)
            return 1
        print(f"✅ Wortarten-Lektoratsbericht: {report}")
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
