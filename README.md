# beat-edl

オーディオファイルのビートを解析し、DaVinci Resolve で読み込める **EDL マーカーファイル**を書き出すデスクトップアプリです。

- **ビート検出**: 既定は [librosa](https://librosa.org/)（追加依存が軽い）。小節頭（ダウンビート）はオンセット強度から位相推定します。任意で [madmom](https://github.com/CPJKU/madmom) を入れると、RNN+DBN による高精度なダウンビート/拍子トラッキングが使えます。
- **GUI**: [pywebview](https://pywebview.flowrl.com/) による軽量シェル（OS標準WebViewを使用＝Tauri相当の軽さ）。波形＋ビートマーカーを `wavesurfer.js` で表示します。
- **出力**: CMX3600 EDL。各ビートをマーカーとして書き出し（`|C:` 色 / `|M:` 名前 / `|D:` 長さ）。小節頭は色分け可能。

## アーキテクチャ

```
src/beat_edl/
  detection/        # ビート検出バックエンド（差し替え可能）
    base.py         #   BeatDetector インターフェース / BeatResult / DetectOptions
    librosa_backend.py   # 既定。テンポ+ビート、ヒューリスティックな小節頭推定
    madmom_backend.py    # 任意。真のダウンビート/拍子トラッキング
  edl/writer.py     # CMX3600 EDL マーカー書き出し（Resolve 互換）
  timecode.py       # 秒 -> SMPTE タイムコード変換（フレーム量子化）
  core.py           # 解析 -> マーカー生成 -> EDL のパイプライン（GUI非依存）
  api.py            # pywebview の JS<->Python ブリッジ
  cli.py            # ヘッドレス CLI
  __main__.py       # デスクトップウィンドウ起動
web/                # フロントエンド（HTML/CSS/JS）
tests/              # timecode / edl のユニットテスト
```

検出と出力は GUI から切り離されており、`core.py` を CLI・テスト・GUI のいずれからも同じように駆動できます。

## インストール

```bash
pip install -e .            # librosa バックエンド + GUI
```

### 任意: madmom（高精度ダウンビート）

リリース版 madmom は Python 3.10+ でビルド/インポートに失敗するため、互換ビルドを git から入れます:

```bash
pip install -e ".[madmom]"
pip install --no-build-isolation "git+https://github.com/CPJKU/madmom.git"
```

> madmom バックエンドの音声読み込みは librosa 経由で行うため、ffmpeg は不要です。

## 使い方

### GUI

```bash
beat-edl            # または: python -m beat_edl
```

オーディオを選択 → 拍子・fps などを設定 → 「解析」で波形上にビート/小節頭を表示 → 「EDL書き出し」。

### CLI

```bash
beat-edl-cli song.wav -o song.edl --fps 24 --beats-per-bar 4
beat-edl-cli song.wav --backend madmom --downbeats-only
```

## Resolve への取り込み

書き出した `.edl` を Resolve のメディアプール/タイムラインへインポートするとマーカーが復元されます。マーカーの記録タイムコードはタイムライン開始TC（既定 `01:00:00:00`）を基準にオフセットされるので、Resolve 既定のタイムラインにそのまま合います。

## 開発

```bash
pip install -e ".[dev]"
PYTHONPATH=src pytest -q
```
