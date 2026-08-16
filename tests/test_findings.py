import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.findings import collect_findings, write_findings


class FindingsTests(unittest.TestCase):
    def make_run(self, root: Path) -> Path:
        run = root / "lektorat" / "ueberarbeitungen" / "4" / "lauf"
        scene = run / "szene"
        scene.mkdir(parents=True)
        (run / "manifest.json").write_text(json.dumps({
            "project": "Homestories", "revision": "4", "next_revision": "5",
            "run_id": "lauf", "files": [{
                "path": "03_Content/101.md", "sha256": "abc", "bytes": 20,
            }],
        }), encoding="utf-8")
        return run

    def test_only_actionable_specialized_findings_are_exported(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run = self.make_run(Path(temp))
            scene = run / "szene"
            (scene / "101-hlx-lektorat.md").write_text(
                "- Zeile 2 — L — konkrete Handlung\n  - Textstelle: `Er ging.`\n"
                "- Zeile 4 — X — bereits gezeigt\n  - Textstelle: `Er war traurig.`\n",
                encoding="utf-8",
            )
            (scene / "101-sagte-lektorat.md").write_text(
                "- Zeile 8 — BEHALTEN — sonst unklar\n  - Textstelle: `sagte er`\n"
                "- Zeile 9 — STREICHEN — Sprecher klar\n  - Textstelle: `sagte sie`\n",
                encoding="utf-8",
            )
            findings = collect_findings(run)
            self.assertEqual([(item.check, item.line) for item in findings], [("hlx", 4), ("sagte", 9)])
            output = write_findings(run, findings)
            self.assertEqual(len(output.read_text(encoding="utf-8").splitlines()), 2)

    def test_korrektorat_and_scene_findings_are_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run = self.make_run(Path(temp))
            scene = run / "szene"
            (scene / "101-korrektorat.md").write_text(
                "- Zeile 3, Spalte 5 — Zeichensetzung — Komma fehlt\n"
                "  - Textstelle: `Wenn er kam ging sie.`\n  - Vorschläge: `kam, ging`\n",
                encoding="utf-8",
            )
            (scene / "101_lektorat.md").write_text(
                "## Kurzdiagnose\nText\n## Perspektivlektorat\n"
                "### Befund: Sprung\n- Fundstelle: 101.md, Zeile 7\n"
                "- Diagnose: Perspektive springt.\n- Relevanz: hoch\n"
                "- Begründung: Irritation\n- Empfehlung: Perspektive klären.\n- Querverweise: keine\n",
                encoding="utf-8",
            )
            findings = collect_findings(run)
            self.assertEqual(len(findings), 2)
            self.assertEqual({item.line for item in findings}, {3, 7})
            self.assertEqual({item.relevance for item in findings}, {"mittel", "hoch"})


if __name__ == "__main__":
    unittest.main()
