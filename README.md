# LLMWaste

LLMWaste is a low-RAM local-LLM project for laptops where **NVMe capacity is much larger than RAM**. It borrows the central systems idea demonstrated by SQLiteAI's WASTE—keep the reusable model trunk resident, exploit sparse Mixture-of-Experts routing, and avoid treating every model as if every parameter must stay in memory—but builds a hardware-aware orchestration layer and a path toward additional model adapters.

The initial reference machine is a Ryzen 5 PRO 4650U-class ThinkPad with 16 GiB RAM, AVX2 and internal NVMe storage.

> Project status: v0.1.0 foundation. Kimi-Linear uses the upstream WASTE engine today. Qwen3-MoE targets initially use llama.cpp while a native streaming adapter is developed.

## Why this exists

Dense models and sparse models have different economics. A dense 30B model touches essentially all of its weights for each token; streaming those weights from SSD is usually a bad trade. A sparse 30B or 48B MoE may activate only ~3B parameters per token, making expert-aware storage, cache and prefetch strategies much more attractive.

LLMWaste therefore does three things:

1. Profiles the machine: RAM, available RAM, CPU SIMD capability, storage headroom and NVMe presence.
2. Ranks model/back-end combinations for the machine instead of assuming one runtime fits every model.
3. Provides non-blocking subprocess orchestration for WASTE and llama.cpp while the native multi-architecture streaming engine is built out.

## Current target models

| Model | Role | Total / active | Current backend | Why it matters |
|---|---|---:|---|---|
| Kimi-Linear-48B-A3B-Instruct | general | 48B / ~3B | WASTE | Best current proof that SSD-streamed sparse inference can work on low RAM |
| Qwen3-Coder-30B-A3B-Instruct | coding | 30.5B / ~3.3B | llama.cpp (experimental) | Primary coding target for a future native Qwen3-MoE streaming adapter |
| Qwen3-30B-A3B | general | 30.5B / ~3.3B | llama.cpp (experimental) | General Qwen3-MoE adapter validation target |
| Qwen3-8B | fallback | 8.2B / 8.2B | llama.cpp | Fast dense fallback when streaming is not beneficial |

Model sizes in the catalog are planning estimates rather than universal guarantees; quantization and container format change disk and memory requirements.

## Install

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

For development:

```bash
python -m pip install pytest
pytest
python scripts/check_governance.py
```

## Profile the laptop

```bash
llmwaste hardware
llmwaste plan --role coding
llmwaste plan --role general
```

## Install/check the upstream WASTE backend

The repository does not copy SQLiteAI's implementation. The bootstrap helper obtains the current upstream engine and builds/tests it separately:

```bash
python scripts/bootstrap_waste.py
export LLMWASTE_WASTE_BIN="$HOME/.local/share/llmwaste/waste/waste"
llmwaste doctor
```

The helper uses asynchronous subprocess execution and never runs through a shell.

## Run a WASTE container

```bash
llmwaste run \
  kimi-linear-48b-a3b-instruct \
  ~/models/kimi-linear.waste \
  "Explain why sparse MoE models are attractive on a RAM-limited laptop." \
  -n 256
```

## Run a GGUF through llama.cpp

```bash
export LLMWASTE_LLAMA_BIN=/usr/local/bin/llama-cli

llmwaste run \
  qwen3-coder-30b-a3b-instruct \
  ~/models/qwen3-coder-30b-a3b.gguf \
  "Review this Python architecture for concurrency bugs." \
  --threads 6 \
  -n 256
```

## Architecture direction

```text
OpenCode / CLI / OpenAI-compatible API
                 |
          hardware planner
                 |
       model/backend router
          /             \
   llama.cpp        streaming engine
   dense/fallback      sparse MoE
                         |
                resident shared trunk
                         |
                 authoritative router
                         |
               async expert prefetch
                         |
              bounded RAM expert cache
                         |
                   internal NVMe
```

The future native engine must preserve correctness: prediction may schedule I/O but may not override the model's authoritative router.

## Laptop policy

The reference `configs/thinkpad-l14-gen1.toml` reserves 20% of RAM (3.2 GiB on a 16 GiB machine) for the OS and other applications. Avoid swap-heavy configurations: a larger nominal expert cache can be slower if cache hits become page faults.

## Project documents

- `docs/ARCHITECTURE.md` — engine and adapter boundaries.
- `docs/MODEL_TARGETS.md` — model selection and implementation order.
- `docs/HARDWARE.md` — reference laptop constraints and benchmark methodology.
- `TODO.md` — prioritized engineering backlog.
- `AGENTS.md` — repository rules for coding agents.

## Upstream inspiration and attribution

LLMWaste is an independent project inspired by the architecture and published measurements of [SQLiteAI/WASTE](https://github.com/sqliteai/waste). WASTE is Apache-2.0 licensed. This repository currently interoperates with an independently installed upstream WASTE binary instead of vendoring its source.

## License

Apache-2.0. See `LICENSE`.
