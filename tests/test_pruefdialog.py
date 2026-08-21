import json
import tempfile
import unittest
from pathlib import Path

from manuskript.pruefdialog import acts, discover_projects, load_project_config


class PruefdialogTests(unittest.TestCase):
    def test_projects_are_discovered_from_root_and_service_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            projects = root / "projekte"
            configs = root / "config"
            alpha = projects / "Alpha"
            beta = root / "Beta"
            (alpha / "03_Content").mkdir(parents=True)
            (beta / "03_Content").mkdir(parents=True)
            (alpha / ".manuskript.json").write_text("{}", encoding="utf-8")
            configs.mkdir()
            beta_config = root / "Beta.json"
            beta_config.write_text(json.dumps({"name": "Beta"}), encoding="utf-8")
            (configs / "beta.conf").write_text(
                f"PROJECT={beta}\nCONFIG={beta_config}\n", encoding="utf-8"
            )
            found = discover_projects(projects, configs)
            self.assertEqual([item.name for item in found], ["Alpha", "Beta"])
            self.assertEqual(load_project_config(found[1]), {"name": "Beta"})

    def test_acts_come_from_hundreds_in_file_names(self) -> None:
        files = tuple(Path(name) for name in ("050.md", "101.md", "199.md", "200.md", "305.md"))
        self.assertEqual(acts(files), (0, 1, 2, 3))

