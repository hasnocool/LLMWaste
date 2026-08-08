# scripts/check_governance.py
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r'__version__\s*=\s*"([^"]+)"')
PYPROJECT_RE = re.compile(r'^version\s*=\s*"([^"]+)"$', re.MULTILINE)


def fail(message: str) -> None:
    print(f"governance: {message}", file=sys.stderr)


def main() -> int:
    init_text = (ROOT / "src/llmwaste/__init__.py").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    runtime = VERSION_RE.search(init_text)
    package = PYPROJECT_RE.search(pyproject)
    if not runtime or not package or runtime.group(1) != package.group(1):
        fail("runtime and package versions disagree")
        return 1

    required = ("README.md", "CHANGELOG.md", "TODO.md", "AGENTS.md")
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        fail(f"missing required documentation: {', '.join(missing)}")
        return 1

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if package.group(1) not in changelog:
        fail("CHANGELOG.md does not mention current version")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
