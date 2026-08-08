# Reference hardware

## Baseline target

The initial profile is a ThinkPad L14 Gen 1 AMD-class laptop:

- Ryzen 5 PRO 4650U-class CPU;
- 6 cores / 12 threads;
- AVX2/FMA CPU path;
- 16 GiB system RAM baseline;
- internal NVMe storage;
- integrated graphics are not assumed to provide a useful large-model VRAM pool.

The software auto-detects the actual machine at runtime; these values are a benchmark target, not hard-coded requirements.

## Memory policy

On a 16 GiB system, the default planning rule reserves at least 20% of physical RAM for the operating system and other processes. This produces a 12.8 GiB process planning ceiling before model-specific floors and caches are considered.

Do not chase cache-hit percentage past the point where the kernel starts paging the process. Major page faults and end-to-end tokens/sec are more important than hit rate.

## Storage policy

Sparse expert streaming is storage-bound enough that the model bank should live on internal NVMe. External USB storage is useful for archives and source checkpoints but should not be assumed adequate for active expert reads.

## CPU policy

- Prefer AVX2 kernels on the reference Ryzen CPU.
- Use the physical-core count as an initial compute-thread baseline when SMT hurts cache behavior.
- Separate I/O workers from compute workers in the future native engine.
- Benchmark thread counts rather than assuming all 12 logical CPUs is optimal.

## Power-aware future work

A laptop/off-grid profile can later add a power budget to model routing. Lower-power modes may favor a resident small model rather than high-I/O expert streaming even when the larger model is technically runnable.
