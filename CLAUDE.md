# CLAUDE.md

このリポジトリで作業する際の規約と頻出コマンド。

## プロジェクト概要

オーディオのビートを解析し、DaVinci Resolve 用の EDL マーカーファイルを生成するデスクトップアプリ。
詳細仕様は `docs/spec.md`。

## 開発環境（uv 管理）

このプロジェクトは **uv** で管理する。pip は使わない。

```bash
uv sync                      # 依存（dev含む）をインストール
uv run pytest -q             # テスト実行
uv run beat-edl              # GUI 起動
uv run beat-edl-cli a.wav    # CLI 実行
uv add <pkg>                 # 依存追加（pyproject + lock を更新）
uv lock                      # ロック再生成
```

- ランタイム依存は `[project.dependencies]`、開発用は `[dependency-groups].dev`。
- **madmom は uv の依存に入れない**（理由は下記）。

## madmom（任意・高精度ダウンビート）

リリース版 madmom は Python 3.10+ でインポートに失敗するため、git ビルドを使う。
`--no-build-isolation` が必要で lock に乗せると壊れやすいので、手動インストール扱い。

```bash
uv pip install cython "numpy<2" mido
uv pip install --no-build-isolation "git+https://github.com/CPJKU/madmom.git"
```

未導入でも librosa バックエンドで動作する（madmom が入っていれば自動で優先される）。

## exe ビルド（PyInstaller, onedir）

- 設定: `packaging/beat-edl.spec`（`web/` を同梱）。
- ローカル（Windows）: `packaging/build.ps1` を実行 → `dist/beat-edl/` に生成。
- CI: `.github/workflows/build-windows.yml`（Windows runner）が push/tag でビルドし
  アーティファクトを出力。
- **Linux 環境では Windows exe はビルド不可**（PyInstaller はクロスコンパイル不可）。

## ブランチ運用（GitHub Flow）

- デフォルトブランチは `main`。常にビルド可能・リリース可能な状態を保つ。
- 機能・修正は `main` から短命ブランチを切って作業する。
- ブランチ名は **コミット型のプレフィックス** に合わせ、`<type>/<短い説明>`（説明は英語 kebab-case）:
  - `feat/` 新機能, `fix/` バグ修正, `docs/` ドキュメント,
    `build/` ビルド/依存/パッケージング, `refactor/`, `test/`, `perf/`, `chore/`
  - 例: `feat/madmom-progress`, `fix/edl-timeline-offset`, `docs/branching-policy`
- `main` への反映は **原則 Pull Request 経由**（レビュー/CI の記録を残す）。
  タイポ等の軽微な修正は `main` へ直接コミット可。
- リリースは SemVer タグ `vX.Y.Z`。タグ push で Windows exe が CI ビルドされる。

## コミット規約

- **粒度: 論理単位で自律的にコミットする**。「uv化」「docs追加」「pyinstaller設定」のような
  意味のあるまとまりごとに 1 コミット。1 コミットに無関係な変更を混ぜない。
- コミットメッセージは命令形の要約 + 必要なら本文で「なぜ」を説明。
  要約はブランチ型と同じ接頭辞（`feat:` / `fix:` / `docs:` / `build:` …）を付ける。
- PR はユーザーから明示的に依頼があるまで作らない。

## アーキテクチャの要点

- 検出は `detection/` の `BeatDetector` 実装（librosa / madmom）を `core.py` が駆動。
  検出と EDL 出力は GUI 非依存で、CLI・テスト・GUI から共通利用する。
- 新しい検出方式を足すときは `BeatDetector` を実装し `detection/__init__.py` の
  レジストリに登録する。
- EDL/タイムコードのロジックを変えたら `tests/` を更新・追加する。
