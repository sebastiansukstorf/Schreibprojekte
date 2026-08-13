import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.sagte_lektorat import (
    add_missing_quotes_to_report,
    add_quotes_to_answer,
    remove_duplicate_decisions,
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


if __name__ == "__main__":
    unittest.main()
