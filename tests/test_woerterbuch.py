import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from manuskript.woerterbuch import add_word, load_words, replace_word, Occurrence


class WoerterbuchTests(unittest.TestCase):
    def test_dictionary_is_case_insensitive_and_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "projekt.txt"
            add_word(path, "Noostream")
            add_word(path, "noostream")
            add_word(path, "Isi")
            self.assertEqual(load_words(path), {"noostream", "isi"})
            self.assertEqual(path.read_text(encoding="utf-8"), "Isi\nNoostream\n")

    def test_confirmed_replacement_changes_complete_words_and_creates_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            source = project / "03_Content" / "101.md"
            source.parent.mkdir()
            source.write_text("Steffan sah Steffanie und Steffan.\n", encoding="utf-8")
            import hashlib
            digests = {source: hashlib.sha256(source.read_bytes()).hexdigest()}
            items = [Occurrence(source, 1, 1, "Steffan", "", ())]
            count, log = replace_word(
                project, items, "Steffan", "Stefan", digests,
                now=datetime(2026, 8, 21, 12, 0, 0),
            )
            self.assertEqual(count, 2)
            self.assertEqual(source.read_text(encoding="utf-8"), "Stefan sah Steffanie und Stefan.\n")
            backup = project / "lektorat/woerterbuch/sicherungen/20260821-120000/03_Content/101.md"
            self.assertTrue(backup.is_file())
            self.assertTrue(log.is_file())

