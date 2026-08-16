"""Unveraenderliche, per Inhaltspruefsumme gebundene Lektoratslaeufe."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from manuskript.nachtlauf import manuscript_files


@dataclass(frozen=True)
class RevisionRun:
    project: Path
    revision: str
    next_revision: str
    run_id: str
    root: Path
    scene_dir: Path
    manifest_path: Path
    digest: str
    snapshot_project: Path


def revision_slug(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Die Überarbeitung darf nicht leer sein.")
    slug = re.sub(r"[^0-9A-Za-zÄÖÜäöüß._-]+", "-", value).strip("-.")
    if not slug or slug in {".", ".."}:
        raise ValueError("Ungültige Bezeichnung der Überarbeitung.")
    return slug


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot(project: Path, *, exclude: tuple[str, ...] = ()) -> tuple[list[dict], str]:
    project = project.resolve().parent if project.resolve().name == "03_Content" else project.resolve()
    entries = []
    combined = hashlib.sha256()
    for path in manuscript_files(project, exclude=exclude):
        relative = path.relative_to(project).as_posix()
        checksum = file_sha256(path)
        entry = {"path": relative, "sha256": checksum, "bytes": path.stat().st_size}
        entries.append(entry)
        combined.update(relative.encode("utf-8"))
        combined.update(b"\0")
        combined.update(checksum.encode("ascii"))
        combined.update(b"\n")
    return entries, combined.hexdigest()


def create_revision_run(
    project: Path,
    *,
    revision: str,
    next_revision: str | None = None,
    exclude: tuple[str, ...] = (),
    now: datetime | None = None,
) -> RevisionRun:
    project = project.resolve().parent if project.resolve().name == "03_Content" else project.resolve()
    revision_value = revision.strip()
    next_value = (next_revision or revision_value).strip()
    revision_dir = project / "lektorat" / "ueberarbeitungen" / revision_slug(revision_value)
    files, digest = snapshot(project, exclude=exclude)
    timestamp = (now or datetime.now().astimezone()).strftime("%Y%m%d-%H%M%S")
    run_id = f"{timestamp}-{digest[:8]}"
    root = revision_dir / run_id
    if root.exists():
        raise ValueError(f"Lektoratslauf existiert bereits: {root}")
    scene_dir = root / "szene"
    scene_dir.mkdir(parents=True)
    snapshot_project = project / "lektorat" / ".arbeitskopien" / run_id
    if snapshot_project.exists():
        raise ValueError(f"Temporäre Arbeitskopie existiert bereits: {snapshot_project}")
    for source in sorted(project.rglob("*.md")):
        relative = source.relative_to(project)
        if "lektorat" in {part.casefold() for part in relative.parts}:
            continue
        target = snapshot_project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    manifest_path = root / "manifest.json"
    manifest = {
        "schema": 1,
        "project": project.name,
        "revision": revision_value,
        "next_revision": next_value,
        "run_id": run_id,
        "created_at": (now or datetime.now().astimezone()).isoformat(timespec="seconds"),
        "source_digest": digest,
        "files": files,
        "status": "running",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return RevisionRun(
        project, revision_value, next_value, run_id, root, scene_dir, manifest_path, digest,
        snapshot_project,
    )


def finish_revision_run(run: RevisionRun, *, exclude: tuple[str, ...], failed: int) -> dict:
    files, digest = snapshot(run.project, exclude=exclude)
    manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
    manifest["finished_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    manifest["result_failures"] = failed
    manifest["source_unchanged"] = digest == run.digest
    manifest["status"] = "complete" if failed == 0 and digest == run.digest else "attention"
    manifest["final_source_digest"] = digest
    manifest["final_files"] = files
    run.manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def load_revision_run(project: Path, value: str) -> RevisionRun:
    """Lade einen unvollstaendigen Lauf samt unveraenderter Arbeitskopie."""
    project = project.resolve().parent if project.resolve().name == "03_Content" else project.resolve()
    root = resolve_run(project, value)
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") == "complete":
        raise ValueError(f"Lektoratslauf ist bereits vollständig: {root}")
    run_id = str(manifest["run_id"])
    snapshot_project = project / "lektorat" / ".arbeitskopien" / run_id
    if not (snapshot_project / "03_Content").is_dir():
        raise ValueError(f"Arbeitskopie für die Wiederaufnahme fehlt: {snapshot_project}")
    manifest["resumed_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    manifest["resume_count"] = int(manifest.get("resume_count", 0)) + 1
    manifest["status"] = "running"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return RevisionRun(
        project=project,
        revision=str(manifest["revision"]),
        next_revision=str(manifest["next_revision"]),
        run_id=run_id,
        root=root,
        scene_dir=root / "szene",
        manifest_path=manifest_path,
        digest=str(manifest["source_digest"]),
        snapshot_project=snapshot_project,
    )


def cleanup_snapshot(run: RevisionRun) -> None:
    if run.snapshot_project.is_dir():
        shutil.rmtree(run.snapshot_project)
    parent = run.snapshot_project.parent
    if parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()


def snapshot_context(run: RevisionRun, context_path: Path | None) -> Path | None:
    if context_path is None:
        return None
    context_path = context_path.resolve()
    try:
        relative = context_path.relative_to(run.project)
    except ValueError:
        return context_path
    candidate = run.snapshot_project / relative
    if not candidate.exists():
        raise ValueError(f"Kontext fehlt in der Arbeitskopie: {candidate}")
    return candidate


def resolve_run(project: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_dir():
        return candidate.resolve()
    project = project.resolve().parent if project.resolve().name == "03_Content" else project.resolve()
    revision_dir = project / "lektorat" / "ueberarbeitungen" / revision_slug(value)
    runs = sorted(path for path in revision_dir.iterdir() if path.is_dir()) if revision_dir.is_dir() else []
    if not runs:
        raise ValueError(f"Kein Lektoratslauf für Überarbeitung {value!r} gefunden.")
    return runs[-1]
