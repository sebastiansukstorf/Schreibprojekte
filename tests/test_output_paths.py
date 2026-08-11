import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.cli import resolve_output_target
from manuskript.sagte_lektorat import default_report_path


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

        self.assertEqual(output, Path("/tmp/MeinProjekt/Lektorat/100-sagte-lektorat.md").resolve())


if __name__ == "__main__":
    unittest.main()
