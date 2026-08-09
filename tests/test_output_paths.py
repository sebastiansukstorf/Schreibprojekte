import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Skripte.manuskript_cli import resolve_output_target


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


if __name__ == "__main__":
    unittest.main()
