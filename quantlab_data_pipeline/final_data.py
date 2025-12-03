from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

import pandas as pd

from .paths import final_data_path


def get_final_data(
    tickers: Optional[Iterable[str]] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> pd.DataFrame:
    """
    Public interface to load the final long-format dataset with optional filtering.
    """
    df = pd.read_parquet(final_data_path())
    if tickers:
        tickers_set = set(tickers)
        df = df[df["Ticker"].isin(tickers_set)]
    if start_date:
        df = df[df["Date"] >= pd.to_datetime(start_date).date()]
    if end_date:
        df = df[df["Date"] <= pd.to_datetime(end_date).date()]
    return df.reset_index(drop=True)
