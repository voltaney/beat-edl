# CHANGELOG


## v0.1.0 (2026-06-17)

### Build System

- Add PR test CI and make the Windows build manual-only
  ([`9760731`](https://github.com/voltaney/beat-edl/commit/9760731ed4e4479bdfe6de6a688774e81a12bc21))

- ci.yml: run pytest on Ubuntu for pull requests and pushes to main. - build-windows.yml: drop the
  push/tag/claude triggers (release builds are handled by release.yml); keep workflow_dispatch for
  ad-hoc builds.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

- Add PyInstaller (onedir) packaging and Windows CI
  ([`db66558`](https://github.com/voltaney/beat-edl/commit/db665587a662fdd0ace61a18a3fb9df4b9036ea3))

- packaging/beat-edl.spec: onedir build bundling the web UI and librosa data/submodules. A dedicated
  entry.py avoids relative-import failures when PyInstaller runs the entry as a top-level script. -
  packaging/build.ps1: local Windows build via uv. - .github/workflows/build-windows.yml: build +
  test on a Windows runner and upload the app as an artifact (PyInstaller cannot cross-compile). -
  README: document uv setup, optional madmom, and the exe build.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

- Automate releases with python-semantic-release
  ([`ba04af3`](https://github.com/voltaney/beat-edl/commit/ba04af346024edcaa30f5388d5db689df5313e5e))

On every push to main, PSR derives the next version from Conventional Commits, bumps the version
  (pyproject + __init__), updates the changelog, tags vX.Y.Z and creates a GitHub Release; a
  dependent Windows job builds the exe and attaches it. Document the flow in CLAUDE.md.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

- Manage project with uv and ship web UI inside the package
  ([`51d3d99`](https://github.com/voltaney/beat-edl/commit/51d3d997c2440d5704dfb615d7a439c54e78ac68))

- Convert dependency management to uv: regenerate uv.lock, move dev tools (pytest, pyinstaller) into
  [dependency-groups], require Python >=3.10. madmom stays out of the lock by design (git +
  --no-build-isolation). - Move web/ into src/beat_edl/web so installed and frozen builds find it;
  resolve the UI path across editable/installed/PyInstaller in __main__.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

### Documentation

- Add CLAUDE.md with conventions and commands
  ([`7d1bae2`](https://github.com/voltaney/beat-edl/commit/7d1bae24f2f5f93a7acb3cd47a8dc879810613b2))

Record the uv-based workflow, optional madmom install, PyInstaller build, architecture notes, and
  the commit convention (logical-unit commits).

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

- Add specification in docs/spec.md
  ([`b5a0208`](https://github.com/voltaney/beat-edl/commit/b5a0208ad9f7c121ff9b275563000e6e6f87f4be))

Document scope, functional requirements, the librosa/madmom detection backends, the CMX3600 EDL
  marker format, timecode conversion, architecture, distribution, and known limitations.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

- Allow auto-creating PRs to main in CLAUDE.md
  ([`cbcf61f`](https://github.com/voltaney/beat-edl/commit/cbcf61f8e153f20fd4425daf0ea69409577e2ecf))

Per user direction, feature/fix branches may open a PR to main automatically once work is complete;
  a per-PR request is no longer required.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

- Define branching policy (GitHub Flow) in CLAUDE.md
  ([`e028d65`](https://github.com/voltaney/beat-edl/commit/e028d6596f6f6ba1f33cf2afb4256f55837e6978))

Default branch is main; short-lived branches use commit-type prefixes (feat/, fix/, docs/, build/,
  ...). Changes land on main via PR by default; releases are SemVer tags that trigger the Windows
  build.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

### Features

- Beat-synced EDL marker generator (Python + pywebview)
  ([`30080c5`](https://github.com/voltaney/beat-edl/commit/30080c516101290ab4800fac68e79b338ae885c8))

Scaffold a desktop app that analyses an audio file's beats and writes a DaVinci Resolve-compatible
  CMX3600 EDL marker file.

- Pluggable detection backends: librosa (default, light, heuristic downbeats) and madmom (optional,
  true RNN+DBN downbeat/meter tracking). madmom loads audio via librosa so ffmpeg is not required. -
  CMX3600 EDL writer using Resolve's |C:/|M:/|D: marker notation, with frame-quantized SMPTE
  timecode and timeline-start offset. - pywebview GUI shell (OS webview) with waveform + beat
  overlay; plus a headless CLI and a GUI-agnostic core pipeline. - Unit tests for timecode and EDL
  output.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC

### Refactoring

- Remove waveform display from the GUI
  ([`fcfb3b4`](https://github.com/voltaney/beat-edl/commit/fcfb3b4f92cbc1f027d77eeb924e97f7d0f1d9c1))

Drop the wavesurfer.js waveform view and its beat/downbeat overlay. The analyze step still reports
  tempo and beat/downbeat counts in the status line; EDL export is unaffected. Update spec.md and
  README accordingly.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01KtcNWL6Htudp7EzH1jdkqC
