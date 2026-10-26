# 運用

README は、環境を作ってターミナルを開き、Python からライブラリを使うところまでを案内します。この文書は、その先でコマンドと HTTP API が共有している決まり、失敗したときのメッセージ、データベースとログの置き場所をまとめます。

サブコマンドの説明は `phub --help`、リクエストの形と例は Swagger UI（<http://127.0.0.1:8000/docs>）にあります。

## 構成

portfolio-hub は、1 台のマシンの上でプロジェクトと rez の環境を覚え、その環境でツールを起動します。

- プロジェクトは環境を持ちます。環境の名前は、そのプロジェクトの中で一意です。
- 環境は、解決するパッケージ、起動してよいツール、ツールを省略したときに起動する既定のツールを持ちます。
- パッケージの一覧と解決は rez が行います。同梱のパッケージはリポジトリの `packages/` にあります。
- プロジェクトと環境の記録は SQLite にあります。パッケージの中身はデータベースへコピーしません。

入口は `phub` と `phub serve` です。どちらも `portfolio_hub.applications` の同じ関数を呼びます。

| モジュール | 役割 |
| --- | --- |
| `portfolio_hub.cli` / `portfolio_hub.http` | コマンドと HTTP の入口 |
| `portfolio_hub.applications` | 作成、変更、解決、起動。成功した操作のログ |
| `portfolio_hub.project` / `portfolio_hub.environment` | 名前、パッケージ、ツールの決まり |
| `portfolio_hub.sqlite` | SQLite への保存 |
| `portfolio_hub.rez` | パッケージの一覧、解決、起動 |
| `portfolio_hub.installer` | 上記の組み立て。データベースのファイルが無いとき、見本を作る |

## 名前と中身

プロジェクト名と環境名は 2 文字以上 64 文字以下で、英数字と `_` です（`^[A-Za-z0-9_]+$`）。

| 入力 | メッセージ |
| --- | --- |
| `sample project` | `String should match pattern '^[A-Za-z0-9_]+$'` |
| `a` | `String should have at least 2 characters` |
| 65 文字 | `String should have at most 64 characters` |

プロジェクト名はこのマシンの中で一意です。同じ名前を作ると `project sample_project already exists` になります。今の名前への変更は成功します。

環境名はプロジェクトの中で一意です。別のプロジェクトには同じ名前を付けられます。重複すると `the project already has an environment named anim` になります。HTTP でプロジェクトを作るとき、同名の環境を 2 つ渡した場合もこのメッセージになり、プロジェクトは残りません。

パッケージ名は `^[A-Za-z0-9_][A-Za-z0-9_.]*$`、版は 1 文字以上です。環境にはパッケージが 1 つ以上必要です（`an environment needs at least one package`）。同じパッケージ名を 2 回入れると `packages are chosen more than once: greeter` になります。版が違っていても、同じ名前は 1 つだけです。

ツール名は空白を含まない 1 文字以上 64 文字以下です（`^\S{1,64}$`）。同じツールを 2 回登録すると `tools are registered more than once: greet` になります。既定のツールは `terminal` か、登録したツールの 1 つです。登録していない名前を既定にすると `default tool cheer is not one of the tools` になります。

`terminal` はツールの一覧に無くても起動できます。一覧に無いそれ以外の名前は `tool nosuchtool is not one of the tools of environment anim` で失敗します。

`phub environments set-packages` と `set-tools`、および対応する HTTP の PUT は、渡した一覧で全体を置き換えます。`set-tools` で `--tool` を省略するとツールは空になり、`--default-tool` を省略していれば既定は `terminal` です。

環境を保存する時点では解決しません。存在しないパッケージも環境として保存でき、失敗は `resolve` か `launch` でわかります。

## コマンド

CLI は名前でプロジェクトと環境を探します。成功すると終了コードは 0 です。データを変えるコマンドと `launch` は、何をしたかを 1 行で出します。失敗すると終了コードは 1 で、メッセージは標準エラーに 1 行です。

`phub` は引数を読む前にデータベースを用意します。`--help` と `--version` でも、ファイルが無ければ見本の `sample_project` を作ります。

| コマンド | 成功したときの 1 行 |
| --- | --- |
| `phub projects create <name>` | `created project <name>` |
| `phub projects rename <name> <new>` | `renamed project <name> to <new>` |
| `phub projects delete <name>` | `deleted project <name>` |
| `phub environments create <project> <name> --package <pkg> <version>` | `created environment <name> in project <project>` |
| `phub environments rename <project> <name> <new>` | `renamed environment <name> to <new> in project <project>` |
| `phub environments set-packages <project> <name> --package ...` | `replaced the packages of environment <name> in project <project>` |
| `phub environments set-tools <project> <name> --tool ...` | `replaced the tools of environment <name> in project <project>` |
| `phub environments delete <project> <name>` | `deleted environment <name> from project <project>` |
| `phub launch <project> <environment> [tool]` | `launched <tool> in environment <environment> of project <project> (pid <pid>)` |

