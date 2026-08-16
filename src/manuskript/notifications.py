"""Fehlertolerante Statusmeldungen fuer lange Lektoratslaeufe."""

from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class NtfyNotifier:
    base_url: str
    topic: str
    token: str
    progress: Callable[[str], None] = print

    @classmethod
    def from_config(cls, config: dict, *, progress: Callable[[str], None] = print) -> NtfyNotifier | None:
        settings = config.get("notifications", {}).get("ntfy", {})
        if not settings or not settings.get("enabled", False):
            return None
        base_url = str(settings.get("base_url", "")).rstrip("/")
        topic = str(settings.get("topic", "")).strip("/")
        token_env = str(settings.get("token_env", "NTFY_TOKEN"))
        token = os.environ.get(token_env, "")
        if not base_url or not topic:
            progress("⚠️ ntfy: base_url oder topic fehlt; Push-Mitteilungen deaktiviert.")
            return None
        if not token:
            progress(f"⚠️ ntfy: Umgebungsvariable {token_env} fehlt; Push-Mitteilungen deaktiviert.")
            return None
        return cls(base_url, topic, token, progress)

    def send(self, title: str, message: str, *, priority: int = 3, tags: str = "books") -> bool:
        endpoint = f"{self.base_url}/{urllib.parse.quote(self.topic, safe='')}"
        request = urllib.request.Request(
            endpoint,
            data=message.encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "text/plain; charset=utf-8",
                "Title": title,
                "Priority": str(priority),
                "Tags": tags,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                response.read()
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as error:
            self.progress(f"⚠️ ntfy-Mitteilung fehlgeschlagen: {error}")
            return False
        return True


def scene_number(path: Path) -> int | None:
    prefix = path.stem.split("-", 1)[0].split("_", 1)[0]
    return int(prefix) if prefix.isdigit() else None


def act_number(path: Path) -> int | None:
    number = scene_number(path)
    return number // 100 if number is not None and number >= 100 else None
