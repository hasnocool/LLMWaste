# src/llmwaste/models.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

Role = Literal["coding", "general", "fallback"]
Backend = Literal["waste", "llama.cpp"]
Status = Literal["ready", "experimental", "planned"]


@dataclass(frozen=True, slots=True)
class ModelSpec:
    key: str
    repo: str
    role: Role
    backend: Backend
    status: Status
    total_params_b: float
    active_params_b: float
    estimated_disk_gib: float
    minimum_ram_gib: float
    preferred_ram_gib: float
    description: str

    @property
    def active_fraction(self) -> float:
        return self.active_params_b / self.total_params_b

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["active_fraction"] = round(self.active_fraction, 4)
        return data


MODEL_CATALOG: tuple[ModelSpec, ...] = (
    ModelSpec(
        key="kimi-linear-48b-a3b-instruct",
        repo="moonshotai/Kimi-Linear-48B-A3B-Instruct",
        role="general",
        backend="waste",
        status="ready",
        total_params_b=48.0,
        active_params_b=3.0,
        estimated_disk_gib=19.0,
        minimum_ram_gib=1.28,
        preferred_ram_gib=10.0,
        description=(
            "Primary WASTE-style target: sparse 48B MoE with about 3B active "
            "parameters per token and a compact linear-attention state."
        ),
    ),
    ModelSpec(
        key="qwen3-coder-30b-a3b-instruct",
        repo="Qwen/Qwen3-Coder-30B-A3B-Instruct",
        role="coding",
        backend="llama.cpp",
        status="experimental",
        total_params_b=30.5,
        active_params_b=3.3,
        estimated_disk_gib=18.0,
        minimum_ram_gib=8.0,
        preferred_ram_gib=14.0,
        description=(
            "Best coding-oriented sparse target for the laptop. Runs through "
            "llama.cpp today; native expert-streaming adapter is a project goal."
        ),
    ),
    ModelSpec(
        key="qwen3-30b-a3b",
        repo="Qwen/Qwen3-30B-A3B",
        role="general",
        backend="llama.cpp",
        status="experimental",
        total_params_b=30.5,
        active_params_b=3.3,
        estimated_disk_gib=18.0,
        minimum_ram_gib=8.0,
        preferred_ram_gib=14.0,
        description=(
            "General-purpose sparse MoE target. Useful for validating a future "
            "Qwen3-MoE streaming adapter independently of coding tuning."
        ),
    ),
    ModelSpec(
        key="qwen3-8b",
        repo="Qwen/Qwen3-8B",
        role="fallback",
        backend="llama.cpp",
        status="ready",
        total_params_b=8.2,
        active_params_b=8.2,
        estimated_disk_gib=5.5,
        minimum_ram_gib=7.0,
        preferred_ram_gib=10.0,
        description=(
            "Dense fallback for fast local work when SSD streaming would be a "
            "net loss or the larger model is unavailable."
        ),
    ),
)


def get_model(key: str) -> ModelSpec:
    for model in MODEL_CATALOG:
        if model.key == key:
            return model
    raise KeyError(f"unknown model: {key}")