一覧は表です。0 件でも見出しは出ます。

- `phub projects list` の列は `name` です。行は保存した順です。
- `phub environments list <project>` の列は `name`、`packages`、`tools`、`default tool` です。行は保存した順です。パッケージは `名前 版` を名前と版で並べ、`, ` でつなぎます。ツールは名前で並べ、`, ` でつなぎます。
- `phub packages` と `phub resolve` の列は `name` と `version` で、名前と版の順です。

プロジェクトを削除すると、そのプロジェクトの環境も削除されます。他のプロジェクトの環境は残ります。

`phub projects create` が受け取るのは名前だけです。プロジェクトと環境を 1 回のリクエストで作るのは、HTTP の `POST /api/projects` です。

## 解決と起動

`phub resolve <project> <environment>` は、rez が選んだパッケージを表示します。依存も含みます。`greeter_plugin 1.0.0` は `greeter-2` を要求するので、`greeter 2.0.0` も解決結果に入ります。

```console
$ uv run phub environments create sample_project anim --package greeter_plugin 1.0.0
created environment anim in project sample_project
$ uv run phub resolve sample_project anim
 name            version
 greeter         2.0.0
 greeter_plugin  1.0.0
```

探し先は、rez の `packages_path` のうしろに同梱ディレクトリを足した一覧です。同じパスは 1 つにまとめます。`REZ_PACKAGES_PATH` を置くと rez 側の一覧が変わります。同梱ディレクトリは、その場合も一覧に残ります。同梱ディレクトリの既定はリポジトリの `packages/` で、`PORTFOLIO_HUB_REZ_BUNDLED_PACKAGES_PATH` で変えられます。

| パッケージ | 中身 |
| --- | --- |
| `hello 1.0.0` | コマンド `hello` が `Hello, World!` を出します |
| `greeter 1.0.0` | `greeter.greet(name)` は `Hello, world!` の形です。コマンド `greet` は、引数が無ければ `Hello, world! (greeter 1.0.0)` を出します |
| `greeter 2.0.0` | `greeter.greet(name, excited=False)` です。`excited=True` のときは `Hello, world!!!` です。コマンド `greet` は、引数が無ければ `Hello, world! (greeter 2.0.0)` を出します |
| `greeter_plugin 1.0.0` | `greeter-2` が必要です。`greeter_plugin.cheer` とコマンド `cheer` は `greeter.greet(name, excited=True)` を呼びます |

見本の環境は `hello 1.0.0` を要求し、ツール `hello` を登録し、既定のツールは `terminal` です。`hello` を起動すると、ツールが `Hello, World!` を出し、`phub` は `launched hello in environment sample_environment of project sample_project (pid <pid>)` を出します。`<pid>` はそのときのプロセス番号です。

ツールを省略すると、環境の既定のツールが起動します。表示には、実際に起動したツール名が入ります。`terminal` のときは、解決した環境の対話シェルを開きます。使うプログラムは `PORTFOLIO_HUB_REZ_TERMINAL_COMMAND` で、macOS の既定は `open -a Terminal`、それ以外は `x-terminal-emulator -e` です。

解決に失敗すると、メッセージは rez の文面です。CLI の終了コードは 1、HTTP は 422 です。環境の記録は残ります。

| 要求 | メッセージ |
| --- | --- |
| `greeter 9.9.9` | `Package could not be found: greeter-9.9.9` |
| 未知のパッケージ名 | パッケージ名と、探したディレクトリが入った rez のメッセージ |
| `greeter 1.0.0` と `greeter_plugin 1.0.0` | `The following package conflicts occurred: (greeter-2 <--!--> greeter==1.0.0)` |

`launch` の 1 行には解決結果が入りません。解決結果は `resolve` で見ます。HTTP の起動レスポンスには `tool`、`pid`、`resolved_packages` が入ります。

ツールとして登録できることと、解決した環境にその実行ファイルがあることは別です。`hello` だけの環境に `greet` を登録して起動すると、`FileNotFoundError`（`greet` が無い）のトレースバックになります。

## HTTP API

`phub serve` は `PORTFOLIO_HUB_HOST` と `PORTFOLIO_HUB_PORT`（既定は `127.0.0.1:8000`）で待ちます。受け取れる `Host` は `127.0.0.1` と `localhost` です。それ以外の `Host` は状態 400 で、本文は `Invalid host header` です。

API は UUID でプロジェクトと環境を指定します。

| 操作 | メソッドとパス | 成功 |
| --- | --- | --- |
| プロジェクト一覧 | `GET /api/projects` | 200 |
| プロジェクト作成 | `POST /api/projects` | 201 |
| プロジェクト名の変更 | `PUT /api/projects/{project_id}/name` | 204、本文は空 |
| プロジェクト削除 | `DELETE /api/projects/{project_id}` | 204、本文は空 |
| 環境一覧 | `GET /api/projects/{project_id}/environments` | 200 |
| 環境作成 | `POST /api/projects/{project_id}/environments` | 201 |
| 環境名の変更 | `PUT /api/environments/{environment_id}/name` | 204、本文は空 |
| パッケージの置き換え | `PUT /api/environments/{environment_id}/packages` | 204、本文は空 |
| ツールの置き換え | `PUT /api/environments/{environment_id}/tools` | 204、本文は空 |
| 環境削除 | `DELETE /api/environments/{environment_id}` | 204、本文は空 |
| パッケージ一覧 | `GET /api/packages` | 200 |
| 解決 | `GET /api/environments/{environment_id}/resolved-packages` | 200 |
| 起動 | `POST /api/environments/{environment_id}/launches` | 201 |

