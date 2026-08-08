# tests/test_hardware.py
from pathlib import Path

from llmwaste.hardware import _cpu_flags, _read_meminfo


def test_meminfo_parser(tmp_path: Path) -> None:
    path = tmp_path / "meminfo"
    path.write_text("MemTotal:       16777216 kB\nMemAvailable:   12582912 kB\n", encoding="utf-8")
    total, available = _read_meminfo(path)
    assert total == 16.0
    assert available == 12.0


def test_cpu_flags_parser(tmp_path: Path) -> None:
    path = tmp_path / "cpuinfo"
    path.write_text("flags : sse4_2 avx avx2 fma\n", encoding="utf-8")
    assert "avx2" in _cpu_flags(path)
