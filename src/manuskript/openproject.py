"""Vorschau und idempotenter Export von Lektoratsbefunden nach OpenProject API v3."""

from __future__ import annotations

import json
import os
import hashlib
import base64
from collections import Counter, defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from manuskript.findings import read_findings


RELEVANCE = {"niedrig": 1, "mittel": 2, "hoch": 3}


def _bundle_id(kind: str, file: str, findings: list[dict]) -> str:
    payload = "\0".join([kind, file, *(item["id"] for item in findings)])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _checklist(findings: list[dict]) -> str:
    lines = []
    for item in sorted(findings, key=lambda value: (int(value.get("line", 0)), value["id"])):
        quote_text = str(item.get("quote", "")).replace("\n", " ").strip()
        quote_part = f" — `{quote_text}`" if quote_text else ""
        lines.append(f"- [ ] Zeile {item.get('line', 0)}{quote_part}: {item['diagnosis']}")
    return "\n".join(lines)


def _bundled_finding(kind: str, file: str, findings: list[dict]) -> dict:
    first = findings[0]
    if kind == "sagte":
        category = "Sprecherzuordnungen gesammelt prüfen"
        recommendation = "Alle markierten Sprecherzuordnungen im Szenenkontext einzeln prüfen."
    else:
        category = "Unklare Schreibweisen gesammelt prüfen"
        recommendation = "Unbekannte Namen, Anglizismen und mögliche Tippfehler gesammelt prüfen."
    return {
        **first,
        "id": _bundle_id(kind, file, findings),
        "line": 0,
        "column": None,
        "category": category,
        "quote": "",
        "diagnosis": _checklist(findings),
        "recommendation": recommendation,
    }


def bundle_findings(findings: list[dict], config: dict) -> list[dict]:
    """Bündele prüfpflichtige Kandidaten, ohne ihre Zeilenbezüge zu verlieren."""
    settings = config.get("openproject", {})
    bundle_sagte = bool(settings.get("bundle_sagte_per_scene", True))
    bundle_typos = bool(settings.get("bundle_generic_typos_per_scene", True))
    direct_quote_marks = ('„', '“', '»', '«', '"')
    kept: list[dict] = []
    sagte: dict[str, list[dict]] = defaultdict(list)
    typos: dict[str, list[dict]] = defaultdict(list)
    for finding in findings:
        file = str(finding["file"])
        if finding.get("check") == "sagte":
            if not any(mark in str(finding.get("quote", "")) for mark in direct_quote_marks):
                continue
            if bundle_sagte:
                sagte[file].append(finding)
                continue
        diagnosis = str(finding.get("diagnosis", "")).casefold()
        generic_typo = "möglicher tippfehler" in diagnosis or "möglicherweise ein tippfehler" in diagnosis
        if finding.get("check") == "korrektorat" and generic_typo and bundle_typos:
            typos[file].append(finding)
            continue
        kept.append(finding)
    for file, items in sagte.items():
        kept.append(_bundled_finding("sagte", file, items))
    for file, items in typos.items():
        kept.append(_bundled_finding("korrektorat", file, items))
    return kept


def selected_findings(run_dir: Path, config: dict) -> list[dict]:
    settings = config.get("openproject", {})
    minimum = str(settings.get("minimum_relevance", "mittel")).lower()
    threshold = RELEVANCE.get(minimum)
    if threshold is None:
        raise ValueError("openproject.minimum_relevance muss niedrig, mittel oder hoch sein.")
    cap = int(settings.get("max_tasks_per_scene", 0))
    if cap < 0:
        raise ValueError("openproject.max_tasks_per_scene darf nicht negativ sein.")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for finding in bundle_findings(read_findings(run_dir), config):
        if RELEVANCE.get(str(finding.get("relevance", "mittel")).lower(), 2) >= threshold:
            grouped[str(finding["file"])].append(finding)
    selected = []
    for file in sorted(grouped):
        ordered = sorted(
            grouped[file],
            key=lambda item: (-RELEVANCE.get(str(item.get("relevance", "mittel")).lower(), 2), int(item.get("line", 0)), item["id"]),
        )
        selected.extend(ordered[:cap] if cap else ordered)
    return selected


