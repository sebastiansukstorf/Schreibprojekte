import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.openproject import preview, selected_findings, sync
from manuskript.openproject import OpenProjectClient


class OpenProjectPreviewTests(unittest.TestCase):
    def test_basic_auth_uses_fixed_apikey_username(self) -> None:
        client = OpenProjectClient("https://example.test", "abc")
        self.assertEqual(client.authorization(), "Basic YXBpa2V5OmFiYw==")

    def make_run(self, root: Path) -> Path:
        run = root / "run"
        run.mkdir()
        (run / "manifest.json").write_text(json.dumps({
            "project": "Homestories", "revision": "4", "next_revision": "5", "run_id": "testlauf",
        }), encoding="utf-8")
        findings = [
            {"id": "a", "file": "03_Content/101.md", "line": 1, "column": None, "check": "hlx", "category": "X", "relevance": "hoch", "quote": "Text", "diagnosis": "Doppelt", "recommendation": "Prüfen", "source_sha256": "abc"},
            {"id": "b", "file": "03_Content/101.md", "line": 2, "column": None, "check": "sagte", "category": "Sprecherführung", "relevance": "mittel", "quote": "Text", "diagnosis": "Klar", "recommendation": "Streichen prüfen", "source_sha256": "abc"},
            {"id": "c", "file": "03_Content/101.md", "line": 3, "column": None, "check": "wortarten", "category": "Adverb", "relevance": "niedrig", "quote": "Text", "diagnosis": "Schwach", "recommendation": "Prüfen", "source_sha256": "abc"},
        ]
        (run / "findings.jsonl").write_text(
            "".join(json.dumps(item) + "\n" for item in findings), encoding="utf-8",
        )
        return run

    def test_relevance_and_scene_cap_are_applied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run = self.make_run(Path(temp))
            config = {"openproject": {"minimum_relevance": "mittel", "max_tasks_per_scene": 1}}
            selected = selected_findings(run, config)
            self.assertEqual([item["id"] for item in selected], ["a"])
            rendered = preview(run, config)
            self.assertIn("Zielversion: `5`", rendered)
            self.assertIn("Aufgaben: 1", rendered)
            self.assertIn("noch keine OpenProject-Daten verändert", rendered)

    def test_sync_creates_version_parent_and_idempotent_child_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run = self.make_run(Path(temp))
            manifest_path = run / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.update({"status": "complete", "source_unchanged": True})
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            records = []

            class FakeClient:
                def __init__(self, *args, **kwargs): pass
                def project(self, identifier):
                    return {"_links": {"self": {"href": "/api/v3/projects/1"}}}
                def versions(self, project_id): return []
                def create_version(self, project_id, name):
                    return {"name": name, "_links": {"self": {"href": "/api/v3/versions/2"}}}
                def project_types(self, project_id):
                    return [{"name": "Aufgabe", "_links": {"self": {"href": "/api/v3/types/3"}}}]
                def existing_markers(self, project_id): return {}
                def create_work_package(self, project_id, type_id, subject, description, **kwargs):
                    records.append((subject, kwargs))
                    return {"_links": {"self": {"href": f"/api/v3/work_packages/{10 + len(records)}"}}}

            config = {
                "openproject": {
                    "base_url": "https://projects.example.test", "project_identifier": "homestories",
                    "minimum_relevance": "mittel", "max_tasks_per_scene": 1,
                }
            }
            with patch("manuskript.openproject.OpenProjectClient", FakeClient):
                result = sync(run, config, token="secret")
            self.assertEqual(result["created"], 1)
            self.assertEqual(len(records), 2)
            self.assertTrue(records[0][0].startswith("[LKTSZ-"))
            self.assertTrue(records[1][0].startswith("[LKT-"))
            self.assertEqual(records[1][1]["parent_id"], 11)


if __name__ == "__main__":
    unittest.main()
