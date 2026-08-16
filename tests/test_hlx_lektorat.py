import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.hlx_lektorat import (
    default_report_path,
    extract_hlx_batches,
    parse_hlx_answer,
    target_line_numbers,
)


class HlxLektoratTests(unittest.TestCase):
    def test_headings_and_blank_lines_are_not_targets(self) -> None:
        text = "# Kapitel\n\nEr trat ein.\n»Hallo.«"
        self.assertEqual(target_line_numbers(text), [3, 4])

    def test_batches_mark_targets_and_keep_context(self) -> None:
        text = "# Kapitel\n\nEr trat ein.\nSie sah auf.\n»Hallo.«"
        batches, targets = extract_hlx_batches(text, context_lines=1, batch_size=2)
        self.assertEqual(targets, [3, 4, 5])
        self.assertIn(">>> ZIELZEILE 3: Er trat ein.", batches[0])
        self.assertIn("    Kontext 2:", batches[0])

    def test_answer_is_validated_and_enriched(self) -> None:
        source = ["Er trat ein.", "Sie war wuetend."]
        answer = "- Zeile 1 — L — konkrete Handlung\n- Zeile 2 — X — bereits sichtbar"
        rendered = parse_hlx_answer(answer, {1, 2}, source)
        self.assertIn("Zeile 2 — X", rendered)
        self.assertIn("Textstelle: `Sie war wuetend.`", rendered)

    def test_report_is_written_beside_content_folder(self) -> None:
        source = Path("/tmp/Roman/03_Content/101.md")
        self.assertEqual(
            default_report_path(source),
            Path("/tmp/Roman/lektorat/szene/101-hlx-lektorat.md").resolve(),
        )


if __name__ == "__main__":
    unittest.main()
