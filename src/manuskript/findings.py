"""Normalisiere Lektoratsberichte fuer Aufgabenexporte."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    id: str
    file: str
    line: int
    column: int | None
    check: str
    category: str
    relevance: str
    quote: str
    diagnosis: str
    recommendation: str
    report: str
    source_sha256: str


def _fingerprint(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _source_index(manifest: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in manifest.get("files", []):
        path = str(item.get("path", ""))
        if path:
            result[Path(path).stem] = item
    return result


def _make(
    *, source: dict, line: int, column: int | None, check: str, category: str,
    relevance: str, quote: str, diagnosis: str, recommendation: str, report: Path,
) -> Finding:
    identity = {
        "source_sha256": source.get("sha256", ""),
        "file": source.get("path", ""),
        "line": line,
        "check": check,
        "category": category,
        "diagnosis": diagnosis.strip(),
        "recommendation": recommendation.strip(),
    }
    return Finding(
        id=_fingerprint(identity), file=str(source.get("path", "")), line=line,
        column=column, check=check, category=category, relevance=relevance,
        quote=quote.strip(), diagnosis=diagnosis.strip(), recommendation=recommendation.strip(),
        report=report.as_posix(), source_sha256=str(source.get("sha256", "")),
    )


def _quote_after(lines: list[str], index: int) -> str:
    for line in lines[index + 1 : index + 4]:
        match = re.match(r"\s+- Textstelle:\s*`(.*)`\s*$", line)
        if match:
            return match.group(1).replace("\\`", "`")
    return ""


def _parse_korrektorat(report: Path, source: dict) -> list[Finding]:
    lines = report.read_text(encoding="utf-8").splitlines()
    result = []
    pattern = re.compile(r"^- Zeile (\d+), Spalte (\d+) — (.+?) — (.+)$")
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        proposals = ""
        for detail in lines[index + 1 : index + 4]:
            proposal = re.match(r"\s+- Vorschläge:\s*(.+)$", detail)
            if proposal:
                proposals = proposal.group(1).replace("`", "")
                break
        recommendation = f"Vorschläge prüfen: {proposals}" if proposals and proposals != "keine" else "Fundstelle prüfen."
        result.append(_make(
            source=source, line=int(match.group(1)), column=int(match.group(2)),
            check="korrektorat", category=match.group(3), relevance="mittel",
            quote=_quote_after(lines, index), diagnosis=match.group(4),
            recommendation=recommendation, report=report,
        ))
    return result


def _parse_sagte(report: Path, source: dict) -> list[Finding]:
    lines = report.read_text(encoding="utf-8").splitlines()
    result = []
    pattern = re.compile(r"^- Zeile (\d+) — (STREICHEN|BEHALTEN) — (.+)$", re.IGNORECASE)
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match or match.group(2).upper() != "STREICHEN":
            continue
        result.append(_make(
            source=source, line=int(match.group(1)), column=None, check="sagte",
            category="Sprecherführung", relevance="mittel", quote=_quote_after(lines, index),
            diagnosis=match.group(3), recommendation="Sprecherzuordnung auf Streichung prüfen.",
            report=report,
        ))
    return result


def _parse_hlx(report: Path, source: dict) -> list[Finding]:
    lines = report.read_text(encoding="utf-8").splitlines()
    result = []
    pattern = re.compile(r"^- Zeile (\d+) — ([HLX]) — (.+)$", re.IGNORECASE)
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match or match.group(2).upper() == "L":
            continue
        category = match.group(2).upper()
        recommendation = (
            "Information auf szenische Vermittlung prüfen."
            if category == "H" else "Erklärende Doppelung auf Streichung prüfen."
        )
        result.append(_make(
            source=source, line=int(match.group(1)), column=None, check="hlx",
            category=category, relevance="mittel", quote=_quote_after(lines, index),
            diagnosis=match.group(3), recommendation=recommendation, report=report,
        ))
    return result


def _parse_wortarten(report: Path, source: dict) -> list[Finding]:
    lines = report.read_text(encoding="utf-8").splitlines()
    result = []
    pattern = re.compile(
        r"^- Zeile (\d+) — `?([^`]+?)`? — (ADJEKTIV|ADVERB) — "
        r"(STREICHEN|ERSETZEN|BEHALTEN) — (.+)$", re.IGNORECASE,
    )
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match or match.group(4).upper() == "BEHALTEN":
            continue
        suggestion = "im Kontext prüfen"
        for detail in lines[index + 1 : index + 4]:
            proposal = re.match(r"\s+- Vorschlag:\s*(.+)$", detail)
            if proposal:
                suggestion = proposal.group(1)
                break
        result.append(_make(
            source=source, line=int(match.group(1)), column=None, check="wortarten",
            category=f"{match.group(3).title()} {match.group(4).upper()}", relevance="mittel",
            quote=_quote_after(lines, index), diagnosis=match.group(5),
            recommendation=suggestion, report=report,
        ))
    return result


def _parse_scene(report: Path, source: dict) -> list[Finding]:
    lines = report.read_text(encoding="utf-8").splitlines()
    result = []
    module = "Szenenlektorat"
    index = 0
    while index < len(lines):
        if lines[index].startswith("## ") and lines[index] != "## Kurzdiagnose":
            module = lines[index][3:].strip()
        if not lines[index].startswith("### Befund:"):
            index += 1
            continue
        title = lines[index].split(":", 1)[1].strip()
        fields: dict[str, str] = {}
        index += 1
        while index < len(lines) and not lines[index].startswith(("### Befund:", "## ")):
            match = re.match(r"^- (Fundstelle|Diagnose|Relevanz|Begründung|Empfehlung|Querverweise):\s*(.*)$", lines[index])
            if match:
                fields[match.group(1)] = match.group(2).strip()
            index += 1
        location = fields.get("Fundstelle", "")
        line_match = re.search(r"\bZeile\s+(\d+)", location, re.IGNORECASE)
        line_number = int(line_match.group(1)) if line_match else 0
        result.append(_make(
            source=source, line=line_number, column=None, check="szenenlektorat",
            category=module, relevance=fields.get("Relevanz", "mittel").lower(),
            quote="", diagnosis=f"{title}: {fields.get('Diagnose', fields.get('Begründung', ''))}",
            recommendation=fields.get("Empfehlung", "Fundstelle prüfen."), report=report,
        ))
    return result


def collect_findings(run_dir: Path, *, enabled_checks: set[str] | None = None) -> list[Finding]:
    run_dir = run_dir.resolve()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    sources = _source_index(manifest)
    findings: list[Finding] = []
    for report in sorted((run_dir / "szene").glob("*.md")):
        name = report.name
        stem = name.split("-", 1)[0].split("_", 1)[0]
        source = sources.get(stem)
        if not source:
            continue
        if name.endswith("-korrektorat.md"):
            if enabled_checks is not None and "korrektorat" not in enabled_checks:
                continue
            findings.extend(_parse_korrektorat(report, source))
        elif name.endswith("-sagte-lektorat.md"):
            if enabled_checks is not None and "sagte" not in enabled_checks:
                continue
            findings.extend(_parse_sagte(report, source))
        elif name.endswith("-hlx-lektorat.md"):
            if enabled_checks is not None and "hlx" not in enabled_checks:
                continue
            findings.extend(_parse_hlx(report, source))
        elif name.endswith("-adjektive-adverbien-lektorat.md"):
            if enabled_checks is not None and "wortarten" not in enabled_checks:
                continue
            findings.extend(_parse_wortarten(report, source))
        elif name.endswith("_lektorat.md"):
            if enabled_checks is not None and "szenenlektorat" not in enabled_checks:
                continue
            findings.extend(_parse_scene(report, source))
    unique = {item.id: item for item in findings}
    return sorted(unique.values(), key=lambda item: (item.file, item.line, item.check, item.id))


def write_findings(run_dir: Path, findings: list[Finding]) -> Path:
    output = run_dir / "findings.jsonl"
    content = "".join(json.dumps(asdict(item), ensure_ascii=False) + "\n" for item in findings)
    output.write_text(content, encoding="utf-8")
    return output


def read_findings(run_dir: Path) -> list[dict]:
    path = run_dir / "findings.jsonl"
    if not path.is_file():
        raise ValueError(f"Maschinenlesbare Befunde fehlen: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