失敗したときの本文は `{"detail": "<message>"}` です。

| 状態 | とき |
| --- | --- |
| 404 | プロジェクトまたは環境が無い。`project <uuid> does not exist`、`environment <uuid> does not exist` |
| 409 | 名前が既に使われている |
| 422 | 決まりに反する、解決できない、またはリクエストの形が違う |

UUID でないパスは 422 です。検証メッセージが複数あるときは、`; ` でつないで 1 つの `detail` にします。`GET /api/projects/not-a-uuid/environments` の `detail` は次のとおりです。

```text
Input should be a valid UUID, invalid character: found `n` at 0
```

起動するツールは JSON の `tool` です。省略すると環境の既定のツールになります。値 `terminal` はターミナルを開きます。

## データとログ

データベースとログは、プロセスの開始時に用意します。場所の既定値は README の設定一覧と同じです。

| ファイル | 既定 |
| --- | --- |
| データベース | `PORTFOLIO_HUB_HOME` の `portfolio_hub.db` |
| ログ | `PORTFOLIO_HUB_HOME` の `logs/portfolio_hub.log` |

`PORTFOLIO_HUB_HOME` の既定はリポジトリ直下です。カレントディレクトリの `.env` を読み、未知の変数は無視します。

データベースのファイルが無いとき、見本を作ります。

| 名前 | 中身 |
| --- | --- |
| プロジェクト `sample_project` | |
| 環境 `sample_environment` | パッケージ `hello 1.0.0`、ツール `hello`、既定のツール `terminal` |

ファイルが既にあるときは見本を足しません。見本からやり直すときは、プロセスを止めてからデータベースのファイルを消し、次の `phub` を実行します。

テーブルは `projects`（`id`、一意な `name`）、`environments`（プロジェクト内で一意な `name`、`default_tool`）、`environment_packages`（`name`、`version`）、`environment_tools`（`name`）です。外部キーは有効です。プロジェクトと環境の一覧は、保存した順です。

ログはロガー `portfolio_hub` の INFO です。1 行の形は次のとおりです。

```text
YYYY-MM-DDTHH:MM:SS±HHMM INFO portfolio_hub.applications <message>
```

ファイルは 1,000,000 バイトでローテーションし、古いファイルを 5 つ残します。

記録するのは、成功した作成、名前の変更、パッケージとツールの置き換え、削除、起動です。失敗は標準エラーの 1 行です。作成と削除の行には名前と id が入ります。次は、見本を作ったときの形です。id と時刻は、その実行の値です。

```text
2026-10-26T16:05:17+0000 INFO portfolio_hub.applications created project sample_project (c2e438ca-74ba-463c-85c3-e8454580ca6a)
2026-10-26T16:05:17+0000 INFO portfolio_hub.applications created environment sample_environment (b5a21cba-6a8e-4920-bf08-8e7e30b290ea) in project sample_project
```

プロジェクトを消したときは、環境の削除が先に記録されます。

## つまずきやすいところ

- 対象の Python は 3.14 です。`requires-python` は `>=3.14,<3.15`、`.python-version` は `3.14` です。3.15 では rez がプラグインを読み込めません。`uv sync` が 3.14 を用意します。
- 最初の `phub` が見本を作ります。`--help` でも作ります。
- パッケージが解決できなくても、環境は保存できます。
- 一覧に無いツールは 1 行のエラーです。一覧にはあるのに実行ファイルが解決結果に無いとき、および `PORTFOLIO_HUB_REZ_TERMINAL_COMMAND` のプログラムが無いときは、`FileNotFoundError` のトレースバックです。Linux で `x-terminal-emulator` が無いときは、この変数を実在するプログラムにします。
- CLI で対象が無いときの文には名前が入ります（`project unknown does not exist`、`environment unknown does not exist in project sample_project`）。HTTP の 404 の文には UUID が入ります。
- `127.0.0.1` と `localhost` 以外の `Host` は、状態 400、本文 `Invalid host header` です。

## 開発するとき

依存のインストールは `uv sync`、テストは `./test.sh` です。カバレッジが 70% を下回ると失敗します。

CI はこれに加えて次を実行します。

- `uv lock --check`
- `python3 .github/scripts/changelog.py`（`CHANGELOG.md` の先頭の版と `pyproject.toml` の版が一致すること）
- `uv audit --preview-features audit`
- `uv run ruff check .`
- `uv run ty check`
- `uv run tach check`
- `uv run tach check-external`
