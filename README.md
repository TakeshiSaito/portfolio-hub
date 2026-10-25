# portfolio-hub

[![CI](https://github.com/TakeshiSaito/portfolio-hub/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/TakeshiSaito/portfolio-hub/actions/workflows/ci.yml?query=branch%3Amain)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

1 台のマシン上で、プロジェクトとその中の [rez](https://github.com/AcademySoftwareFoundation/rez) 環境を管理し、その環境でツールを起動するハブです。
操作の入口として、コマンドライン（`phub`）と HTTP API（FastAPI）を用意しています。

この README では、仮想環境を用意して CLI を動かし、`serve` コマンドで FastAPI のドキュメント画面（Swagger UI）を開くまでを案内します。

## 必要なもの

- macOS または Linux
- [uv](https://docs.astral.sh/uv/)（Python 3.14 は uv が自動で用意します）

## 1. 仮想環境をセットアップする

リポジトリを取得し、ルートで `uv sync` を実行します。

```bash
git clone <このリポジトリの URL> launcher
cd launcher
uv sync
```

`.venv/` に仮想環境が作られ、Python 3.14 と依存パッケージ（rez、FastAPI など）がインストールされます。
以降のコマンドはすべて `uv run` 経由で、この仮想環境の中で実行します。

次に、rez がパッケージを探す場所を指定します。
ここではリポジトリに同梱のサンプルパッケージ（`packages/`）を使います。

```bash
export REZ_PACKAGES_PATH="$PWD/packages"
```

## 2. CLI を動かす

ヘルプでコマンドの一覧を確認します。
`projects` と `environments` は、`list`、`create`、`rename`、`delete` などのサブコマンドを持ちます（`uv run phub environments --help`）。

```bash
uv run phub --help
```

バージョンは `uv run phub --version` で確認できます。Swagger UI では、タイトルの横に表示されます。

使えるパッケージを一覧にします。

```console
$ uv run phub packages
 name            version
 greeter         1.0.0
 greeter         2.0.0
 greeter_plugin  1.0.0
 hello           1.0.0
```

初めて起動したときは、サンプルのプロジェクトと環境が作られます。
`environments list` は、プロジェクトの環境を、パッケージとツールと一緒に表で表示します。

```console
$ uv run phub projects list
sample_project
$ uv run phub environments list sample_project
 name                packages     tools  default tool
 sample_environment  hello 1.0.0  hello  terminal
```

環境を作り、その環境が解決するパッケージを確認します。

```console
$ uv run phub environments create sample_project anim --package greeter 2.0.0 --tool greet --default-tool greet
$ uv run phub environments list sample_project
 name                packages       tools  default tool
 sample_environment  hello 1.0.0    hello  terminal
 anim                greeter 2.0.0  greet  greet
$ uv run phub resolve sample_project anim
 name     version
 greeter  2.0.0
```

環境の中でツールを起動します。起動したプロセスの PID が表示されます。
ツール名に `terminal` を指定すると、その環境に入ったターミナルが開きます。
ツール名を省くと、環境の既定のツール（`--default-tool`）が起動します。既定のツールを決めていない環境では `terminal` が既定なので、ターミナルが開きます。

```bash
uv run phub launch sample_project anim greet
```

データは `PORTFOLIO_HUB_SQLITE_PATH`（既定は `PORTFOLIO_HUB_HOME` の下の `portfolio_hub.db`）の SQLite に保存されます。

## 3. serve で FastAPI のドキュメント画面を開く

HTTP API を起動します。

```console
$ uv run phub serve
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

ブラウザで <http://127.0.0.1:8000/docs> を開くと、FastAPI のドキュメント画面（Swagger UI）が表示されます。
各エンドポイントには「Try it out」が最初から有効になっており、入力例を使ってそのまま API を呼び出せます。
CLI で作った `anim` 環境は、`GET /api/projects` で `sample_project` の ID を調べ、`GET /api/projects/{project_id}/environments` で確認できます。

HTTP API はこのマシンのプロセスを起動できるので、`Host` が `127.0.0.1` か `localhost` のリクエストだけを受け付けます（それ以外は 400）。
ほかのサイトから、DNS リバインディングで手元のサーバーを呼ばれるのを防ぐためです。

止めるときは `Ctrl+C` を押します。

## 設定

設定は環境変数で変更します。コマンドを実行するディレクトリ（通常はリポジトリ直下）の `.env` ファイルにも書けます。

| 環境変数 | 既定値 | 内容 |
| --- | --- | --- |
| `PORTFOLIO_HUB_HOST` | `127.0.0.1` | `serve` が待ち受けるホスト |
| `PORTFOLIO_HUB_PORT` | `8000` | `serve` が待ち受けるポート |
| `PORTFOLIO_HUB_HOME` | リポジトリ直下 | データの置き場所。データベースとログの既定の置き場所になる |
| `PORTFOLIO_HUB_LOG_PATH` | `PORTFOLIO_HUB_HOME` の下の `logs/portfolio_hub.log` | ログのファイル |
| `PORTFOLIO_HUB_SQLITE_PATH` | `PORTFOLIO_HUB_HOME` の下の `portfolio_hub.db` | データを保存する SQLite ファイル |
| `PORTFOLIO_HUB_REZ_BUNDLED_PACKAGES_PATH` | リポジトリ直下の `packages/` | 同梱の rez パッケージの置き場所（rez の設定のパスに加えて探す） |
| `PORTFOLIO_HUB_REZ_TERMINAL_COMMAND` | macOS は `open -a Terminal`、それ以外は `x-terminal-emulator -e` | `terminal` を `launch` したときに使うターミナル |

`REZ_PACKAGES_PATH` は rez 自身の設定なので、`.env` ではなくシェルで指定してください。

## ログ

プロジェクトや環境を作る・変える・消す操作と、ツールの起動は、ログ（`PORTFOLIO_HUB_LOG_PATH`）に 1 行ずつ追記されます。
CLI と HTTP API のどちらから操作しても記録され、一覧の表示などの読むだけの操作は記録されません。
ログが 1 MB を超えると、新しいファイルに切り替わります。古いログは `portfolio_hub.log.1` 〜 `portfolio_hub.log.5` として 5 世代まで残ります。

```text
2026-10-25T10:00:00+0900 INFO portfolio_hub.applications created project foo (5bc2ec40-5051-4c69-9964-ae1504bedafd)
2026-10-25T10:00:05+0900 INFO portfolio_hub.applications launched greet in environment anim (6db7caea-29e4-473a-9442-f7299949089f) with pid 12345
```

## テスト

```bash
./test.sh
```

pytest を実行し、JUnit 形式の結果とカバレッジを `reports/` に書き出します。カバレッジが 70% を下回ると失敗します。
テストは `packages/` のパッケージに対して、実際の rez を使って動きます。

モジュールの依存の向き（ドメインがアダプターや入口に依存しない、など）は、`tach.toml` に書いた規則を tach で確かめます。

```bash
uv run tach check
```

## リリース

`CHANGELOG.md` に新しいバージョンの節（`## [0.0.2] - 2026-11-01` など）を書き、`uv version 0.0.2` で `pyproject.toml` のバージョンを揃えて main に入れます。
GitHub Actions（`.github/workflows/release.yml`）がテストとビルドを行い、タグ `v0.0.2` と GitHub Release を作ります。リリースノートには、`CHANGELOG.md` のその節が入ります。
同じバージョンの Release がすでにあれば、何もしません。

## ライセンス

[MIT](LICENSE)
