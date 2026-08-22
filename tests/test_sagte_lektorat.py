import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.sagte_lektorat import (
    add_missing_quotes_to_report,
    add_quotes_to_answer,
    decision_line_numbers,
    keep_expected_decisions,
    isolate_target,
    remove_duplicate_decisions,
    run_sagte_lektorat,
    target_quotes,
)


class SagteReportTests(unittest.TestCase):
    def test_report_contains_exact_target_text(self) -> None:
        excerpt = '    Kontext 6: Er sah ihn an.\n>>> ZIELZEILE 7: "Hallo", sagte Peter.'
        answer = "- Zeile 7 — STREICHEN — Peter ist durch die Handlung eindeutig."

        rendered = add_quotes_to_answer(answer, target_quotes(excerpt))

        self.assertIn('Textstelle: `"Hallo", sagte Peter.`', rendered)

    def test_small_model_markdown_variation_is_accepted(self) -> None:
        answer = "- **Zeile 7**: **STREICHEN** - Peter ist eindeutig."

        rendered = add_quotes_to_answer(answer, {7: '"Hallo", sagte Peter.'})

        self.assertIn("Zeile 7 — STREICHEN", rendered)
        self.assertIn('Textstelle: `"Hallo", sagte Peter.`', rendered)

    def test_existing_report_is_enriched_without_duplicate_quotes(self) -> None:
        source = 'Er sah ihn an.\n"Hallo", sagte Peter.'
        report = "- Zeile 2 — STREICHEN — Peter ist eindeutig.\n"

        enriched = add_missing_quotes_to_report(report, source)
        enriched_again = add_missing_quotes_to_report(enriched, source)

        self.assertEqual(enriched, enriched_again)
        self.assertIn('Textstelle: `"Hallo", sagte Peter.`', enriched)

    def test_duplicate_decision_and_quote_are_removed(self) -> None:
        report = (
            "- Zeile 7 — STREICHEN — erster Grund\n"
            "  - Textstelle: `erste`\n"
            "- Zeile 7 — BEHALTEN — zweiter Grund\n"
            "  - Textstelle: `zweite`\n"
        )

        cleaned = remove_duplicate_decisions(report)

        self.assertEqual(cleaned.count("Zeile 7"), 1)
        self.assertIn("`erste`", cleaned)
        self.assertNotIn("`zweite`", cleaned)

    def test_extra_decision_is_discarded_without_losing_expected_one(self) -> None:
        answer = (
            "Zeile 31 — BEHALTEN — erwartetes Urteil\n"
            "Zeile 24 — STREICHEN — wiederholtes fremdes Urteil"
        )
        self.assertEqual(decision_line_numbers(answer), [31, 24])
        cleaned = keep_expected_decisions(answer, {31})
        self.assertIn("Zeile 31", cleaned)
        self.assertNotIn("Zeile 24", cleaned)

    def test_rescue_excerpt_marks_only_missing_line_as_target(self) -> None:
        excerpt = (
            ">>> ZIELZEILE 7: A, sagte er.\n"
            ">>> ZIELZEILE 9: B, sagte sie."
        )
        rescued = isolate_target(excerpt, 9)
        self.assertIn("Kontext 7: A, sagte er.", rescued)
        self.assertIn(">>> ZIELZEILE 9: B, sagte sie.", rescued)
        self.assertEqual(rescued.count(">>> ZIELZEILE"), 1)

    def test_missing_batch_decision_is_requested_individually(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "101.md"
            source.write_text(
                "„A“, sagte er.\nPause\n„B“, sagte sie.\n",
                encoding="utf-8",
            )
            incomplete = "- Zeile 1 — BEHALTEN — Sprecher sonst unklar."
            rescue = "- Zeile 3 — STREICHEN — Sprecherin ist eindeutig."
            with patch(
                "manuskript.sagte_lektorat.ollama_generate",
                side_effect=[incomplete, incomplete, incomplete, rescue],
            ) as generate:
                report = run_sagte_lektorat(
                    source, output=Path(temp) / "report.md", context_lines=0, batch_size=4,
                )
            rendered = report.read_text(encoding="utf-8")
            self.assertEqual(generate.call_count, 4)
            self.assertIn("Zeile 1 — BEHALTEN", rendered)
            self.assertIn("Zeile 3 — STREICHEN", rendered)


if __name__ == "__main__":
    unittest.main()
