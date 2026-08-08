# tests/test_planner.py
from llmwaste.hardware import HardwareProfile
from llmwaste.planner import recommend, safe_memory_budget


def profile() -> HardwareProfile:
    return HardwareProfile(
        platform="linux",
        machine="x86_64",
        cpu="AMD Ryzen 5 PRO 4650U",
        logical_cpus=12,
        ram_gib=16.0,
        available_ram_gib=12.0,
        avx2=True,
        avx512=False,
        nvme_present=True,
        root_free_gib=100.0,
    )


def test_safe_budget_reserves_os_memory() -> None:
    assert safe_memory_budget(profile()) == 12.8


def test_general_prefers_kimi_linear() -> None:
    plans = recommend(profile(), "general")
    assert plans[0].model.key == "kimi-linear-48b-a3b-instruct"
    assert plans[0].runnable is True


def test_coding_prefers_qwen_coder() -> None:
    plans = recommend(profile(), "coding")
    assert plans[0].model.key == "qwen3-coder-30b-a3b-instruct"
