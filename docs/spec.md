# beat-edl 仕様書

オーディオファイルのビートを解析し、DaVinci Resolve に取り込める **EDL マーカーファイル**を生成するデスクトップアプリの仕様。

## 1. 目的・スコープ

- 入力: 単一のオーディオファイル（wav / mp3 / flac / m4a / aac / ogg）。
- 出力: CMX3600 形式の `.edl`。各ビート位置にマーカーを配置する。
- 用途: 楽曲のビートに合わせた編集（カット/エフェクト）の基準点を Resolve 上に用意する。

非スコープ: 映像の解析、マルチトラック、リアルタイム処理。

## 2. 機能要件

| ID | 要件 |
|----|------|
| F-1 | オーディオファイルを選択できる（ネイティブダイアログ）。 |
| F-2 | ビートとテンポ(BPM)を自動検出する。 |
| F-3 | 拍子（1小節あたりの拍数, 既定 4）を指定し、小節頭（ダウンビート）を特定する。 |
| F-4 | テンポを手動指定（ヒント）できる（0 で自動）。 |
| F-5 | 「Nビートごと」に間引いてマーカーを出力できる。 |
| F-6 | 「小節頭のみ」出力モードを選べる。 |
| F-7 | フレームレート（23.976〜60）を指定できる。 |
| F-8 | マーカー色・小節頭色を Resolve パレットから選べる。小節頭の色分けは ON/OFF 可能。 |
| F-9 | タイムライン開始TC（既定 `01:00:00:00`）を指定でき、マーカーTCはこれを基準にオフセットされる。 |
| F-10 | 波形上にビート/小節頭をオーバーレイ表示する。 |
| F-11 | `.edl` を保存ダイアログで書き出す。 |
| F-12 | GUIを使わないヘッドレスCLIを提供する。 |

## 3. ビート検出

検出は差し替え可能なバックエンド構成（`BeatDetector` インターフェース）。

### 3.1 librosa バックエンド（既定・軽量）

- `librosa.beat.beat_track` でテンポとビートフレームを取得。
- ダウンビートは **ヒューリスティック**: `beats_per_bar` を周期として位相を 0..N-1 まで試し、
  各位相のビート上のオンセット強度の総和が最大になる位相を小節頭とみなす
  （小節頭は強拍であることが多いという前提）。
- 追加依存が軽く（PyTorch 不要）、必ず動作する既定経路。
- 限界: 曲によっては位相を誤ることがある。拍子変化には未対応。

### 3.2 madmom バックエンド（任意・高精度）

- `RNNDownBeatProcessor` + `DBNDownBeatTrackingProcessor(beats_per_bar=[N], fps=100)`。
- モデルがビートと小節内位置を直接返すため、ダウンビートが正確。
- 音声読み込みは librosa 経由で行い、**ffmpeg 不要**にしている。
- 導入は任意（インストール手順は CLAUDE.md / README 参照）。リリース版は Python 3.10+ で
  壊れるため git ビルドを使う。

### 3.3 バックエンド選択

`get_backend(name)`:
- `name=None` のとき madmom → librosa の順で利用可能なものを選ぶ。
- 利用可能なバックエンドは `available_backends()` がインストール状況から返す。

## 4. EDL 出力仕様

DaVinci Resolve のマーカー round-trip 形式（CMX3600）に従う。

```
TITLE: Beat Markers
FCM: NON-DROP FRAME

001  001      V     C        01:00:01:00 01:00:01:01 01:00:01:00 01:00:01:01
 |C:ResolveColorBlue |M:Beat 1 |D:1
```

- イベント番号は 1 始まりの連番。
- 各マーカーはソース/レコードに同じ in/out を持つ（マーカー用途では値は同一でよいが、
  EDL 文法上 4 つの TC が必要）。
- コメント行 `|C:` = 色（`ResolveColor<Name>`）, `|M:` = マーカー名, `|D:` = 長さ(フレーム)。
- レコードTC = タイムライン開始TC + ビート位置（秒→フレーム量子化）。

### 4.1 タイムコード変換

- `seconds_to_frames(t, fps)` = `round(t * fps)`（最近接フレームへ量子化）。
- NTSC系（23.976/29.97/59.94）は **non-drop** とし、ラベルは丸めた整数レート（24/30/60）を使う。
- マーカーは開始TCぶんのフレーム数を加算した絶対フレームから HH:MM:SS:FF を算出。

### 4.2 Resolve マーカー色

`Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream`。

## 5. アーキテクチャ

```
src/beat_edl/
  detection/   検出バックエンド（base / librosa / madmom）+ レジストリ
  edl/writer   CMX3600 マーカー書き出し
  timecode     秒→SMPTE 変換
  core         解析→マーカー生成→EDL のパイプライン（GUI非依存）
  api          pywebview の JS<->Python ブリッジ
  cli          ヘッドレスCLI
  __main__     デスクトップウィンドウ起動
  web/         フロントエンド（HTML/CSS/JS, wavesurfer.js）
```

`core.py` を CLI・テスト・GUI から共通に駆動する。

## 6. 配布

- **GUI**: pywebview（OS標準WebView）。Windows は WebView2 ランタイムを利用。
- **exe**: PyInstaller の onedir 構成（onefile 不要）。`web/` をデータとして同梱。
  Linux ではビルド不可のため Windows 上 or GitHub Actions(Windows runner) でビルドする。

## 7. 既知の制約 / TODO

- librosa のダウンビート推定は位相誤りの可能性あり（高精度は madmom 推奨）。
- 拍子変化・可変テンポには未対応。
- Resolve への実インポート検証（色・位置）は実機確認が必要。
- GUI 実機表示（`file://` での波形ロード、ダイアログ）は要確認。
