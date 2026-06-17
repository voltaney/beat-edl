"""Launch the beat-edl desktop window."""

from __future__ import annotations

import os
import sys

import webview

from .api import Api


def _web_dir() -> str:
    """Locate the bundled web UI across editable, installed and frozen runs.

    - PyInstaller: data is unpacked under ``sys._MEIPASS``.
    - Normal install / editable: the ``web`` folder ships inside the package.
    """
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        return os.path.join(base, "beat_edl", "web")
    return os.path.join(os.path.dirname(__file__), "web")


def main() -> None:
    api = Api()
    index = os.path.join(_web_dir(), "index.html")
    webview.create_window(
        "beat-edl",
        url=index,
        js_api=api,
        width=920,
        height=760,
        min_size=(720, 560),
    )
    webview.start()


if __name__ == "__main__":
    main()
