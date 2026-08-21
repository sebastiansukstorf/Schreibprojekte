"""Rechtschreib- und Zeichensetzungspruefung mit LanguageTool."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "http://127.0.0.1:8081"
OFFICIAL_RULES_URL = "https://www.rechtschreibrat.com/DOX/RfdR_Amtliches-Regelwerk_2024.pdf"
LANGUAGETOOL_URL = "https://github.com/languagetool-org/languagetool"


@dataclass(frozen=True)
class Finding:
    line: int
    column: int
    kind: str
    message: str
    context: str
    replacements: tuple[str, ...]
    rule_id: str


def default_report_path(source: Path) -> Path:
    source = source.resolve()
    project_dir = source.parent.parent if source.parent.name == "03_Content" else source.parent
    return project_dir / "lektorat" / "szene" / f"{source.stem}-korrektorat.md"


def mask_markdown(content: str) -> str:
    """Blende Markdown-Steuerzeichen aus, ohne Offsets und Zeilen zu verschieben."""
    masked: list[str] = []
    in_fence = False
    for line in content.splitlines(keepends=True):
        body = line[:-1] if line.endswith("\n") else line
        newline = "\n" if line.endswith("\n") else ""
        if re.match(r"^\s*```", body):
            in_fence = not in_fence
            masked.append(" " * len(body) + newline)
            continue
        if in_fence:
            masked.append(" " * len(body) + newline)
            continue
        body = re.sub(r"^(\s*)(#{1,6}|[-*+]\s|>\s)", lambda m: " " * len(m.group(0)), body)
        body = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), body)
        masked.append(body + newline)
    return "".join(masked)


def language_tool_check(
    text: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    language: str = "de-DE",
    timeout: int = 120,
) -> dict:
    """Rufe die dokumentierte LanguageTool-HTTP-API mit Python-Bordmitteln auf."""
    endpoint = f"{base_url.rstrip('/')}/v2/check"
    request = Request(
        endpoint,
        data=urlencode({"text": text, "language": language}).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except (HTTPError, URLError, TimeoutError, ConnectionError) as error:
        raise RuntimeError(f"LanguageTool unter {endpoint} ist nicht erreichbar: {error}") from error
    if not isinstance(result, dict) or not isinstance(result.get("matches"), list):
        raise RuntimeError("LanguageTool lieferte keine auswertbare Antwort.")
    return result


def finding_kind(match: dict) -> str | None:
    """Beschraenke LanguageTool bewusst auf Orthografie und Zeichensetzung."""
    rule = match.get("rule") or {}
    category = rule.get("category") or {}
    category_id = str(category.get("id", "")).upper()
    rule_id = str(rule.get("id", "")).upper()
    issue_type = str(rule.get("issueType", "")).lower()
    if issue_type == "misspelling" or category_id in {"TYPOS", "CASING"}:
        return "Rechtschreibung"
    punctuation_markers = ("PUNCT", "COMMA", "KOMMA", "WHITESPACE")
    if category_id in {"TYPOGRAPHY", "PUNCTUATION"} or any(
        marker in rule_id for marker in punctuation_markers
    ):
        return "Zeichensetzung"
    if issue_type == "grammar" or category_id == "GRAMMAR":
        return "Grammatik"
    return None


def offset_to_line_column(content: str, offset: int) -> tuple[int, int]:
    line = content.count("\n", 0, offset) + 1
    previous_break = content.rfind("\n", 0, offset)
    return line, offset - previous_break


def parse_findings(
    content: str,
    response: dict,
    *,
    checked_content: str | None = None,
    include_quote_typography: bool = False,
) -> list[Finding]:
    findings: list[Finding] = []
    lines = content.splitlines()
    for match in response.get("matches", []):
        kind = finding_kind(match)
        if kind is None:
            continue
        offset = int(match.get("offset", 0))
        length = max(1, int(match.get("length", 1)))
        if checked_content is not None and content[offset : offset + length] != checked_content[offset : offset + length]:
            continue
        line, column = offset_to_line_column(content, offset)
        rule = match.get("rule") or {}
        message = str(match.get("message", "Prüfhinweis"))
        quote_typography = (
            "anführungszeichen" in message.casefold()
            or str(rule.get("id", "")).upper() in {
                "DE_UNPAIRED_QUOTES",
                "FALSCHES_ANFUEHRUNGSZEICHEN",
            }
            or (
                "zeichen ohne sein gegenstück" in message.casefold()
                and any(mark in message for mark in ('„', '“', '»', '«', '"'))
            )
        )
        if quote_typography and not include_quote_typography:
            continue
        replacements = tuple(
            str(item["value"])
            for item in match.get("replacements", [])[:5]
            if isinstance(item, dict) and "value" in item
        )
        findings.append(
            Finding(
                line=line,
                column=column,
                kind=kind,
                message=message,
                context=lines[line - 1].strip() if 0 < line <= len(lines) else "",
                replacements=replacements,
                rule_id=str(rule.get("id", "unbekannt")),
            )
        )
    return sorted(findings, key=lambda item: (item.line, item.column, item.rule_id))


def render_report(source: Path, findings: list[Finding], language: str, base_url: str) -> str:
    spelling = sum(item.kind == "Rechtschreibung" for item in findings)
    punctuation = sum(item.kind == "Zeichensetzung" for item in findings)
    grammar = sum(item.kind == "Grammatik" for item in findings)
    output = [
        f"# Korrektorat: {source.name}",
        "",
        f"Prüfsprache: `{language}` · Engine: LanguageTool über `{base_url}`.",
        f"Fundstellen: {len(findings)} ({spelling} Rechtschreibung, {grammar} Grammatik, "
        f"{punctuation} Zeichensetzung).",
        "",
        "Grundlagen:",
        f"- [Amtliches Regelwerk der deutschen Rechtschreibung 2024]({OFFICIAL_RULES_URL})",
        f"- [LanguageTool – Open-Source-Prüfsoftware]({LANGUAGETOOL_URL})",
        "",
        "> Hinweise sind Korrekturvorschläge, keine automatischen Änderungen. Eigennamen, Figurenrede",
        "> und bewusst gesetzte Abweichungen müssen redaktionell beurteilt werden.",
    ]
    if not findings:
        output.extend(["", "Keine einschlägigen Fundstellen gefunden."])
        return "\n".join(output) + "\n"
    for item in findings:
        escaped = item.context.replace("`", "\\`")
        output.extend(
            [
                "",
                f"- Zeile {item.line}, Spalte {item.column} — {item.kind} — {item.message}",
                f"  - Textstelle: `{escaped}`",
                f"  - Vorschläge: {', '.join(f'`{value}`' for value in item.replacements) if item.replacements else 'keine'}",
                f"  - Regel: `{item.rule_id}`",
            ]
        )
    return "\n".join(output) + "\n"


def run_korrektorat(
    source: Path,
    output: Path | None = None,
    *,
    base_url: str = DEFAULT_BASE_URL,
    language: str = "de-DE",
) -> Path:
    source = source.resolve()
    if not source.is_file() or source.suffix.lower() != ".md":
        raise ValueError(f"Keine Markdown-Datei: {source}")
    if language not in {"de-DE", "de-AT", "de-CH"}:
        raise ValueError("Prüfsprache muss de-DE, de-AT oder de-CH sein.")
    content = source.read_text(encoding="utf-8")
    checked_content = mask_markdown(content)
    response = language_tool_check(checked_content, base_url=base_url, language=language)
    findings = parse_findings(content, response, checked_content=checked_content)
    report = (output or default_report_path(source)).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_report(source, findings, language, base_url), encoding="utf-8")
    return report
