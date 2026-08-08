# TODO

## v0.1.x — validate the reference laptop

- [ ] Run Kimi-Linear WASTE container on the Ryzen/16 GiB reference machine.
- [ ] Capture NVMe model, sequential/random read performance and filesystem.
- [ ] Benchmark 1, 2, 3, 4, 6 and 8 GiB effective expert-cache headroom.
- [ ] Record major page faults, RSS, bytes/token, cache hit rate and tokens/sec.
- [ ] Add benchmark JSON schema and append-only results directory.
- [ ] Add `llmwaste benchmark` command.
- [ ] Add OpenAI-compatible proxy endpoint for OpenCode integration.

## v0.2.0 — Qwen3-MoE adapter groundwork

- [ ] Define stable `ModelAdapter` metadata contract.
- [ ] Map Qwen3-MoE expert/router tensor names and shapes.
- [ ] Implement converter prototype that splits shared tensors from per-expert records.
- [ ] Implement synthetic expert-bank container tests.
- [ ] Add aligned pread worker pool and bounded cache prototype.
- [ ] Add authoritative routing correctness oracle against a reference runtime.
- [ ] Add Qwen3-Coder-30B-A3B adapter.
- [ ] Add Qwen3-30B-A3B adapter using the same implementation.

## v0.3.0 — performance engine

- [ ] AVX2 expert kernels for the reference Ryzen CPU.
- [ ] Lookahead expert prefetch that never overrides the authoritative router.
- [ ] Cache admission policy using frequency, recency and read cost.
- [ ] Page-fault-aware automatic memory-budget tuner.
- [ ] Direct-I/O experiment with aligned buffers; keep only if measurements win.
- [ ] Persistent conversation state and prompt-prefix reuse.
- [ ] Speculative decoding with a resident draft model.

## Later

- [ ] Vulkan/AMD iGPU experiments only after CPU/NVMe baseline is measured.
- [ ] Power-aware routing policy for battery/off-grid operation.
- [ ] Integration adapter for OpencodeSmart.
- [ ] Automatic choice between resident llama.cpp and sparse streaming backend.
