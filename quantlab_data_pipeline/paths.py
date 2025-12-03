from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return repository root inferred from this file location."""
    return Path(__file__).resolve().parents[1]


def data_root() -> Path:
    """
    Return external data root (sibling to repo), e.g., quant-lab/data/.
    Defaults to ../data relative to repo root.
    """
    return repo_root().parent / "data"


def raw_data_dir() -> Path:
    """Landing zone for raw parquet outputs."""
    return data_root() / "data-raw"


def final_data_path() -> Path:
    """Single merged analytical table location."""
    return data_root() / "final" / "final_long.parquet"
