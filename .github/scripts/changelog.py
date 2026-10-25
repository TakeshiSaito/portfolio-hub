import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the latest version in CHANGELOG.md after checking that pyproject.toml has the same version.")
    parser.add_argument("--notes", type=Path, help="write the changes of that version to this file")
    arguments = parser.parse_args()
    version, notes = _latest_release((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
    project_version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    if version != project_version:
        print(f"CHANGELOG.md has {version} but pyproject.toml has {project_version}", file=sys.stderr)
        return 1
    if arguments.notes:
        arguments.notes.write_text(notes, encoding="utf-8")
    print(version)
    return 0


def _latest_release(changelog: str) -> tuple[str, str]:
    heading, _, body = re.split(r"^## ", changelog, flags=re.MULTILINE)[1].partition("\n")
    match = re.fullmatch(r"\[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}", heading.strip())
    if match is None:
        raise SystemExit(f"the first section of CHANGELOG.md is not a version: {heading.strip()}")
    return match.group(1), body.strip() + "\n"


if __name__ == "__main__":
    sys.exit(main())
