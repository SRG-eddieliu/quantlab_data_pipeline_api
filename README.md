# quantlab_data_pipeline_api

Automated pipeline for ingesting, transforming, and serving financial and economic time-series data using WRDS constituents and Alpha Vantage MCP tools. Data is written to external Parquet stores (raw and final long format), with logging and quality checks.

## Layout
- Repository root: code and configs.
- External data root (sibling to repo): `../data/`
  - Raw landing zone: `../data/data-raw/`
  - Final analytical table: `../data/final/final_long.parquet`

## Credentials
Create `credentials.yml` at the repo root (gitignored) with Alpha Vantage and WRDS credentials:
```yaml
alphavantage_api: "<free-key>"
alphavantage_api_paid: "<paid-key>"
wrds_username: "<wrds-username>"
wrds_password: "<wrds-password>"
```

## mapping notes
Constituents are pulled from `crsp_a_indexes.dsp500list_v2` using `permno`, `mbrstartdt`, `mbrenddt` and mapped to tickers via `crsp.msenames` date-overlap joins.

## Key functions
- `run_ingestion(date_start=None, date_end=None, ...)`: pulls constituents from WRDS, fetches Alpha Vantage via REST (MCP only for analytics if used), saves raw Parquet per ticker/endpoint. If dates not provided, uses `config/datalist.yml` defaults.
- `transform_raw_to_final()`: builds domain-specific final tables in `../data/final/`: `price_daily.parquet`, `price_weekly.parquet`, `fundamentals.parquet`, `economic_indicators.parquet`, `company_overview.parquet`.
- `run_quality_checks(dataset="price_daily")`: basic completeness/consistency/bounds checks on price datasets.
- `get_final_data(dataset="price_daily", tickers=None, start_date=None, end_date=None)`: read and filter a chosen final dataset.
- `export_fundamental_failures()`: scans `fundamentals.parquet` for “invalid api call” rows and writes a CSV with suggested API calls to re-run (default: `data/final/failures_temp.csv`).
- `export_company_overview_failures()`: scans `company_overview.parquet` for “invalid api call” rows and writes a CSV with suggested API calls to re-run (default: `data/final/company_overview_failures.csv`).
- `export_all_failures()`: scans all raw Parquets for “invalid api call” rows and writes a single CSV (`data/final/failures_all.csv`) with ticker/function/API URL to rerun.
- `refetch_failures(failures_csv)`: re-fetch failed fundamentals/company overview calls listed in a CSV (ticker/function) and overwrite raw Parquets; rerun `transform_raw_to_final()` afterward.

## API usage notes
- Time series (`TIME_SERIES_DAILY_ADJUSTED`, `TIME_SERIES_WEEKLY_ADJUSTED`) are fetched via the Alpha Vantage REST API with `datatype=csv` and `outputsize=full` for full history.
- Fundamentals, listings/calendars, and economic endpoints use the REST API with their function names (e.g., `OVERVIEW`, `INCOME_STATEMENT`, `LISTING_STATUS`, etc.)
- MCP is used for tool discovery
- Ingestion writes a unique ticker list (`wrds_sp500_unique_tickers.parquet`) and uses it to drive API calls; the daily constituent Parquet is still written for auditing.
- Alpha Vantage source:https://www.alphavantage.co/documentation/
- Ingestion has a `resume` flag (default True): it skips endpoints where a non-empty Parquet already exists, so you can rerun after timeouts without re-fetching everything. 
      run_ingestion(date_start=date(2024, 1, 2), date_end=date(2025, 1, 2), sleep_seconds=12.0, use_paid_key=True, resume = False)

## MCP configuration
The repo includes `.vscode/mcp.json` pointing to the Alpha Vantage MCP HTTP endpoint. Ensure the API key in that file matches your credentials.yml.

## Considerations
- WRDS crsp_a_indexes.dsp500list_v2 (annual) used to create SP500 constituents annual list. Daily constituents were then expanded based on annual information which introduce look-ahead/survivorship bias. With WRDS daily access these bias can be removed
