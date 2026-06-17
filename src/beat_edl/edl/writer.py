"""Write CMX3600 EDL files containing timeline markers for DaVinci Resolve.

Resolve round-trips timeline markers through EDL events using comment lines of
the form::

    001  001      V     C        01:00:01:00 01:00:01:01 01:00:01:00 01:00:01:01
     |C:ResolveColorBlue |M:Beat 1 |D:1

where ``|C:`` is the marker colour, ``|M:`` is the marker note/name and ``|D:``
is the marker duration in frames. The record-in timecode is where the marker
lands on the timeline. We emit one zero/one-frame event per beat.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from ..timecode import seconds_to_frames, frames_to_timecode

# Valid Resolve marker colours (the suffix after "ResolveColor").
RESOLVE_COLORS = (
    "Blue",
    "Cyan",
    "Green",
    "Yellow",
    "Red",
    "Pink",
    "Purple",
    "Fuchsia",
    "Rose",
    "Lavender",
    "Sky",
    "Mint",
    "Lemon",
    "Sand",
    "Cocoa",
    "Cream",
)


@dataclass(frozen=True)
class Marker:
    """A single marker positioned at ``time`` seconds into the audio."""

    time: float
    name: str = ""
    color: str = "Blue"
    duration_frames: int = 1

    def resolve_color(self) -> str:
        color = self.color
        if color.startswith("ResolveColor"):
            return color
        if color not in RESOLVE_COLORS:
            raise ValueError(
                f"unknown Resolve colour {color!r}; expected one of {RESOLVE_COLORS}"
            )
        return f"ResolveColor{color}"


def write_edl(
    markers: Sequence[Marker],
    fps: float,
    *,
    title: str = "Beat Markers",
    timeline_start: str = "01:00:00:00",
) -> str:
    """Render a sequence of markers as a CMX3600 EDL string.

    ``timeline_start`` is the timeline start timecode; marker record times are
    offset by it so they line up with a Resolve timeline that begins there.
    """
    start_frames = _timecode_to_frames(timeline_start, fps)

    lines = [f"TITLE: {title}", "FCM: NON-DROP FRAME", ""]
    for index, marker in enumerate(markers, start=1):
        abs_frames = start_frames + seconds_to_frames(marker.time, fps)
        rec_in = frames_to_timecode(abs_frames, fps)
        rec_out = frames_to_timecode(abs_frames + max(1, marker.duration_frames), fps)
        event = f"{index:03d}".rjust(3)
        # Source in/out mirror record in/out; the actual values are irrelevant
        # for a marker but the EDL grammar requires four timecodes.
        lines.append(
            f"{event}  001      V     C        "
            f"{rec_in} {rec_out} {rec_in} {rec_out}"
        )
        name = marker.name or f"Beat {index}"
        lines.append(
            f" |C:{marker.resolve_color()} |M:{name} |D:{marker.duration_frames}"
        )
    return "\n".join(lines) + "\n"


def markers_from_beats(
    beat_times: Iterable[float],
    *,
    color: str = "Blue",
    downbeat_color: str = "Red",
    downbeats: Sequence[float] | None = None,
    name_prefix: str = "Beat",
) -> list[Marker]:
    """Build markers from beat times, optionally colouring downbeats differently.

    ``downbeats`` is a set of times (seconds) that should use ``downbeat_color``.
    Matching is done on rounded milliseconds so float jitter does not matter.
    """
    downbeat_keys = {round(t, 3) for t in (downbeats or [])}
    markers: list[Marker] = []
    for i, t in enumerate(beat_times, start=1):
        is_down = round(t, 3) in downbeat_keys
        markers.append(
            Marker(
                time=t,
                name=f"{name_prefix} {i}",
                color=downbeat_color if is_down else color,
            )
        )
    return markers


def _timecode_to_frames(tc: str, fps: float) -> int:
    parts = tc.split(":")
    if len(parts) != 4:
        raise ValueError(f"invalid timecode {tc!r}; expected HH:MM:SS:FF")
    h, m, s, f = (int(p) for p in parts)
    rate = int(round(fps))
    return ((h * 60 + m) * 60 + s) * rate + f
