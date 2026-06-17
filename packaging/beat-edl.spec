# PyInstaller spec for beat-edl (onedir build).
#
# Build:  uv run pyinstaller packaging/beat-edl.spec --noconfirm
# Output: dist/beat-edl/  (a directory; not onefile, by design)
#
# Note: PyInstaller cannot cross-compile. Build the Windows app on Windows
# (locally via packaging/build.ps1 or in CI via build-windows.yml).

import os

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
WEB_SRC = os.path.join(ROOT, "src", "beat_edl", "web")
# Use a dedicated entry script: PyInstaller runs the entry as a top-level
# script, where beat_edl.__main__'s relative imports would fail.
ENTRY = os.path.join(ROOT, "packaging", "entry.py")

# Ship the web UI so the frozen app resolves sys._MEIPASS/beat_edl/web.
datas = [(WEB_SRC, os.path.join("beat_edl", "web"))]
# librosa loads parts of itself and its data lazily; bundle data + submodules.
datas += collect_data_files("librosa")
datas += collect_data_files("soundfile")

hiddenimports = []
hiddenimports += collect_submodules("librosa")
# sklearn/scipy/numba/soundfile/pywebview are covered by PyInstaller's bundled
# hooks; add the few dynamic imports those hooks tend to miss.
hiddenimports += ["sklearn.utils._typedefs", "sklearn.neighbors._partition_nodes"]

block_cipher = None

a = Analysis(
    [ENTRY],
    pathex=[os.path.join(ROOT, "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="beat-edl",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # windowed GUI app
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="beat-edl",
)
