"""Beat-detection backend interface shared by all detectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class BeatResult:
    """The outcome of analysing an audio file.

    ``beats`` and ``downbeats`` are times in seconds from the start of the file.
    ``downbeats`` is a subset of ``beats`` (bar starts). ``tempo`` is in BPM.
    """

    beats: list[float]
    downbeats: list[float] = field(default_factory=list)
    tempo: float = 0.0
    beats_per_bar: int = 4
    backend: str = ""


@dataclass
class DetectOptions:
    """User-tunable analysis parameters."""

    beats_per_bar: int = 4
    # Override the detected tempo (BPM). 0 means auto-detect.
    tempo_hint: float = 0.0
    # Only emit every Nth beat (1 = every beat). Useful for sparser markers.
    beat_interval: int = 1
    # Restrict markers to downbeats only.
    downbeats_only: bool = False


class BeatDetector(ABC):
    """A pluggable beat/downbeat detector."""

    name: str = "base"

    @abstractmethod
    def detect(self, audio_path: str, options: DetectOptions) -> BeatResult:
        """Analyse ``audio_path`` and return detected beats."""

    @staticmethod
    def is_available() -> bool:
        """Whether this backend's dependencies are importable."""
        return False