def preview(run_dir: Path, config: dict) -> str:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    findings = selected_findings(run_dir, config)
    by_file = Counter(item["file"] for item in findings)
    by_check = Counter(item["check"] for item in findings)
    lines = [
        "# OpenProject-Vorschau", "",
        f"Projekt: `{manifest['project']}`  ",
        f"Geprüfter Stand: `{manifest['revision']}`  ",
        f"Zielversion: `{manifest['next_revision']}`  ",
        f"Lauf: `{manifest['run_id']}`  ",
        f"Aufgaben: {len(findings)} in {len(by_file)} Szene(n)", "",
        "## Prüfungen", "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in sorted(by_check.items()))
    lines.extend(["", "## Szenen", ""])
    for file, count in sorted(by_file.items()):
        lines.append(f"- `{file}`: {count} Aufgabe(n)")
    lines.extend(["", "> Es wurden noch keine OpenProject-Daten verändert.", ""])
    return "\n".join(lines)


class OpenProjectClient:
    def __init__(self, base_url: str, token: str, *, timeout: int = 30, auth_scheme: str = "basic"):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.auth_scheme = auth_scheme

    def authorization(self) -> str:
        if self.auth_scheme == "bearer":
            return f"Bearer {self.token}"
        if self.auth_scheme == "basic":
            encoded = base64.b64encode(f"apikey:{self.token}".encode("utf-8")).decode("ascii")
            return f"Basic {encoded}"
        raise ValueError("openproject.auth_scheme muss basic oder bearer sein.")

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}", data=body, method=method,
            headers={
                "Authorization": self.authorization(),
                "Content-Type": "application/json",
                "Accept": "application/hal+json",
                "User-Agent": "Schreibprojekte/0.1 OpenProject-API",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:1000]
            raise RuntimeError(f"OpenProject {method} {path}: HTTP {error.code}: {detail}") from error
        except (URLError, TimeoutError, ConnectionError) as error:
            raise RuntimeError(f"OpenProject ist nicht erreichbar: {error}") from error

    def project(self, identifier: str) -> dict | None:
        try:
            return self.request("GET", f"/api/v3/projects/{quote(identifier, safe='')}")
        except RuntimeError as error:
            if "HTTP 404" in str(error):
                return None
            raise

    def create_project(self, name: str, identifier: str) -> dict:
        return self.request("POST", "/api/v3/projects", {"name": name, "identifier": identifier, "public": False})

    def versions(self, project_id: int) -> list[dict]:
        result = self.request("GET", f"/api/v3/projects/{project_id}/versions?pageSize=200")
        return list(result.get("_embedded", {}).get("elements", []))

    def create_version(self, project_id: int, name: str) -> dict:
        return self.request("POST", "/api/v3/versions", {
            "name": name, "status": "open", "sharing": "none",
            "_links": {"definingProject": {"href": f"/api/v3/projects/{project_id}"}},
        })

    def project_types(self, project_id: int) -> list[dict]:
        result = self.request("GET", f"/api/v3/projects/{project_id}/types")
        return list(result.get("_embedded", {}).get("elements", []))

    def existing_markers(self, project_id: int) -> dict[str, int]:
        query = urlencode({"pageSize": 1000})
        result = self.request("GET", f"/api/v3/projects/{project_id}/work_packages?{query}")
        markers: dict[str, int] = {}
        for item in result.get("_embedded", {}).get("elements", []):
            subject = str(item.get("subject", ""))
            if subject.startswith(("[LKT-", "[LKTSZ-")) and "]" in subject:
                markers[subject[1 : subject.index("]")]] = _id_from_href(item)
        return markers

    def create_work_package(
        self, project_id: int, type_id: int, subject: str, description: str,
        *, version_id: int | None = None, parent_id: int | None = None,
    ) -> dict:
        links: dict[str, dict] = {
            "project": {"href": f"/api/v3/projects/{project_id}"},
            "type": {"href": f"/api/v3/types/{type_id}"},
        }
        if version_id is not None:
            links["version"] = {"href": f"/api/v3/versions/{version_id}"}
        if parent_id is not None:
            links["parent"] = {"href": f"/api/v3/work_packages/{parent_id}"}
        return self.request("POST", "/api/v3/work_packages", {
            "subject": subject,
            "description": {"format": "markdown", "raw": description},
            "_links": links,
        })


def _id_from_href(item: dict) -> int:
    href = str(item.get("_links", {}).get("self", {}).get("href", ""))
    try:
        return int(href.rstrip("/").rsplit("/", 1)[1])
    except (IndexError, ValueError) as error:
        raise RuntimeError(f"OpenProject-Antwort enthält keine ID: {href!r}") from error


