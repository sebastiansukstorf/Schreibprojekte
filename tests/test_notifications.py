import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from manuskript.notifications import NtfyNotifier, act_number


class NotificationTests(unittest.TestCase):
    def test_act_is_derived_from_scene_number(self) -> None:
        self.assertEqual(act_number(Path("101.md")), 1)
        self.assertEqual(act_number(Path("299-kapitel.md")), 2)
        self.assertIsNone(act_number(Path("notiz.md")))

    def test_missing_token_disables_notifications(self) -> None:
        config = {"notifications": {"ntfy": {
            "enabled": True, "base_url": "https://ntfy.example", "topic": "test",
        }}}
        messages = []
        with patch.dict(os.environ, {}, clear=True):
            notifier = NtfyNotifier.from_config(config, progress=messages.append)
        self.assertIsNone(notifier)
        self.assertIn("NTFY_TOKEN", messages[0])

    def test_send_uses_bearer_token_and_never_raises_on_network_error(self) -> None:
        messages = []
        notifier = NtfyNotifier("https://ntfy.example", "schreibprojekte", "secret", messages.append)
        with patch("urllib.request.urlopen", side_effect=OSError("offline")):
            self.assertFalse(notifier.send("Titel", "Text"))
        self.assertIn("offline", messages[0])

    def test_send_posts_json(self) -> None:
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        notifier = NtfyNotifier("https://ntfy.example", "schreibprojekte", "secret")
        with patch("urllib.request.urlopen", return_value=response) as urlopen:
            self.assertTrue(notifier.send("Titel", "Text"))
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertIn(b'"topic": "schreibprojekte"', request.data)


if __name__ == "__main__":
    unittest.main()
