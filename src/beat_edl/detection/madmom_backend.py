"""madmom-based detector (optional, high-accuracy downbeat tracking).

madmom's RNN + DBN downbeat tracker reports beats *and* their position within
the bar, so downbeats come directly from the model rather than a heuristic.

The released madmom (0.16.x) does not import on Python 3.10+, so this backend is
optional: install a compatible build (e.g. from git master) to enable it. The
app falls back to the librosa backend when madmom is unavailable.
"""

from __future__ import annotations

from .base import BeatDetector, BeatResult, DetectOptions


class MadmomBackend(BeatDetector):
    name = "madmom"

    @staticmethod
    def is_available() -> bool:
        try:
            from madmom.features.downbeats import (  # noqa: F401
                DBNDownBeatTrackingProcessor,
                RNNDownBeatProcessor,
            )
        except Exception:
            return False
        return True

    def detect(self, audio_path: str, options: DetectOptions) -> BeatResult:
        import librosa
        from madmom.audio.signal import Signal
        from madmom.features.downbeats import (
            DBNDownBeatTrackingProcessor,
            RNNDownBeatProcessor,
        )

        beats_per_bar = options.beats_per_bar
        # Load audio with librosa (already a dependency) rather than madmom's
        # loader, which otherwise requires ffmpeg/avconv to be installed.
        y, sr = librosa.load(audio_path, sr=44100, mono=True)
        act = RNNDownBeatProcessor()(Signal(y, sample_rate=sr))
        proc = DBNDownBeatTrackingProcessor(
            beats_per_bar=[beats_per_bar], fps=100
        )
        # Returns an (N, 2) array: [time_in_seconds, beat_position_in_bar].
        tracked = proc(act)

        beats = [float(t) for t, _ in tracked]
        downbeats = [float(t) for t, pos in tracked if int(pos) == 1]
        tempo = self._estimate_tempo(beats)

        return BeatResult(
            beats=beats,
            downbeats=downbeats,
            tempo=tempo,
            beats_per_bar=beats_per_bar,
            backend=self.name,
        )

    @staticmethod
    def _estimate_tempo(beats):
        if len(beats) < 2:
            return 0.0
        intervals = [b - a for a, b in zip(beats, beats[1:]) if b > a]
        if not intervals:
            return 0.0
        intervals.sort()
        median = intervals[len(intervals) // 2]
        return 60.0 / median if median > 0 else 0.0
