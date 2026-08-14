import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.korrektorat import (
    default_report_path,
    language_tool_check,
    mask_markdown,
    parse_findings,
    render_report,
)


class KorrektoratTests(unittest.TestCase):
    def test_markdown_is_masked_without_changing_offsets(self) -> None:
        text = "# Kapitel\nEin `Codewort` bleibt.\n"
        masked = mask_markdown(text)
        self.assertEqual(len(masked), len(text))
        self.assertEqual(masked.count("\n"), text.count("\n"))
        self.assertNotIn("#", masked.splitlines()[0])
        self.assertIn("Kapitel", masked.splitlines()[0])
        self.assertNotIn("Codewort", masked)

    def test_http_api_uses_documented_post_parameters(self) -> None:
        class Response(BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.close()

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["data"] = request.data.decode("utf-8")
            captured["timeout"] = timeout
            return Response(b'{"matches": []}')

        with patch("manuskript.korrektorat.urlopen", fake_urlopen):
            result = language_tool_check("Ein Text.", language="de-DE")

        self.assertEqual(result, {"matches": []})
        self.assertEqual(captured["url"], "http://127.0.0.1:8081/v2/check")
        self.assertIn("language=de-DE", captured["data"])
        self.assertIn("text=Ein+Text.", captured["data"])

    def test_only_spelling_and_punctuation_are_reported(self) -> None:
        response = {
            "matches": [
                {
                    "offset": 4,
                    "message": "Möglicher Tippfehler",
                    "replacements": [{"value": "ging"}],
                    "rule": {"id": "GERMAN_SPELLER_RULE", "issueType": "misspelling", "category": {"id": "TYPOS"}},
                },
                {
                    "offset": 0,
                    "message": "Stil",
                    "replacements": [],
                    "rule": {"id": "STYLE", "issueType": "style", "category": {"id": "STYLE"}},
                },
            ]
        }
        findings = parse_findings("Er gink heim.", response)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "Rechtschreibung")
        self.assertEqual(findings[0].line, 1)
        self.assertEqual(findings[0].column, 5)

    def test_findings_created_only_by_markdown_mask_are_ignored(self) -> None:
        content = "# 1\n"
        checked = "  1\n"
        response = {
            "matches": [{
                "offset": 0,
                "length": 2,
                "message": "Doppeltes Leerzeichen",
                "replacements": [{"value": " "}],
                "rule": {"id": "WHITESPACE_RULE", "issueType": "typographical", "category": {"id": "TYPOGRAPHY"}},
            }]
        }
        self.assertEqual(parse_findings(content, response, checked_content=checked), [])

    def test_report_contains_sources_and_original_line(self) -> None:
        response = {
            "matches": [{
                "offset": 3,
                "message": "Komma prüfen",
                "replacements": [{"value": ","}],
                "rule": {"id": "COMMA_RULE", "issueType": "grammar", "category": {"id": "GRAMMAR"}},
            }]
        }
        report = render_report(Path("101.md"), parse_findings("Ja das stimmt.", response), "de-DE", "http://localhost:8081")
        self.assertIn("Amtliches Regelwerk", report)
        self.assertIn("Zeile 1, Spalte 4 — Zeichensetzung", report)
        self.assertIn("`Ja das stimmt.`", report)

    def test_languagetool_punctuation_category_is_included(self) -> None:
        response = {
            "matches": [{
                "offset": 0,
                "length": 1,
                "message": "Anführungszeichen prüfen",
                "replacements": [],
                "rule": {"id": "DE_UNPAIRED_QUOTES", "issueType": "typographical", "category": {"id": "PUNCTUATION"}},
            }]
        }
        findings = parse_findings('"Text"', response)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "Zeichensetzung")

    def test_default_report_path_is_outside_content(self) -> None:
        source = Path("/tmp/Roman/03_Content/101.md")
        expected = Path("/tmp/Roman/Korrektorat/101-rechtschreibung-zeichensetzung.md").resolve()
        self.assertEqual(default_report_path(source), expected)


if __name__ == "__main__":
    unittest.main()
