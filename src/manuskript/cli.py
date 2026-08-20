#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from manuskript.hlx_lektorat import run_hlx_lektorat
from manuskript.findings import collect_findings, write_findings
from manuskript.korrektorat import run_korrektorat
from manuskript.nachtlauf import run_night_checks, write_summary
from manuskript.notifications import NtfyNotifier, act_number
from manuskript.openproject import preview as openproject_preview
from manuskript.openproject import sync as openproject_sync
from manuskript.redaktion import run_redaktion
from manuskript.revision import (
    cleanup_snapshot,
    create_revision_run,
    finish_revision_run,
    load_revision_run,
    resolve_run,
    snapshot_context,
)
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

    redaktion_parsers = {}
    for command, level, help_text in (
        ("lektorat-szene", "szene", "Prüfe eine Datei mit allen sieben Szenenmodulen"),
        ("lektorat-teil", "teil", "Prüfe einen Teil oder Akt als dramatische Einheit"),
        ("lektorat-gesamt", "gesamt", "Prüfe den vollständigen Roman"),
    ):
        level_parser = subparsers.add_parser(command, help=help_text)
        level_parser.set_defaults(redaktion_level=level)
        level_parser.add_argument("path", help="Markdown-Datei, 03_Content- oder Projektordner")
        level_parser.add_argument("--output", help="Optionaler Pfad für den Markdown-Bericht")
        level_parser.add_argument("--context", help="Optionale Story Bible oder Kontextordner")
        level_parser.add_argument("--label", help="Bezeichnung des Teils für den Ausgabedateinamen")
        level_parser.add_argument("--start", type=int, help="Erste numerische Dateinummer")
        level_parser.add_argument("--end", type=int, help="Letzte numerische Dateinummer")
        level_parser.add_argument(
            "--config",
            default=str(DEFAULT_CONFIG),
            help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
        )
        redaktion_parsers[command] = level_parser

    night_parser = subparsers.add_parser(
        "lektorat-nacht", help="Führe alle Datei-/Szenenprüfungen für 03_Content aus"
    )
    night_parser.add_argument("path", nargs="?", help="Projekt- oder 03_Content-Ordner")
    night_parser.add_argument("--context", help="Optionale Story Bible oder Kontextordner")
    night_parser.add_argument("--force", action="store_true", help="Auch aktuelle Berichte neu erzeugen")
    revision_group = night_parser.add_mutually_exclusive_group()
    revision_group.add_argument("--revision", help="Bezeichnung des unveränderlich geprüften Stands")
    revision_group.add_argument("--resume", help="Unvollständigen Lauf dieses Stands fortsetzen")
    night_parser.add_argument("--next-revision", help="Zielüberarbeitung für die spätere Aufgabenliste")
    night_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Pfad zur Konfigurationsdatei (Standard: .manuskript.json)",
    )
    for command, help_text in (
        ("openproject-preview", "Zeige die geplanten OpenProject-Aufgaben eines Lektoratslaufs"),
        ("openproject-sync", "Übertrage einen Lektoratslauf idempotent nach OpenProject"),
    ):
        openproject_parser = subparsers.add_parser(command, help=help_text)
        openproject_parser.add_argument("path", help="Projektordner")
        openproject_parser.add_argument(
            "--run", required=True,
            help="Laufverzeichnis oder Überarbeitungsbezeichnung (verwendet den neuesten Lauf)",
        )
        openproject_parser.add_argument(
            "--config", default=str(DEFAULT_CONFIG),
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
                fallback_model=hlx_config.get(
                    "fallback_model", hlx_config.get("model", common_config.get("model", "llama3.1:8b"))
                ),
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

    if args.command in redaktion_parsers:
        input_path = Path(args.path).expanduser().resolve()
        output_path = Path(args.output).expanduser().resolve() if args.output else None
        context_path = Path(args.context).expanduser().resolve() if args.context else None
        config = load_config(config_path)
        common_config = config.get("lektorat", {})
        redaktion_config = config.get("redaktion", {})
        level_config = config.get(f"{args.redaktion_level}_lektorat", {})

        def setting(name, default):
            return level_config.get(name, redaktion_config.get(name, common_config.get(name, default)))

        try:
            report = run_redaktion(
                input_path,
                level=args.redaktion_level,
                output=output_path,
                label=args.label,
                start=args.start,
                end=args.end,
                context_path=context_path,
                base_url=setting("base_url", "http://127.0.0.1:11434"),
                model=setting("model", "qwen3:8b"),
                style_profile=setting("style_profile", ""),
                max_manuscript_chars=int(setting("max_manuscript_chars", 300_000)),
                max_context_chars=int(setting("max_context_chars", 80_000)),
            )
        except (TypeError, ValueError, RuntimeError) as error:
            print(f"❌ {args.redaktion_level.capitalize()}-Lektorat fehlgeschlagen: {error}", file=sys.stderr)
            return 1
        print(f"✅ {args.redaktion_level.capitalize()}-Lektoratsbericht: {report}")
        return 0

    if args.command == "lektorat-nacht":
        input_path = resolve_target(args.path, repo_root=REPO_ROOT)
        project_root = input_path.parent if input_path.name == "03_Content" else input_path
        project_config = project_root / ".manuskript.json"
        uses_default_config = config_path.resolve() == DEFAULT_CONFIG.resolve()
        config = load_config(project_config if uses_default_config and project_config.is_file() else config_path)
        context_path = Path(args.context).expanduser().resolve() if args.context else None
        revision_run = None
        notifier = NtfyNotifier.from_config(config)
        raw_exclude = config.get("nachtlauf", {}).get("exclude", [])
        exclude = tuple(raw_exclude) if isinstance(raw_exclude, list) else ()
        try:
            if args.resume and args.next_revision:
                raise ValueError("--next-revision kann bei --resume nicht geändert werden.")
            if args.resume:
                revision_run = load_revision_run(input_path, args.resume)
            elif args.revision:
                revision_run = create_revision_run(
                    input_path,
                    revision=args.revision,
                    next_revision=args.next_revision,
                    exclude=exclude,
                )
            action = "fortgesetzt" if args.resume else "gestartet"
            run_label = revision_run.revision if revision_run else "ohne Revisionsbindung"
            if notifier:
                notifier.send(
                    f"{project_root.name}: Nachtlauf {action}",
                    f"Stand {run_label} · Datei- und Szenenprüfungen laufen.",
                    tags="books,rocket" if not args.resume else "books,arrow_forward",
                )

            def notify_scene(index, total, source, scene_results, act_complete):
                notification_mode = config.get("notifications", {}).get("ntfy", {}).get("progress", "act")
                if not notifier or (notification_mode != "scene" and not act_complete):
                    return
                completed = sum(item.status == "completed" for item in scene_results)
                skipped = sum(item.status == "skipped" for item in scene_results)
                failed_scene = sum(item.status == "failed" for item in scene_results)
                if completed == 0 and failed_scene == 0:
                    return
                act = act_number(source)
                percent = round(index / total * 100)
                if notification_mode == "scene":
                    title = f"{project_root.name}: {source.name} abgeschlossen"
                else:
                    title = f"{project_root.name}: Akt {act} abgeschlossen" if act is not None else f"{project_root.name}: Zwischenstand"
                notifier.send(
                    title,
                    f"{index} von {total} Dateien · {percent} % · "
                    f"{completed} neu · {skipped} bereits fertig · {failed_scene} fehlgeschlagen.",
                    priority=4 if failed_scene else 3,
                    tags="books,warning" if failed_scene else "books,white_check_mark",
                )
            results = run_night_checks(
                revision_run.snapshot_project if revision_run else input_path,
                config,
                force=args.force or (revision_run is not None and not args.resume),
                context_path=snapshot_context(revision_run, context_path) if revision_run else context_path,
                output_root=revision_run.scene_dir if revision_run else None,
                scene_completed=notify_scene,
            )
            summary = write_summary(
                input_path, results,
                output=revision_run.root / "zusammenfassung.md" if revision_run else None,
            )
            if revision_run:
                findings = collect_findings(
                    revision_run.root,
                    enabled_checks={result.check for result in results},
                )
                write_findings(revision_run.root, findings)
                failed = sum(result.status == "failed" for result in results)
                manifest = finish_revision_run(revision_run, exclude=exclude, failed=failed)
                if manifest["status"] == "complete":
                    cleanup_snapshot(revision_run)
                if not manifest["source_unchanged"]:
                    print("⚠️ Manuskript wurde während des Laufs verändert; kein sicherer Importstand.")
        except (OSError, TypeError, ValueError, RuntimeError) as error:
            if notifier:
                notifier.send(
                    f"{project_root.name}: Nachtlauf abgebrochen",
                    str(error), priority=5, tags="books,rotating_light",
                )
            print(f"❌ Nachtlauf konnte nicht gestartet werden: {error}", file=sys.stderr)
            return 1
        failed = sum(result.status == "failed" for result in results)
        if notifier:
            notifier.send(
                f"{project_root.name}: Nachtlauf beendet",
                f"Stand {run_label} · {len(results) - failed} Prüfungen erfolgreich/übersprungen · {failed} fehlgeschlagen.",
                priority=4 if failed else 3,
                tags="books,warning" if failed else "books,tada",
            )
        print(f"Nachtlauf abgeschlossen. Zusammenfassung: {summary}")
        if failed:
            print(f"⚠️ {failed} Prüfung(en) fehlgeschlagen; Details stehen in der Zusammenfassung.")
            return 2
        return 0

    if args.command in {"openproject-preview", "openproject-sync"}:
        project = resolve_target(args.path, repo_root=REPO_ROOT)
        config = load_config(config_path)
        try:
            run_dir = resolve_run(project, args.run)
            if args.command == "openproject-preview":
                rendered = openproject_preview(run_dir, config)
                output = run_dir / "openproject-vorschau.md"
                output.write_text(rendered, encoding="utf-8")
                print(rendered, end="")
                print(f"Vorschau: {output}")
            else:
                result = openproject_sync(run_dir, config)
                print(json.dumps(result, ensure_ascii=False, indent=2))
        except (OSError, TypeError, ValueError, RuntimeError) as error:
            print(f"❌ OpenProject-Export fehlgeschlagen: {error}", file=sys.stderr)
            return 1
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
