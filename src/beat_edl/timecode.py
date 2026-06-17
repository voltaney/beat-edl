"""Timecode helpers for converting beat times (seconds) to SMPTE timecode.

DaVinci Resolve timelines default to a start timecode of 01:00:00:00 and use
frame-quantized markers, so beat positions in seconds must be rounded to the
nearest frame at the project frame rate before being written to an EDL.
"""

from __future__ import annotations

from dataclasses import dataclass

# Frame rates that are nominally fractional (NTSC family). For these, true
# drop-frame timecode could be used, but Resolve happily imports non-drop
# timecode computed from the rounded integer rate, which keeps things simple
# and unambiguous for marker placement.
COMMON_FRAME_RATES = (23.976, 24.0, 25.0, 29.97, 30.0, 50.0, 59.94, 60.0)


def _nominal_rate(fps: float) -> int:
    """Return the integer number of frames per second label used in timecode.

    23.976 -> 24, 29.97 -> 30, 59.94 -> 60. For integer rates this is just the
    rounded value.
    """
    return int(round(fps))


@dataclass(frozen=True)
class Timecode:
    hours: int
    minutes: int
    seconds: int
    frames: int

    def __str__(self) -> str:
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}:{self.frames:02d}"


def seconds_to_frames(t: float, fps: float) -> int:
    """Round a time in seconds to the nearest whole frame index."""
    return int(round(t * fps))


def frames_to_timecode(total_frames: int, fps: float) -> Timecode:
    """Convert an absolute frame count to non-drop SMPTE timecode."""
    rate = _nominal_rate(fps)
    if rate <= 0:
        raise ValueError(f"invalid frame rate: {fps}")
    frames = total_frames % rate
    total_seconds = total_frames // rate
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = (total_minutes // 60) % 24
    return Timecode(hours, minutes, seconds, frames)


def seconds_to_timecode(t: float, fps: float, *, offset_frames: int = 0) -> Timecode:
    """Convert a time in seconds to timecode, with an optional frame offset.

    ``offset_frames`` is typically the timeline start (e.g. 1 hour worth of
    frames for Resolve's default 01:00:00:00 start).
    """
    return frames_to_timecode(seconds_to_frames(t, fps) + offset_frames, fps)
