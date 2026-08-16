import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.nachtlauf import manuscript_files, report_is_current, run_night_checks, write_summary


class NachtlaufTests(unittest.TestCase):
    def test_all_markdown_files_below_content_are_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            content = project / "03_Content"
            (content / "kapitel").mkdir(parents=True)
            (content / "100.md").write_text("A", encoding="utf-8")
            (content / "kapitel" / "101.md").write_text("B", encoding="utf-8")
            (content / "notiz.txt").write_text("C", encoding="utf-8")
            self.assertEqual([path.name for path in manuscript_files(project)], ["100.md", "101.md"])

    def test_configured_structure_files_are_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            content = project / "03_Content"
            content.mkdir()
            for name in ("050.md", "100.md", "101.md", "200.md"):
                (content / name).write_text(name, encoding="utf-8")
            files = manuscript_files(project, exclude=("050.md", "100.md", "200.md"))
            self.assertEqual([path.name for path in files], ["101.md"])

    def test_current_report_is_skipped_unless_forced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "100.md"
            report = root / "bericht.md"
            source.write_text("Text", encoding="utf-8")
            report.write_text("Bericht", encoding="utf-8")
            os.utime(report, (source.stat().st_mtime + 5, source.stat().st_mtime + 5))
            self.assertTrue(report_is_current(source, report))

    def test_failures_do_not_abort_remaining_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            content = project / "03_Content"
            content.mkdir()
            source = content / "100.md"
            source.write_text("Text", encoding="utf-8")

            def success(path, *args, **kwargs):
                output = project / "lektorat" / "szene" / f"{path.stem}-fake.md"
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text("ok", encoding="utf-8")
                return output

            with (
                patch("manuskript.nachtlauf.run_korrektorat", side_effect=RuntimeError("offline")),
                patch("manuskript.nachtlauf.run_sagte_lektorat", side_effect=success),
                patch("manuskript.nachtlauf.run_hlx_lektorat", side_effect=success),
                patch("manuskript.nachtlauf.run_wortarten_lektorat", side_effect=success),
                patch("manuskript.nachtlauf.run_redaktion", side_effect=success),
            ):
                results = run_night_checks(project, {}, force=True, progress=lambda message: None)

            self.assertEqual(len(results), 5)
            self.assertEqual(results[0].status, "failed")
            self.assertEqual(sum(result.status == "completed" for result in results), 4)
            summary = write_summary(project, results)
            self.assertTrue(summary.is_file())
            self.assertIn("Fehlgeschlagen: 1", summary.read_text(encoding="utf-8"))

    def test_revision_reports_become_visible_only_after_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            content = project / "03_Content"
            output = project / "run" / "szene"
            content.mkdir()
            (content / "101.md").write_text("Text", encoding="utf-8")

            def success(path, *args, **kwargs):
                target = Path(kwargs["output"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fertig", encoding="utf-8")
                return target

            with (
                patch("manuskript.nachtlauf.run_korrektorat", side_effect=success),
                patch("manuskript.nachtlauf.run_sagte_lektorat", side_effect=success),
                patch("manuskript.nachtlauf.run_hlx_lektorat", side_effect=success),
                patch("manuskript.nachtlauf.run_wortarten_lektorat", side_effect=success),
                patch("manuskript.nachtlauf.run_redaktion", side_effect=success),
            ):
                results = run_night_checks(project, {}, output_root=output, progress=lambda _: None)

            self.assertEqual(sum(item.status == "completed" for item in results), 5)
            self.assertFalse(list(output.glob("*.partial")))
            self.assertEqual(len(list(output.glob("*.md"))), 5)


if __name__ == "__main__":
    unittest.main()
