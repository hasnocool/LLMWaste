# src/llmwaste/hardware.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import os
import platform
import shutil

GIB = 1024 ** 3


@dataclass(frozen=True, slots=True)
class HardwareProfile:
    platform: str
    machine: str
    cpu: str
    logical_cpus: int
    ram_gib: float
    available_ram_gib: float
    avx2: bool
    avx512: bool
    nvme_present: bool
    root_free_gib: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _read_meminfo(path: Path = Path("/proc/meminfo")) -> tuple[float, float]:
    if not path.exists():
        return 0.0, 0.0
    fields: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition(":")
        if not value:
            continue
        amount = value.strip().split()[0]
        if amount.isdigit():
            fields[key] = int(amount) * 1024
    total = fields.get("MemTotal", 0) / GIB
    available = fields.get("MemAvailable", fields.get("MemFree", 0)) / GIB
    return total, available


def _cpu_flags(path: Path = Path("/proc/cpuinfo")) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    for line in text.splitlines():
        if line.startswith("flags") or line.startswith("features"):
            _, _, flags = line.partition(":")
            return set(flags.split())
    return set()


def _cpu_name(path: Path = Path("/proc/cpuinfo")) -> str:
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name"):
                return line.partition(":")[2].strip()
    return platform.processor() or "unknown"


def _has_nvme(sys_block: Path = Path("/sys/block")) -> bool:
    try:
        return any(p.name.startswith("nvme") for p in sys_block.iterdir())
    except OSError:
        return False


def detect_hardware() -> HardwareProfile:
    total, available = _read_meminfo()
    flags = _cpu_flags()
    root_free = shutil.disk_usage(Path.cwd()).free / GIB
    return HardwareProfile(
        platform=platform.system().lower(),
        machine=platform.machine().lower(),
        cpu=_cpu_name(),
        logical_cpus=os.cpu_count() or 1,
        ram_gib=round(total, 2),
        available_ram_gib=round(available, 2),
        avx2="avx2" in flags,
        avx512=any(flag.startswith("avx512") for flag in flags),
        nvme_present=_has_nvme(),
        root_free_gib=round(root_free, 2),
    )
