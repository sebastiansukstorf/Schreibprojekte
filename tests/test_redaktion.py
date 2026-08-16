import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.redaktion import (
    LEVEL_MODULES,
    build_prompt,
    default_report_path,
    load_manuscript,
    parse_scene_metadata,
    render_scene_yaml,
    run_redaktion,
    select_markdown_files,
    validate_answer,
)


def valid_answer(level: str) -> str:
    sections = ["## Kurzdiagnose\n\nKnappe Diagnose."]
    sections.extend(f"## {module}\n\nKeine relevanten Befunde." for module in LEVEL_MODULES[level])
    if level == "szene":
        sections.append(
            '```scene_metadata\n'
            '{"einstieg":"spät", "ziel":"Flucht", "konflikt":"Tür blockiert", '
            '"dynamik":"eskaliert", "wendung":"Hilfe erscheint", "ausgang":"Flucht gelingt", '
            '"ende":"offene Gefahr", "funktion":"Konflikt zuspitzen"}\n```'
        )
    return "\n\n".join(sections)


class RedaktionTests(unittest.TestCase):
    def test_scene_requires_one_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "101.md"
            path.write_text("Eine Szene.\n", encoding="utf-8")
            self.assertEqual(select_markdown_files(path, level="szene"), (path.resolve(),))

    def test_part_range_selects_numeric_files_and_ignores_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            content = project / "03_Content"
            content.mkdir()
            for name in ("199.md", "200.md", "205-szene.md", "300.md", "notiz.md"):
                (content / name).write_text(name, encoding="utf-8")
            report_dir = content / "lektorat"
            report_dir.mkdir()
            (report_dir / "201.md").write_text("Bericht", encoding="utf-8")

            files = select_markdown_files(project, level="teil", start=200, end=299)

            self.assertEqual([path.name for path in files], ["200.md", "205-szene.md"])

    def test_prompt_protects_style_and_contains_required_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "101.md"
            path.write_text('»Komm«, sagte er.\n', encoding="utf-8")
            manuscript = load_manuscript(path, level="szene")
            prompt = build_prompt("szene", manuscript, "Kein Kontext", style_profile="Ellipsen erlaubt.")
            self.assertIn("Sprecher müssen nicht fortlaufend mit „sagte er“", prompt)
            self.assertIn("## Dialogformalia", prompt)
            self.assertIn("Fundstelle", prompt)
            self.assertIn("Ellipsen erlaubt.", prompt)

    def test_validation_rejects_missing_module(self) -> None:
        answer = valid_answer("szene").replace("## Dialogformalia", "## Dialog")
        with self.assertRaises(RuntimeError):
            validate_answer("szene", answer)

    def test_run_writes_report_without_changing_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            content = project / "03_Content"
            content.mkdir()
            source = content / "101.md"
            original = "Er trat ein.\n"
            source.write_text(original, encoding="utf-8")
            with patch("manuskript.redaktion.ollama_generate", return_value=valid_answer("szene")):
                report = run_redaktion(source, level="szene", model="testmodell")
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertEqual(report, project / "lektorat" / "szene" / "101_lektorat.md")
            report_text = report.read_text(encoding="utf-8")
            self.assertTrue(report_text.startswith("---\nlektoratsebene: \"szene\""))
            self.assertIn('ziel: "Flucht"', report_text)
            self.assertIn("Das Manuskript wurde nicht verändert", report_text)

    def test_scene_metadata_becomes_yaml_frontmatter(self) -> None:
        metadata = parse_scene_metadata(valid_answer("szene"))
        yaml = render_scene_yaml(metadata)
        self.assertTrue(yaml.startswith("---\n"))
        self.assertTrue(yaml.endswith("\n---"))
        self.assertIn('konflikt: "Tür blockiert"', yaml)

    def test_default_paths_for_all_levels(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            content = project / "03_Content"
            content.mkdir()
            source = content / "201.md"
            source.write_text("Text", encoding="utf-8")
            scene = load_manuscript(source, level="szene")
            part = load_manuscript(project, level="teil")
            self.assertEqual(
                default_report_path(scene, level="szene"),
                project / "lektorat" / "szene" / "201_lektorat.md",
            )
            self.assertEqual(
                default_report_path(part, level="teil", label="teil_2"),
                project / "lektorat" / "teile" / "teil_2_lektorat.md",
            )
            self.assertEqual(
                default_report_path(part, level="gesamt"),
                project / "lektorat" / "gesamt" / "roman_lektorat.md",
            )


if __name__ == "__main__":
    unittest.main()
