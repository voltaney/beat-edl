"""High-level pipeline tying detection and EDL output together.

This module is GUI-agnostic so it can be driven from the pywebview API bridge,
a CLI, or tests.
"""

from __future__ import annotations

from dataclasses import dataclass

from .detection import DetectOptions, get_backend, BeatResult
from .edl import Marker, markers_from_beats, write_edl


@dataclass
class RenderOptions:
    fps: float = 24.0
    color: str = "Blue"
    downbeat_color: str = "Red"
    # Colour downbeats differently from regular beats.
    mark_downbeats: bool = True
    title: str = "Beat Markers"
    timeline_start: str = "01:00:00:00"


def analyze(audio_path: str, options: DetectOptions, backend: str | None = None) -> BeatResult:
    """Run beat detection on an audio file."""
    return get_backend(backend).detect(audio_path, options)


def build_markers(result: BeatResult, render: RenderOptions, detect: DetectOptions) -> list[Marker]:
    """Turn a detection result into the list of markers to be written."""
    if detect.downbeats_only:
        beats = result.downbeats or result.beats
    else:
        beats = result.beats[:: max(1, detect.beat_interval)]

    downbeats = result.downbeats if render.mark_downbeats else []
    return markers_from_beats(
        beats,
        color=render.color,
        downbeat_color=render.downbeat_color,
        downbeats=downbeats,
    )


def render_edl(markers: list[Marker], render: RenderOptions) -> str:
    return write_edl(
        markers,
        fps=render.fps,
        title=render.title,
        timeline_start=render.timeline_start,
    )
