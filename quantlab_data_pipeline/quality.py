from __future__ import annotations

import logging
from typing import Dict, List, Optional

import pandas as pd

from .paths import final_data_path

logger = logging.getLogger(__name__)


def _load_final(path: Optional[str] = None) -> pd.DataFrame:
    target = final_data_path() if path is None else path
    return pd.read_parquet(target)


def run_quality_checks(path: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Run basic quality checks on the final long-format dataset.
    Returns a dictionary of issues by category.
    """
    df = _load_final(path)
    issues: Dict[str, List[str]] = {"missing": [], "consistency": [], "bounds": []}

    missing = df[df["Value"].isna()]
    if not missing.empty:
        issues["missing"].append(f"Missing values: {len(missing)} rows")

    price_metrics = ["open", "high", "low", "close", "adjusted_close"]
    price = df[df["Metric_Name"].isin(price_metrics)]
    if not price.empty:
        wide = price.pivot_table(index=["Ticker", "Date"], columns="Metric_Name", values="Value", aggfunc="first")
        if {"open", "high", "low", "close"}.issubset(wide.columns):
            bad_open_high = wide[wide["open"] > wide["high"]]
            bad_low_close = wide[wide["low"] > wide["close"]]
            if not bad_open_high.empty:
                issues["consistency"].append(f"open>high rows: {len(bad_open_high)}")
            if not bad_low_close.empty:
                issues["consistency"].append(f"low>close rows: {len(bad_low_close)}")

    price_like = df[df["Metric_Name"].isin(price_metrics + ["volume"])]
    negative = price_like[price_like["Value"] < 0]
    if not negative.empty:
        issues["bounds"].append(f"Negative price/volume values: {len(negative)} rows")

    if not any(issues.values()):
        logger.info("Quality checks passed with no issues detected.")
    else:
        logger.warning("Quality checks found issues: %s", issues)
    return issues
