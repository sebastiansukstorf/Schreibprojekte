import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.cli import resolve_output_target
from manuskript.sagte_lektorat import (
    default_report_path,
    extract_sagte_batches,
    extract_sagte_context,
)


class ResolveOutputTargetTests(unittest.TestCase):
    def test_default_output_is_in_source_project(self) -> None:
        repo_root = Path("/tmp/repo")
        source_dir = repo_root / "Testprojekt"

        output = resolve_output_target(None, source_dir=source_dir, repo_root=repo_root)

        self.assertEqual(output, str(source_dir / "docx"))

    def test_relative_output_is_resolved_from_source_project(self) -> None:
        repo_root = Path("/tmp/repo")
        source_dir = repo_root / "Testprojekt"

        output = resolve_output_target("exports", source_dir=source_dir, repo_root=repo_root)

        self.assertEqual(output, str(source_dir / "exports"))

    def test_lektorat_report_is_outside_content_folder(self) -> None:
        source = Path("/tmp/MeinProjekt/03_Content/100.md")

        output = default_report_path(source)

        self.assertEqual(
            output, Path("/tmp/MeinProjekt/lektorat/szene/100-sagte-lektorat.md").resolve()
        )

    def test_sagte_context_is_prefiltered_and_numbered(self) -> None:
        text = "Erste Zeile\n»Hallo«, sagte er.\nDritte Zeile\nVierte Zeile\nFünfte Zeile\nSechste Zeile"

        excerpt, hits = extract_sagte_context(text, radius=1)

        self.assertEqual(hits, [2])
        self.assertIn("1: Erste Zeile", excerpt)
        self.assertIn("2: »Hallo«, sagte er.", excerpt)
        self.assertIn("3: Dritte Zeile", excerpt)
        self.assertNotIn("Sechste Zeile", excerpt)

    def test_sagte_batches_include_each_hit_once(self) -> None:
        text = "\n".join(["»A«, sagte er.", "Pause", "»B«, sagte sie.", "Ende"])

        batches, hits = extract_sagte_batches(text, radius=0, batch_size=8)

        self.assertEqual(hits, [1, 3])
        self.assertEqual(len(batches), 1)
        self.assertIn(">>> ZIELZEILE 1", batches[0])
        self.assertIn(">>> ZIELZEILE 3", batches[0])
        self.assertEqual(batches[0].count(">>> ZIELZEILE"), 2)


if __name__ == "__main__":
    unittest.main()
