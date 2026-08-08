# scripts/bootstrap_waste.py
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import shutil

UPSTREAM = "https://github.com/sqliteai/waste.git"


async def run(argv: list[str], cwd: Path | None = None) -> int:
    process = await asyncio.create_subprocess_exec(*argv, cwd=cwd)
    return await process.wait()


async def main_async(destination: Path) -> int:
    if shutil.which("git") is None or shutil.which("make") is None:
        raise RuntimeError("git and make are required")

    if destination.exists():
        if not (destination / ".git").exists():
            raise RuntimeError(f"destination exists but is not a git checkout: {destination}")
        if await run(["git", "fetch", "--depth", "1", "origin", "main"], destination) != 0:
            return 1
        if await run(["git", "reset", "--hard", "origin/main"], destination) != 0:
            return 1
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if await run(["git", "clone", "--depth", "1", UPSTREAM, str(destination)]) != 0:
            return 1

    if await run(["make", "-j"], destination) != 0:
        return 1
    if await run(["make", "check"], destination) != 0:
        return 1
    print(destination / "waste")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.home() / ".local" / "share" / "llmwaste" / "waste",
    )
    args = parser.parse_args()
    try:
        return asyncio.run(main_async(args.destination.expanduser().resolve()))
    except RuntimeError as exc:
        print(f"bootstrap_waste: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
