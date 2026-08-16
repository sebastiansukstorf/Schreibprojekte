import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.wortarten_lektorat import (
    default_report_path,
    extract_batches,
    parse_answer,
    word_occurs_only_in_direct_speech,
)


class WortartenLektoratTests(unittest.TestCase):
    def test_batches_skip_headings_and_blank_lines(self) -> None:
        batches = extract_batches("# Kapitel\n\nEr ging sehr langsam.\nSie blieb.", batch_size=1)
        self.assertEqual(batches, ["3: Er ging sehr langsam.", "4: Sie blieb."])

    def test_valid_finding_gets_original_line(self) -> None:
        answer = (
            "- Zeile 1 — sehr — ADVERB — STREICHEN — bloßer Verstärker — "
            "Vorschlag: ersatzlos streichen"
        )
        rendered = parse_answer(answer, ["Er ging sehr langsam."])
        self.assertIn("`sehr` — ADVERB — STREICHEN", rendered[0])
        self.assertIn("Textstelle: `Er ging sehr langsam.`", rendered[2])

    def test_missing_separate_suggestion_is_tolerated(self) -> None:
        answer = "- Zeile 1 — langsam — ADVERB — ERSETZEN — stärker: Er schlurfte."
        rendered = parse_answer(answer, ["Er ging langsam."])
        self.assertIn("Vorschlag: Er schlurfte.", rendered[1])

    def test_invented_word_is_rejected(self) -> None:
        answer = (
            "- Zeile 1 — hastig — ADVERB — STREICHEN — unnoetig — Vorschlag: streichen"
        )
        with self.assertRaises(RuntimeError):
            parse_answer(answer, ["Er ging langsam."])

    def test_phrase_and_mid_sentence_noun_are_rejected(self) -> None:
        phrase = (
            "- Zeile 1 — sehr langsam — ADVERB — STREICHEN — unnoetig — Vorschlag: streichen"
        )
        noun = "- Zeile 1 — Affe — ADJEKTIV — STREICHEN — wertend — Vorschlag: streichen"
        with self.assertRaises(RuntimeError):
            parse_answer(phrase, ["Er ging sehr langsam."])
        with self.assertRaises(RuntimeError):
            parse_answer(noun, ["Er sah aus wie ein Affe."])

    def test_keine_is_accepted(self) -> None:
        self.assertEqual(parse_answer("KEINE", ["Er ging."]), [])

    def test_words_inside_direct_speech_are_protected(self) -> None:
        self.assertTrue(word_occurs_only_in_direct_speech('Er sagte: "Komm mal her."', "mal"))
        self.assertFalse(word_occurs_only_in_direct_speech('"Ja", sagte er leise.', "leise"))

    def test_default_report_path(self) -> None:
        source = Path("/tmp/Roman/03_Content/101.md")
        expected = Path(
            "/tmp/Roman/lektorat/szene/101-adjektive-adverbien-lektorat.md"
        ).resolve()
        self.assertEqual(default_report_path(source), expected)


if __name__ == "__main__":
    unittest.main()
