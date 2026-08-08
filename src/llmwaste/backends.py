# src/llmwaste/backends.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import asyncio
import os
import shutil


@dataclass(frozen=True, slots=True)
class BackendStatus:
    name: str
    executable: str | None
    available: bool


async def _run_checked(argv: list[str]) -> int:
    """Run a subprocess without blocking the event loop."""
    process = await asyncio.create_subprocess_exec(*argv)
    return await process.wait()


def backend_status() -> tuple[BackendStatus, ...]:
    waste = os.environ.get("LLMWASTE_WASTE_BIN") or shutil.which("waste")
    llama = (
        os.environ.get("LLMWASTE_LLAMA_BIN")
        or shutil.which("llama-cli")
        or shutil.which("llama")
    )
    return (
        BackendStatus("waste", waste, waste is not None),
        BackendStatus("llama.cpp", llama, llama is not None),
    )


async def run_waste(
    model_path: Path,
    prompt: str,
    max_tokens: int,
    binary: str | None = None,
) -> int:
    executable = binary or os.environ.get("LLMWASTE_WASTE_BIN") or shutil.which("waste")
    if not executable:
        raise RuntimeError("WASTE executable not found; set LLMWASTE_WASTE_BIN or install waste")
    argv = [executable, "run", str(model_path), prompt, "-n", str(max_tokens)]
    return await _run_checked(argv)


async def run_llama_cpp(
    model_path: Path,
    prompt: str,
    max_tokens: int,
    threads: int | None = None,
    binary: str | None = None,
) -> int:
    executable = (
        binary
        or os.environ.get("LLMWASTE_LLAMA_BIN")
        or shutil.which("llama-cli")
        or shutil.which("llama")
    )
    if not executable:
        raise RuntimeError("llama.cpp executable not found; set LLMWASTE_LLAMA_BIN")
    argv = [executable, "-m", str(model_path), "-p", prompt, "-n", str(max_tokens)]
    if threads:
        argv.extend(["-t", str(threads)])
    return await _run_checked(argv)
