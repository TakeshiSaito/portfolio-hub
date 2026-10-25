# portfolio-hub

[![CI](https://github.com/TakeshiSaito/portfolio-hub/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/TakeshiSaito/portfolio-hub/actions/workflows/ci.yml?query=branch%3Amain)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

1 台のマシン上で、プロジェクトとその中の [rez](https://github.com/AcademySoftwareFoundation/rez) 環境を管理し、その環境でツールを起動するハブです。
操作の入口として、コマンドライン（`phub`）と HTTP API（FastAPI）を用意しています。

## 必要なもの

- macOS または Linux
- [uv](https://docs.astral.sh/uv/)
- 開いたターミナルで使う `python3`

## 1. 環境を用意する

リポジトリを取得し、依存パッケージをインストールします。

```bash
git clone https://github.com/TakeshiSaito/portfolio-hub.git
cd portfolio-hub
uv sync
```

## 2. ターミナルを開いて、ライブラリを使う

使えるパッケージを確かめます。`greeter` は、Python から使えるライブラリです。

```console
$ uv run phub packages
 name            version
 greeter         1.0.0
 greeter         2.0.0
 greeter_plugin  1.0.0
 hello           1.0.0
```

初めて起動したときに作られるプロジェクト `sample_project` に、`greeter 2.0.0` を入れた環境 `anim` を作ります。

```console
$ uv run phub environments create sample_project anim --package greeter 2.0.0
created environment anim in project sample_project
$ uv run phub environments list sample_project
 name                packages       tools  default tool
 sample_environment  hello 1.0.0    hello  terminal
 anim                greeter 2.0.0         terminal
```

環境を起動します。既定のツールが `terminal` なので、`anim` 環境に入ったターミナルが新しく開きます。

```console
$ uv run phub launch sample_project anim
launched terminal in environment anim of project sample_project (pid 12345)
```

開いたターミナルで Python を起動し、`greeter` を使います。

```console
$ python3
>>> import greeter
>>> greeter.greet("world")
'Hello, world!'
```

## 3. FastAPI の画面を開く

HTTP API を起動します。

```console
$ uv run phub serve
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

ブラウザで <http://127.0.0.1:8000/docs> を開くと、FastAPI のドキュメント画面（Swagger UI）が表示されます。
各エンドポイントには「Try it out」が最初から有効になっていて、入力例を使ってそのまま API を呼び出せます。
例えば `GET /api/projects` を実行すると、`sample_project` が返ります。

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
| `PORTFOLIO_HUB_REZ_TERMINAL_COMMAND` | macOS は `open -a Terminal`、それ以外は `x-terminal-emulator -e` | `terminal` を起動したときに使うターミナル |

同梱のパッケージ（`packages/`）は、いつも探し先に入ります。ほかの場所の rez パッケージも使うときは、rez 自身の設定の `REZ_PACKAGES_PATH` をシェルで指定してください。
