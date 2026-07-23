"""Small, dependency-light helpers for durable claim evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / ".openresearch" / "artifacts"
FIXED_COMMAND = "uv run --frozen python repro/src/verify_pld.py"


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def runtime_metadata(seeds: list[int] | None = None) -> dict[str, Any]:
    return {
        "command": FIXED_COMMAND,
        "git_sha": git_sha(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "deterministic_seeds": seeds or [],
        "environment_lock": "uv.lock",
        "author_implementation": {
            "url": "https://github.com/moshenfeld/PLD_accounting.git",
            "commit": "11ed6d14e846de658465fb91309f574ab933cdc9",
            "version": "0.5.0",
        },
    }


def manifest(directory: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return rows
