"""Launch the beat-edl desktop window."""

from __future__ import annotations

import os

import webview

from .api import Api

_WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web")


def main() -> None:
    api = Api()
    index = os.path.join(_WEB_DIR, "index.html")
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
