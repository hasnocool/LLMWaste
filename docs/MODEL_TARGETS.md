# Model targets

## Selection rule

A model benefits from a WASTE-style runtime when its total parameter set is much larger than its per-token active working set and the shared model state can remain resident without pushing the OS into swap.

## Tier 1 — Kimi-Linear-48B-A3B-Instruct

Purpose: prove the storage/cache path on the reference ThinkPad before generalizing the native engine.

- ~48B total parameters.
- ~3B activated parameters.
- hybrid linear-attention architecture.
- upstream WASTE already documents a compact converted container and low minimum-RAM operation.

This is the first model to benchmark because it removes architecture-development risk from the initial hardware experiment.

## Tier 2 — Qwen3-Coder-30B-A3B-Instruct

Purpose: primary local coding model.

- ~30.5B total parameters.
- ~3.3B activated parameters.
- MoE architecture.
- Apache-2.0 model license.

v0.1 treats llama.cpp as the compatibility backend. The native roadmap is to implement a Qwen3-MoE adapter that can store experts independently, route authoritatively and prefetch the next layer without changing model output.

## Tier 3 — Qwen3-30B-A3B

Purpose: isolate Qwen3-MoE engine work from coding fine-tuning behavior.

This model should share almost all of the native adapter with the coder model and therefore becomes a useful correctness/benchmark cross-check.

## Dense fallback — Qwen3-8B

Dense models generally do not benefit from expert streaming because nearly all weights participate in every token. A smaller resident model remains important for autocomplete, offline fallback and tasks where latency matters more than maximum capability.

## Explicit non-goal

Do not try to SSD-stream arbitrary dense 30B+ checkpoints through the native expert path. Supporting an architecture does not mean every model using that architecture benefits from storage streaming.
