import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.revision import create_revision_run, finish_revision_run, load_revision_run, resolve_run


class RevisionTests(unittest.TestCase):
    def test_run_manifest_binds_exact_source_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            content = project / "03_Content"
            content.mkdir()
            source = content / "101.md"
            source.write_text("Erster Stand\n", encoding="utf-8")
            run = create_revision_run(
                project, revision="4", next_revision="5",
                now=datetime.fromisoformat("2026-08-16T12:00:00+02:00"),
            )
            manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["revision"], "4")
            self.assertEqual(manifest["next_revision"], "5")
            self.assertEqual(manifest["files"][0]["path"], "03_Content/101.md")
            self.assertEqual(
                (run.snapshot_project / "03_Content" / "101.md").read_text(encoding="utf-8"),
                "Erster Stand\n",
            )
            finished = finish_revision_run(run, exclude=(), failed=0)
            self.assertTrue(finished["source_unchanged"])
            self.assertEqual(finished["status"], "complete")
            self.assertEqual(resolve_run(project, "4"), run.root)

    def test_changed_source_marks_run_for_attention(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            content = project / "03_Content"
            content.mkdir()
            source = content / "101.md"
            source.write_text("Erster Stand\n", encoding="utf-8")
            run = create_revision_run(project, revision="4")
            source.write_text("Verändert\n", encoding="utf-8")
            finished = finish_revision_run(run, exclude=(), failed=0)
            self.assertFalse(finished["source_unchanged"])
            self.assertEqual(finished["status"], "attention")

    def test_incomplete_run_reuses_its_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            content = project / "03_Content"
            content.mkdir()
            (content / "101.md").write_text("Stand vier\n", encoding="utf-8")
            run = create_revision_run(project, revision="4", next_revision="5")
            finish_revision_run(run, exclude=(), failed=1)
            (content / "101.md").write_text("Schon weiterbearbeitet\n", encoding="utf-8")

            resumed = load_revision_run(project, "4")

            self.assertEqual(resumed.run_id, run.run_id)
            self.assertEqual(
                (resumed.snapshot_project / "03_Content" / "101.md").read_text(encoding="utf-8"),
                "Stand vier\n",
            )
            manifest = json.loads(resumed.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["resume_count"], 1)
            self.assertEqual(manifest["status"], "running")


if __name__ == "__main__":
    unittest.main()
