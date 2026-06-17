"""PyInstaller entry point.

PyInstaller runs the entry file as a top-level script (no parent package), so
beat_edl.__main__ cannot be used directly because of its relative imports.
Import the package's main() with an absolute import instead.
"""

from beat_edl.__main__ import main

if __name__ == "__main__":
    main()
