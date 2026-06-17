"""Beat-detection backends and a small registry to select among them."""

from __future__ import annotations

from .base import BeatDetector, BeatResult, DetectOptions
from .librosa_backend import LibrosaBackend
from .madmom_backend import MadmomBackend

# Ordered by preference: madmom gives true downbeats when available, otherwise
# librosa with heuristic downbeats is the dependency-light default.
_BACKENDS: dict[str, type[BeatDetector]] = {
    LibrosaBackend.name: LibrosaBackend,
    MadmomBackend.name: MadmomBackend,
}


def available_backends() -> list[str]:
    """Names of backends whose dependencies are installed."""
    return [name for name, cls in _BACKENDS.items() if cls.is_available()]


def get_backend(name: str | None = None) -> BeatDetector:
    """Return a backend instance.

    With ``name`` of None, prefer madmom (true downbeats) then librosa. Raise if
    the requested backend, or any backend at all, is unavailable.
    """
    if name is None:
        for candidate in (MadmomBackend.name, LibrosaBackend.name):
            if _BACKENDS[candidate].is_available():
                return _BACKENDS[candidate]()
        raise RuntimeError(
            "no beat-detection backend is available; install 'librosa'"
        )

    if name not in _BACKENDS:
        raise KeyError(f"unknown backend {name!r}; choose from {list(_BACKENDS)}")
    cls = _BACKENDS[name]
    if not cls.is_available():
        raise RuntimeError(f"backend {name!r} is not installed")
    return cls()


__all__ = [
    "BeatDetector",
    "BeatResult",
    "DetectOptions",
    "LibrosaBackend",
    "MadmomBackend",
    "available_backends",
    "get_backend",
]
