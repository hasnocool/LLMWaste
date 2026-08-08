# src/llmwaste/cli.py
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys

from llmwaste import __version__
from llmwaste.backends import backend_status, run_llama_cpp, run_waste
from llmwaste.hardware import detect_hardware
from llmwaste.models import MODEL_CATALOG, get_model
from llmwaste.planner import recommend


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llmwaste",
        description="Plan and run local models around RAM, NVMe and sparse-model economics.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("hardware", help="show detected hardware")

    models = sub.add_parser("models", help="list configured model targets")
    models.add_argument("--json", action="store_true")

    plan = sub.add_parser("plan", help="rank models for this machine")
    plan.add_argument("--role", choices=("coding", "general", "fallback"))
    plan.add_argument("--json", action="store_true")

    sub.add_parser("doctor", help="check local backends")

    run = sub.add_parser("run", help="run a local model through its configured backend")
    run.add_argument("model", help="catalog key")
    run.add_argument("model_path", type=Path, help="local WASTE container or GGUF path")
    run.add_argument("prompt")
    run.add_argument("-n", "--max-tokens", type=int, default=256)
    run.add_argument("--threads", type=int)
    return parser


def _print_plan(role: str | None, as_json: bool) -> int:
    profile = detect_hardware()
    plans = recommend(profile, role)
    if as_json:
        print(json.dumps([plan.to_dict() for plan in plans], indent=2))
        return 0

    print(f"hardware: {profile.cpu} | {profile.ram_gib:.2f} GiB RAM | NVMe={profile.nvme_present}")
    for index, plan in enumerate(plans, 1):
        state = "RUN" if plan.runnable else "NO"
        print(
            f"{index}. [{state}] {plan.model.key} score={plan.score:.1f} "
            f"backend={plan.model.backend} budget={plan.memory_budget_gib:.2f} GiB"
        )
        for note in plan.notes:
            print(f"   - {note}")
    return 0


async def _run_model(args: argparse.Namespace) -> int:
    spec = get_model(args.model)
    if not args.model_path.exists():
        raise FileNotFoundError(args.model_path)
    if spec.backend == "waste":
        return await run_waste(args.model_path, args.prompt, args.max_tokens)
    return await run_llama_cpp(
        args.model_path,
        args.prompt,
        args.max_tokens,
        threads=args.threads,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "hardware":
            print(json.dumps(detect_hardware().to_dict(), indent=2))
            return 0
        if args.command == "models":
            if args.json:
                print(json.dumps([m.to_dict() for m in MODEL_CATALOG], indent=2))
            else:
                for model in MODEL_CATALOG:
                    print(
                        f"{model.key:34} {model.backend:9} {model.status:12} "
                        f"{model.total_params_b:g}B/{model.active_params_b:g}B active"
                    )
            return 0
        if args.command == "plan":
            return _print_plan(args.role, args.json)
        if args.command == "doctor":
            failed = False
            for item in backend_status():
                state = "ok" if item.available else "missing"
                print(f"{item.name}: {state} ({item.executable or 'not found'})")
                failed |= not item.available
            return 1 if failed else 0
        if args.command == "run":
            return asyncio.run(_run_model(args))
    except (KeyError, RuntimeError, FileNotFoundError, ValueError) as exc:
        print(f"llmwaste: {exc}", file=sys.stderr)
        return 2
    return 0
