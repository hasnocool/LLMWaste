# src/llmwaste/planner.py
from __future__ import annotations

from dataclasses import dataclass, asdict

from llmwaste.hardware import HardwareProfile
from llmwaste.models import MODEL_CATALOG, ModelSpec


@dataclass(frozen=True, slots=True)
class ModelPlan:
    model: ModelSpec
    score: float
    runnable: bool
    memory_budget_gib: float
    cache_budget_gib: float
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["model"] = self.model.to_dict()
        return data


def safe_memory_budget(profile: HardwareProfile) -> float:
    if profile.ram_gib <= 0:
        return 0.0
    reserve = max(2.0, profile.ram_gib * 0.20)
    return round(max(0.0, profile.ram_gib - reserve), 2)


def _plan_one(profile: HardwareProfile, model: ModelSpec, role: str | None) -> ModelPlan:
    budget = safe_memory_budget(profile)
    notes: list[str] = []
    runnable = profile.ram_gib >= model.minimum_ram_gib

    if profile.root_free_gib < model.estimated_disk_gib + 5.0:
        runnable = False
        notes.append("insufficient free storage with 5 GiB safety margin")

    if model.backend == "waste" and not profile.nvme_present:
        notes.append("WASTE-style streaming strongly prefers internal NVMe")

    cache = max(0.0, min(budget - model.minimum_ram_gib, budget * 0.55))
    score = 0.0
    if runnable:
        score += 40.0
    if role and model.role == role:
        score += 30.0
    elif model.role == "fallback":
        score += 8.0
    if model.active_fraction <= 0.15:
        score += 18.0
    if model.backend == "waste":
        score += 10.0 if profile.nvme_present else -8.0
    if profile.avx2:
        score += 5.0
    if model.preferred_ram_gib <= budget:
        score += 5.0
    else:
        notes.append("below preferred memory budget; expect more cache misses/page pressure")
    if model.status == "experimental":
        score -= 8.0
        notes.append("experimental backend path")
    elif model.status == "planned":
        score -= 30.0
        notes.append("adapter not implemented yet")

    return ModelPlan(
        model=model,
        score=round(score, 2),
        runnable=runnable,
        memory_budget_gib=budget,
        cache_budget_gib=round(cache, 2),
        notes=tuple(notes),
    )


def recommend(profile: HardwareProfile, role: str | None = None) -> list[ModelPlan]:
    plans = [_plan_one(profile, model, role) for model in MODEL_CATALOG]
    return sorted(plans, key=lambda plan: (plan.runnable, plan.score), reverse=True)