def _description(finding: dict, manifest: dict) -> str:
    location = f"Zeile {finding['line']}" if finding.get("line") else "Abschnitt/Szene"
    if finding.get("column"):
        location += f", Spalte {finding['column']}"
    quote_block = f"\n\n**Original**\n\n> {finding['quote']}" if finding.get("quote") else ""
    return (
        f"**Datei:** `{finding['file']}`  \n**Fundstelle:** {location}  \n"
        f"**Prüfung:** {finding['check']} / {finding['category']}  \n"
        f"**Relevanz:** {finding['relevance']}  \n**Geprüfter Stand:** {manifest['revision']}  \n"
        f"**Lektoratslauf:** `{manifest['run_id']}`  \n**Dateiprüfsumme:** `{finding['source_sha256']}`"
        f"{quote_block}\n\n**Diagnose**\n\n{finding['diagnosis']}\n\n"
        f"**Empfehlung**\n\n{finding['recommendation']}\n\n"
        f"<!-- lektorat-id:{finding['id']} -->"
    )


def sync(run_dir: Path, config: dict, *, token: str | None = None) -> dict:
    settings = config.get("openproject", {})
    base_url = str(settings.get("base_url") or os.environ.get("OPENPROJECT_URL") or "").strip()
    token = token or os.environ.get("OPENPROJECT_API_TOKEN")
    if not base_url or not token:
        raise ValueError("OPENPROJECT_URL und OPENPROJECT_API_TOKEN müssen gesetzt sein.")
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "complete" or not manifest.get("source_unchanged"):
        raise ValueError("Nur vollständig erfolgreiche, unveränderte Lektoratsläufe dürfen synchronisiert werden.")
    identifier = str(settings.get("project_identifier") or manifest["project"].lower())
    project_name = str(settings.get("project_name") or manifest["project"])
    client = OpenProjectClient(
        base_url, token, auth_scheme=str(settings.get("auth_scheme", "basic")).lower()
    )
    project = client.project(identifier)
    if project is None:
        if not settings.get("create_project_if_missing", True):
            raise RuntimeError(f"OpenProject-Projekt {identifier!r} fehlt.")
        project = client.create_project(project_name, identifier)
    project_id = _id_from_href(project)
    version_name = str(settings.get("version_prefix", "Überarbeitung")) + f" {manifest['next_revision']}"
    versions = client.versions(project_id)
    version = next((item for item in versions if item.get("name") == version_name), None)
    if version is None:
        version = client.create_version(project_id, version_name)
    version_id = _id_from_href(version)
    types = client.project_types(project_id)
    preferred = str(settings.get("work_package_type", "Aufgabe")).casefold()
    wp_type = next((item for item in types if str(item.get("name", "")).casefold() == preferred), None)
    if wp_type is None and types:
        wp_type = types[0]
    if wp_type is None:
        raise RuntimeError("Das OpenProject-Projekt stellt keinen Arbeitspakettyp bereit.")
    type_id = _id_from_href(wp_type)
    existing = client.existing_markers(project_id)
    findings = selected_findings(run_dir, config)
    parents: dict[str, int] = {}
    created = skipped = 0
    for finding in findings:
        marker = f"LKT-{finding['id'][:12]}"
        if marker in existing:
            skipped += 1
            continue
        file = finding["file"]
        if file not in parents:
            parent_key = hashlib.sha256(
                f"{manifest['run_id']}\0{file}".encode("utf-8")
            ).hexdigest()[:12]
            parent_marker = f"LKTSZ-{parent_key}"
            if parent_marker in existing:
                parents[file] = existing[parent_marker]
            else:
                parent = client.create_work_package(
                    project_id, type_id,
                    f"[{parent_marker}] {Path(file).stem} – Überarbeitung {manifest['next_revision']}",
                    f"Befunde aus Lektoratslauf `{manifest['run_id']}` für `{file}`.", version_id=version_id,
                )
                parents[file] = _id_from_href(parent)
                existing[parent_marker] = parents[file]
        location = f":{finding['line']}" if finding.get("line") else ""
        subject = f"[{marker}] [{Path(file).stem}{location}] {finding['category']} prüfen"
        created_work_package = client.create_work_package(
            project_id, type_id, subject, _description(finding, manifest),
            version_id=version_id, parent_id=parents[file],
        )
        existing[marker] = _id_from_href(created_work_package)
        created += 1
    result = {"project": project_name, "version": version_name, "created": created, "skipped": skipped}
    (run_dir / "openproject-sync.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
