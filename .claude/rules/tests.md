---
paths:
  - "tests/**/*.py"
---

# テスト

- 観察可能な振る舞いを中心にテストする。内部の実装は直接テストしない。
- 名前は `test_<動作>_<対象>_<条件>_<結果>` にする。条件と結果は、必要なときだけ付ける（例：`test_rename_project`、`test_rename_unknown_project_fails`、`test_delete_unknown_project_is_not_found`）。
