"""Resumierbarer Nachtlauf fuer alle Datei-/Szenenpruefungen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from manuskript.notifications import act_number

from manuskript.hlx_lektorat import default_report_path as hlx_report_path
from manuskript.hlx_lektorat import run_hlx_lektorat
from manuskript.korrektorat import default_report_path as korrektur_report_path
from manuskript.korrektorat import run_korrektorat
from manuskript.redaktion import default_report_path as redaktion_report_path
from manuskript.redaktion import load_manuscript, run_redaktion
from manuskript.sagte_lektorat import default_report_path as sagte_report_path
from manuskript.sagte_lektorat import run_sagte_lektorat
from manuskript.wortarten_lektorat import default_report_path as wortarten_report_path
from manuskript.wortarten_lektorat import run_wortarten_lektorat


@dataclass(frozen=True)
class CheckResult:
    source: Path
    check: str
    status: str
    report: Path | None = None
    error: str | None = None


def content_directory(project: Path) -> Path:
    project = project.resolve()
    if project.name == "03_Content":
        return project
    candidate = project / "03_Content"
    if not candidate.is_dir():
        raise ValueError(f"03_Content nicht gefunden: {candidate}")
    return candidate


def manuscript_files(project: Path, *, exclude: tuple[str, ...] = ()) -> tuple[Path, ...]:
    root = content_directory(project)
    files = []
    for path in sorted(root.rglob("*.md")):
        if "lektorat" in {part.lower() for part in path.parts}:
            continue
        relative = path.relative_to(root)
        if any(relative.match(pattern) or path.name == pattern for pattern in exclude):
            continue
        files.append(path.resolve())
    if not files:
        raise ValueError(f"Keine Markdown-Dateien in {root} gefunden.")
    return tuple(files)


def report_is_current(source: Path, report: Path) -> bool:
    return report.is_file() and report.stat().st_mtime >= source.stat().st_mtime


def _setting(config: dict, section: str, name: str, default):
    common = config.get("lektorat", {})
    return config.get(section, {}).get(name, common.get(name, default))


def scene_report_path(source: Path) -> Path:
    manuscript = load_manuscript(source, level="szene")
    return redaktion_report_path(manuscript, level="szene")


def run_night_checks(
    project: Path,
    config: dict,
    *,
    force: bool = False,
    context_path: Path | None = None,
    output_root: Path | None = None,
    progress: Callable[[str], None] = print,
    scene_completed: Callable[[int, int, Path, list[CheckResult], bool], None] | None = None,
) -> list[CheckResult]:
    """Fuehre alle Szenenpruefungen aus und fahre nach Einzelfehlern fort."""
    night_config = config.get("nachtlauf", {})
    raw_exclude = night_config.get("exclude", [])
    if not isinstance(raw_exclude, list) or not all(isinstance(item, str) for item in raw_exclude):
        raise ValueError("nachtlauf.exclude muss eine Liste von Dateinamen oder Glob-Mustern sein.")
    files = manuscript_files(project, exclude=tuple(raw_exclude))
    if output_root is not None:
        output_root = output_root.expanduser().resolve()
        output_root.mkdir(parents=True, exist_ok=True)
    if context_path is None and night_config.get("context"):
        configured_context = Path(str(night_config["context"])).expanduser()
        root = project.resolve().parent if project.resolve().name == "03_Content" else project.resolve()
        context_path = configured_context if configured_context.is_absolute() else root / configured_context
    results: list[CheckResult] = []
    total = len(files)
    for index, source in enumerate(files, start=1):
        progress(f"[{index}/{total}] {source.name}")
        common = config.get("lektorat", {})
        redaktion = config.get("redaktion", {})
        scene = config.get("szene_lektorat", {})
        final_reports = {
            "korrektorat": output_root / f"{source.stem}-korrektorat.md" if output_root else korrektur_report_path(source),
            "sagte": output_root / f"{source.stem}-sagte-lektorat.md" if output_root else sagte_report_path(source),
            "hlx": output_root / f"{source.stem}-hlx-lektorat.md" if output_root else hlx_report_path(source),
            "wortarten": output_root / f"{source.stem}-adjektive-adverbien-lektorat.md" if output_root else wortarten_report_path(source),
            "szenenlektorat": output_root / f"{source.stem}_lektorat.md" if output_root else scene_report_path(source),
        }

        def working_path(name: str) -> Path | None:
            report = final_reports[name]
            return report.with_suffix(report.suffix + ".partial") if output_root else None

        checks = (
            (
                "korrektorat",
                final_reports["korrektorat"],
                lambda: run_korrektorat(
                    source,
                    output=working_path("korrektorat"),
                    base_url=config.get("korrektorat", {}).get("base_url", "http://127.0.0.1:8081"),
                    language=config.get("korrektorat", {}).get("language", "de-DE"),
                ),
            ),
            (
                "sagte",
                final_reports["sagte"],
                lambda: run_sagte_lektorat(
                    source,
                    output=working_path("sagte"),
                    base_url=common.get("base_url", "http://127.0.0.1:11434"),
                    model=common.get("model", "qwen3:8b"),
                    context_lines=int(common.get("context_lines", 4)),
                    batch_size=int(common.get("batch_size", 4)),
                ),
            ),
            (
                "hlx",
                final_reports["hlx"],
                lambda: run_hlx_lektorat(
                    source,
                    output=working_path("hlx"),
                    base_url=_setting(config, "hlx_lektorat", "base_url", "http://127.0.0.1:11434"),
                    model=_setting(config, "hlx_lektorat", "model", "qwen3:8b"),
                    context_lines=int(_setting(config, "hlx_lektorat", "context_lines", 2)),
                    batch_size=int(_setting(config, "hlx_lektorat", "batch_size", 8)),
                ),
            ),
            (
                "wortarten",
                final_reports["wortarten"],
                lambda: run_wortarten_lektorat(
                    source,
                    output=working_path("wortarten"),
                    base_url=_setting(config, "wortarten_lektorat", "base_url", "http://127.0.0.1:11434"),
                    model=_setting(config, "wortarten_lektorat", "model", "qwen3:8b"),
                    batch_size=int(_setting(config, "wortarten_lektorat", "batch_size", 8)),
                ),
            ),
            (
                "szenenlektorat",
                final_reports["szenenlektorat"],
                lambda: run_redaktion(
                    source,
                    level="szene",
                    output=working_path("szenenlektorat"),
                    context_path=context_path,
                    base_url=scene.get("base_url", redaktion.get("base_url", common.get("base_url", "http://127.0.0.1:11434"))),
                    model=scene.get("model", redaktion.get("model", common.get("model", "qwen3:8b"))),
                    style_profile=scene.get("style_profile", redaktion.get("style_profile", "")),
                    max_manuscript_chars=int(scene.get("max_manuscript_chars", redaktion.get("max_manuscript_chars", 300_000))),
                    max_context_chars=int(scene.get("max_context_chars", redaktion.get("max_context_chars", 80_000))),
                ),
            ),
        )
        for name, report, runner in checks:
            if not force and report_is_current(source, report):
                progress(f"  ↷ {name}: aktuell, übersprungen")
                results.append(CheckResult(source, name, "skipped", report=report))
                continue
            try:
                written = runner()
            except (OSError, TypeError, ValueError, RuntimeError) as error:
                progress(f"  ✗ {name}: {error}")
                results.append(CheckResult(source, name, "failed", error=str(error)))
                continue
            if output_root:
                written = Path(written)
                written.replace(report)
                written = report
            progress(f"  ✓ {name}: {written}")
            results.append(CheckResult(source, name, "completed", report=written))
        if scene_completed:
            next_act = act_number(files[index]) if index < total else None
            scene_completed(index, total, source, results[-len(checks):], act_number(source) != next_act)
    return results


def render_summary(project: Path, results: list[CheckResult]) -> str:
    completed = sum(item.status == "completed" for item in results)
    skipped = sum(item.status == "skipped" for item in results)
    failed = sum(item.status == "failed" for item in results)
    lines = [
        "# Lektorat-Nachtlauf",
        "",
        f"Projekt: `{project.resolve()}`  ",
        f"Beendet: {datetime.now().astimezone().isoformat(timespec='seconds')}  ",
        f"Erfolgreich: {completed} · Übersprungen: {skipped} · Fehlgeschlagen: {failed}",
        "",
        "| Datei | Prüfung | Status | Bericht/Fehler |",
        "| --- | --- | --- | --- |",
    ]
    for item in results:
        detail = str(item.report) if item.report else (item.error or "")
        detail = detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{item.source.name}` | {item.check} | {item.status} | {detail} |")
    return "\n".join(lines) + "\n"


def write_summary(project: Path, results: list[CheckResult], *, output: Path | None = None) -> Path:
    root = project.resolve().parent if project.resolve().name == "03_Content" else project.resolve()
    output = output or root / "lektorat" / "logs" / "nachtlauf_letzter.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_summary(root, results), encoding="utf-8")
    return output
