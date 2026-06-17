"""JS <-> Python bridge exposed to the pywebview frontend.

Methods on :class:`Api` are callable from the web UI as ``pywebview.api.<name>``
and receive/return JSON-serialisable values.
"""

from __future__ import annotations

import os
from typing import Any

import webview

from .core import RenderOptions, analyze, build_markers, render_edl
from .detection import DetectOptions, available_backends
from .edl import RESOLVE_COLORS


class Api:
    def __init__(self) -> None:
        self._last_edl: str = ""

    # -- environment ---------------------------------------------------------

    def get_capabilities(self) -> dict[str, Any]:
        """Report installed backends and the colour palette to the UI."""
        return {
            "backends": available_backends(),
            "colors": list(RESOLVE_COLORS),
        }

    def open_audio_dialog(self) -> str | None:
        """Show a native open-file dialog and return the chosen path."""
        result = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=(
                "Audio Files (*.wav;*.mp3;*.flac;*.m4a;*.aac;*.ogg)",
                "All files (*.*)",
            ),
        )
        if not result:
            return None
        return result[0]

    # -- analysis ------------------------------------------------------------

    def analyze(self, audio_path: str, params: dict[str, Any]) -> dict[str, Any]:
        """Detect beats and return times plus a preview-ready summary."""
        if not audio_path or not os.path.isfile(audio_path):
            return {"ok": False, "error": f"file not found: {audio_path}"}

        detect = DetectOptions(
            beats_per_bar=int(params.get("beats_per_bar", 4)),
            tempo_hint=float(params.get("tempo_hint", 0) or 0),
            beat_interval=int(params.get("beat_interval", 1)),
            downbeats_only=bool(params.get("downbeats_only", False)),
        )
        backend = params.get("backend") or None
        try:
            result = analyze(audio_path, detect, backend)
        except Exception as exc:  # surfaced in the UI rather than crashing
            return {"ok": False, "error": str(exc)}

        return {
            "ok": True,
            "backend": result.backend,
            "tempo": round(result.tempo, 2),
            "beats": result.beats,
            "downbeats": result.downbeats,
            "beats_per_bar": result.beats_per_bar,
        }

    def export_edl(self, audio_path: str, params: dict[str, Any]) -> dict[str, Any]:
        """Re-run detection, build markers, write an EDL via a save dialog."""
        detect = DetectOptions(
            beats_per_bar=int(params.get("beats_per_bar", 4)),
            tempo_hint=float(params.get("tempo_hint", 0) or 0),
            beat_interval=int(params.get("beat_interval", 1)),
            downbeats_only=bool(params.get("downbeats_only", False)),
        )
        render = RenderOptions(
            fps=float(params.get("fps", 24.0)),
            color=params.get("color", "Blue"),
            downbeat_color=params.get("downbeat_color", "Red"),
            mark_downbeats=bool(params.get("mark_downbeats", True)),
            title=params.get("title") or "Beat Markers",
            timeline_start=params.get("timeline_start", "01:00:00:00"),
        )
        backend = params.get("backend") or None

        try:
            result = analyze(audio_path, detect, backend)
            markers = build_markers(result, render, detect)
            edl = render_edl(markers, render)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

        suggested = os.path.splitext(os.path.basename(audio_path))[0] + ".edl"
        save_path = webview.windows[0].create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=suggested,
            file_types=("EDL Files (*.edl)", "All files (*.*)"),
        )
        if not save_path:
            return {"ok": False, "error": "cancelled"}

        path = save_path if isinstance(save_path, str) else save_path[0]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(edl)
        return {"ok": True, "path": path, "marker_count": len(markers)}
