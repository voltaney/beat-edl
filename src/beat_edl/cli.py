"""Headless command-line interface: audio file in, EDL out.

Useful for batch processing and for testing the pipeline without the GUI.

    python -m beat_edl.cli song.wav -o song.edl --fps 24 --beats-per-bar 4
"""

from __future__ import annotations

import argparse
import sys

from .core import RenderOptions, analyze, build_markers, render_edl
from .detection import DetectOptions, available_backends


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="beat-edl", description=__doc__)
    parser.add_argument("audio", help="input audio file")
    parser.add_argument("-o", "--output", help="output .edl path (default: <audio>.edl)")
    parser.add_argument("--backend", choices=available_backends() or None, default=None,
                        help="detection backend (default: best available)")
    parser.add_argument("--fps", type=float, default=24.0)
    parser.add_argument("--beats-per-bar", type=int, default=4)
    parser.add_argument("--tempo", type=float, default=0.0, help="BPM hint (0=auto)")
    parser.add_argument("--every", type=int, default=1, help="emit every Nth beat")
    parser.add_argument("--downbeats-only", action="store_true")
    parser.add_argument("--no-mark-downbeats", action="store_true",
                        help="do not colour downbeats differently")
    parser.add_argument("--color", default="Blue")
    parser.add_argument("--downbeat-color", default="Red")
    parser.add_argument("--timeline-start", default="01:00:00:00")
    parser.add_argument("--title", default="Beat Markers")
    args = parser.parse_args(argv)

    detect = DetectOptions(
        beats_per_bar=args.beats_per_bar,
        tempo_hint=args.tempo,
        beat_interval=args.every,
        downbeats_only=args.downbeats_only,
    )
    render = RenderOptions(
        fps=args.fps,
        color=args.color,
        downbeat_color=args.downbeat_color,
        mark_downbeats=not args.no_mark_downbeats,
        title=args.title,
        timeline_start=args.timeline_start,
    )

    result = analyze(args.audio, detect, args.backend)
    markers = build_markers(result, render, detect)
    edl = render_edl(markers, render)

    out = args.output or (args.audio.rsplit(".", 1)[0] + ".edl")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(edl)

    print(
        f"{result.backend}: {result.tempo:.1f} BPM, "
        f"{len(result.beats)} beats, {len(result.downbeats)} downbeats "
        f"-> {len(markers)} markers written to {out}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
