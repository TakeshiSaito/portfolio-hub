---
paths:
  - "CHANGELOG.md"
  - "pyproject.toml"
  - ".github/workflows/release.yml"
  - ".github/scripts/changelog.py"
---

# チェンジログとリリース

- `CHANGELOG.md` は [Keep a Changelog 1.1.0](https://keepachangelog.com/ja/1.1.0/) の形式で書く。
- 節は、新しいバージョンから順に `## [X.Y.Z] - YYYY-MM-DD` の見出しで置く。
- 節の中は変更の種類（`### Added` など）ごとに分け、使わない種類の見出しは書かない。
- 利用者から見える変更は、いちばん上の、まだリリースしていないバージョンの節に書く。
- そういう節がなければ新しく作り、`uv version <バージョン>` で `pyproject.toml` を揃える。
- バージョンは [Semantic Versioning](https://semver.org/lang/ja/) で付ける。
