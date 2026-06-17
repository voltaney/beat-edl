"""librosa-based beat detector with heuristic downbeat estimation.

librosa reliably tracks beats and tempo but does not itself report which beats
are bar starts. We recover downbeats by assuming a fixed meter (``beats_per_bar``)
and choosing the phase whose beats carry the most onset energy summed over the
track -- bar starts tend to be the most strongly accented beats. This keeps the
default backend dependency-light (no PyTorch, no madmom) while still producing
usable downbeat markers.
"""

from __future__ import annotations

from .base import BeatDetector, BeatResult, DetectOptions


class LibrosaBackend(BeatDetector):
    name = "librosa"

    @staticmethod
    def is_available() -> bool:
        try:
            import librosa  # noqa: F401
        except Exception:
            return False
        return True

    def detect(self, audio_path: str, options: DetectOptions) -> BeatResult:
        import librosa
        import numpy as np

        y, sr = librosa.load(audio_path, sr=None, mono=True)

        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        bpm_hint = options.tempo_hint if options.tempo_hint > 0 else None
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=onset_env,
            sr=sr,
            start_bpm=bpm_hint if bpm_hint else 120.0,
            bpm=bpm_hint,
        )
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        beat_times = [float(t) for t in beat_times]

        downbeats = self._estimate_downbeats(
            beat_frames, onset_env, beat_times, options.beats_per_bar
        )

        tempo_val = float(np.atleast_1d(tempo)[0])
        return BeatResult(
            beats=beat_times,
            downbeats=downbeats,
            tempo=tempo_val,
            beats_per_bar=options.beats_per_bar,
            backend=self.name,
        )

    @staticmethod
    def _estimate_downbeats(beat_frames, onset_env, beat_times, beats_per_bar):
        """Pick the bar-start phase that maximises summed onset strength."""
        import numpy as np

        if beats_per_bar < 2 or len(beat_times) == 0:
            return list(beat_times)

        beat_frames = np.atleast_1d(np.asarray(beat_frames)).astype(int)
        beat_frames = np.clip(beat_frames, 0, len(onset_env) - 1)
        strengths = onset_env[beat_frames]

        best_phase, best_score = 0, -np.inf
        for phase in range(beats_per_bar):
            score = strengths[phase::beats_per_bar].sum()
            if score > best_score:
                best_score, best_phase = score, phase

        return [beat_times[i] for i in range(best_phase, len(beat_times), beats_per_bar)]
