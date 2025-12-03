from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from .paths import final_data_path, raw_data_dir

logger = logging.getLogger(__name__)


def _infer_date_column(df: pd.DataFrame) -> Optional[str]:
    for col in ["date", "timestamp", "datetime"]:
        if col in df.columns:
            return col
    return None


def _wide_to_long(df: pd.DataFrame, date_col: str, ticker: str, data_source: str) -> pd.DataFrame:
    value_cols = [c for c in df.columns if c != date_col]
    melted = df.melt(id_vars=[date_col], value_vars=value_cols, var_name="Metric_Name", value_name="Value")
    melted = melted.rename(columns={date_col: "Date"})
    melted["Ticker"] = ticker
    melted["Data_Source"] = data_source
    melted["Date"] = pd.to_datetime(melted["Date"]).dt.date
    return melted[["Ticker", "Date", "Data_Source", "Metric_Name", "Value"]]


def _extract_meta(path: Path) -> Tuple[str, str]:
    data_source = path.parent.name
    ticker = path.stem
    return ticker, data_source


def transform_raw_to_final() -> Path:
    """
    Load all raw parquet files, normalize to long format, and write final dataset.
    """
    raw_dir = raw_data_dir()
    paths = list(raw_dir.rglob("*.parquet"))
    if not paths:
        raise FileNotFoundError(f"No parquet files found under {raw_dir}")

    frames = []
    for path in paths:
        df = pd.read_parquet(path)
        if df.empty:
            continue
        date_col = _infer_date_column(df)
        ticker, data_source = _extract_meta(path)
        if not date_col:
            # No date column; skip or keep with None dates
            df["Date"] = pd.NaT
            date_col = "Date"
        frames.append(_wide_to_long(df, date_col, ticker, data_source))

    if not frames:
        raise ValueError("No data to transform.")

    final_df = pd.concat(frames, ignore_index=True)
    final_df["Value"] = pd.to_numeric(final_df["Value"], errors="ignore")

    target = final_data_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_parquet(target, index=False)
    logger.info("Wrote final long-format dataset with %d rows to %s", len(final_df), target)
    return target
