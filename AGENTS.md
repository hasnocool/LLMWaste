# Agent instructions

## Project goal

LLMWaste exists to make capable sparse local models practical on RAM-limited laptops by using hardware-aware model selection and, eventually, model-correct expert streaming from NVMe.

## Required engineering rules

1. Preserve model correctness. I/O prediction may schedule reads; it may not replace authoritative routing.
2. Prefer sparse models when total parameters greatly exceed active parameters. Do not force SSD streaming onto dense models when it cannot reduce the per-token weight working set.
3. Async Python code must use non-blocking, concurrency-safe operations. Use `asyncio.create_subprocess_exec` for subprocesses and never call blocking subprocess APIs from an async path.
4. Native blocking file I/O belongs in dedicated I/O workers, not an async coordination thread.
5. Protect OS headroom. More cache is not automatically better if it creates page faults or swap.
6. Benchmark before and after performance changes and record negative results.
7. Add tests for planner, container, adapter and correctness changes.
8. Use semantic versioning.
9. When behavior changes, update `CHANGELOG.md`, `README.md`, `TODO.md` and affected docs in the same PR.
10. Keep package/runtime versions synchronized; `scripts/check_governance.py` must remain green.
11. Never silently replace measured values with estimates. Label estimates clearly.
12. Keep model-specific semantics behind adapters rather than scattering architecture checks throughout storage/cache code.

## Pull requests

A PR should explain the measurement or user problem, implementation, correctness impact, performance evidence and documentation changes. Performance work without reproducible measurements is incomplete.
