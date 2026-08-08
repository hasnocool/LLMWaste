# Architecture

## Design goals

LLMWaste is optimized for machines where storage capacity greatly exceeds memory capacity. The engine should spend RAM on the tensors that are reused heavily and on a bounded hot expert set, not on keeping an entire sparse model resident.

Correctness is non-negotiable: prefetch prediction may alter when bytes are read, but never which experts the authoritative model router selects.

## v0.1 execution layers

```text
CLI
 |
 +-- hardware detection
 |
 +-- model catalog / planner
 |
 +-- backend adapter
      +-- WASTE executable (Kimi family)
      +-- llama.cpp executable (GGUF fallback / Qwen experimentation)
```

The subprocess adapters are asynchronous via `asyncio.create_subprocess_exec`, avoiding thread-blocking calls in async paths and avoiding shell interpolation.

## Native streaming milestone

The planned native layer separates model semantics from storage/cache policy.

```text
ModelAdapter
  - metadata
  - tokenizer contract
  - tensor names/layout
  - router semantics
  - attention/recurrent state
  - expert tensor geometry

StreamingRuntime
  - aligned file reads
  - bounded expert cache
  - admission / eviction policy
  - lookahead I/O scheduling
  - cache telemetry
  - memory pressure guard
  - CPU backend

HardwarePolicy
  - RAM budget
  - page-fault pressure
  - NVMe throughput/latency
  - SIMD capability
  - thermal/power constraints
```

## Adapter order

1. Kimi-Linear 48B A3B: validate WASTE-compatible sparse streaming economics on the reference laptop.
2. Qwen3-Coder 30B A3B: coding-first MoE target.
3. Qwen3 30B A3B: general-purpose Qwen3-MoE validation.
4. Additional sparse architectures only after the adapter API is stable.

## Storage policy

- Prefer one aligned read per expert record.
- Keep shared/trunk tensors resident when feasible.
- Cache only within a process budget that leaves OS headroom.
- Measure major page faults; do not optimize hit rate in isolation.
- Use internal NVMe for expert banks whenever possible.
- Do not introduce blocking file I/O on an async orchestration thread; native compute/I/O workers own blocking syscalls.

## Benchmark contract

Every performance claim should record:

- exact model and quantization/container revision;
- git commit;
- CPU and SIMD path;
- RAM and configured budget;
- storage device and filesystem;
- prompt/context length;
- cold/warm cache state;
- tokens/sec;
- bytes read/token;
- cache hit rate;
- major page faults;
- process RSS and system memory pressure.
