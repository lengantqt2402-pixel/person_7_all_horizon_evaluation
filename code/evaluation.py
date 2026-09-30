import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# PERSON 7 - MULTI-HORIZON FORECAST EVALUATION
# Models: Random Walk, AR, VAR, VAR + Macro
# Horizons: 1, 3, 6, 12 months
# Maturities: 1Y, 2Y, 10Y
# Metrics: MAE, RMSE
# ============================================================

# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_all"
RESULT_DIR = BASE_DIR / "results"

RESULT_DIR.mkdir(exist_ok=True)

AR_FILE = DATA_DIR / "ar_yield_forecasts_with_actuals_all_horizons.csv"
YIELD_MASTER_FILE = DATA_DIR / "us_monthly_master_with_ns.csv"
ACTUAL_FILE = DATA_DIR / "us_monthly_observed_yields_2024_2025.csv"
VAR_FILE = DATA_DIR / "VAR3_yield_forecasts_all_horizons.csv"
VAR_MACRO_FILE = DATA_DIR / "VAR5_yield_forecasts_all_horizons.csv"

START_DATE = pd.Timestamp("2024-01-31")
END_DATE = pd.Timestamp("2025-12-31")

HORIZONS = [1, 3, 6, 12]
MATURITIES = [12, 24, 120]
MATURITY_MAP = {
    12: "DGS1",
    24: "DGS2",
    120: "DGS10",
}

MODEL_FILES = {
    "AR": AR_FILE,
    "VAR": VAR_FILE,
    "VAR+Macro": VAR_MACRO_FILE,
}

print("\n" + "=" * 80)
print("PERSON 7 - MULTI-HORIZON FORECAST EVALUATION")
print("=" * 80)
print("Base directory:", BASE_DIR)
print("Data directory:", DATA_DIR)
print("Result directory:", RESULT_DIR)
print("Target period:", START_DATE.date(), "->", END_DATE.date())
print("Horizons:", HORIZONS)
print("Maturities: 1Y, 2Y, 10Y")


# ------------------------------------------------------------
# 2. CHECK INPUT FILES
# ------------------------------------------------------------

required_files = {
    "AR": AR_FILE,
    "Yield master": YIELD_MASTER_FILE,
    "Observed actual": ACTUAL_FILE,
    "VAR3": VAR_FILE,
    "VAR5 + Macro": VAR_MACRO_FILE,
}

print("\n" + "=" * 80)
print("1. CHECK INPUT FILES")
print("=" * 80)

for name, path in required_files.items():
    if not path.exists():
        raise FileNotFoundError(
            f"Khong tim thay file {name}: {path}"
        )
    print(f"[OK] {name}: {path.name}")


# ------------------------------------------------------------
# 3. HELPERS
# ------------------------------------------------------------

def standardize_forecast_file(df, model_name):
    """
    Convert an AR/VAR forecast file to a common long format:
    origin_date, target_date, horizon_months,
    maturity_months, maturity_series,
    forecast_yield_pct, model
    """
    required = [
        "origin_date",
        "target_date",
        "horizon_months",
        "maturity_months",
        "maturity_series",
        "forecast_yield_pct",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"{model_name}: thieu cot {missing}"
        )

    out = df[required].copy()

    # R may export Date objects to CSV as numeric day counts
    # (days since 1970-01-01). Pandas would otherwise interpret
    # these numbers as nanoseconds, producing dates around 1970.
    def parse_date_column(series):
        numeric = pd.to_numeric(series, errors="coerce")
        numeric_mask = series.notna() & numeric.notna()

        parsed = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")

        if numeric_mask.any():
            parsed.loc[numeric_mask] = pd.to_datetime(
                numeric.loc[numeric_mask],
                unit="D",
                origin="unix",
                errors="coerce",
            )

        if (~numeric_mask).any():
            parsed.loc[~numeric_mask] = pd.to_datetime(
                series.loc[~numeric_mask],
                errors="coerce",
            )

        return parsed

    out["origin_date"] = parse_date_column(out["origin_date"])
    out["target_date"] = parse_date_column(out["target_date"])
    out["horizon_months"] = pd.to_numeric(
        out["horizon_months"], errors="coerce"
    ).astype("Int64")
    out["maturity_months"] = pd.to_numeric(
        out["maturity_months"], errors="coerce"
    ).astype("Int64")
    out["forecast_yield_pct"] = pd.to_numeric(
        out["forecast_yield_pct"], errors="coerce"
    )

    out["model"] = model_name

    # Diagnostic output: helps verify date/horizon/maturity normalization.
    print(f"\n--- DEBUG {model_name} ---")
    print("Raw rows:", len(df))
    print("target_date:", out["target_date"].min(), "->", out["target_date"].max())
    print("horizon_months unique:", sorted(out["horizon_months"].dropna().unique().tolist()))
    print("maturity_months unique:", sorted(out["maturity_months"].dropna().unique().tolist()))
    print("Rows inside target date:", out["target_date"].between(START_DATE, END_DATE).sum())
    print("Rows with valid horizon:", out["horizon_months"].isin(HORIZONS).sum())
    print("Rows with valid maturity:", out["maturity_months"].isin(MATURITIES).sum())

    out = out[
        out["target_date"].between(START_DATE, END_DATE)
        & out["horizon_months"].isin(HORIZONS)
        & out["maturity_months"].isin(MATURITIES)
    ].copy()

    print("Rows AFTER filter:", len(out))

    return out


def calculate_metrics(df):
    """Calculate N, MAE and RMSE by model x horizon x maturity."""
    valid = df.dropna(
        subset=["forecast_yield_pct", "actual_yield_pct"]
    ).copy()

    valid["error"] = (
        valid["forecast_yield_pct"]
        - valid["actual_yield_pct"]
    )
    valid["absolute_error"] = valid["error"].abs()
    valid["squared_error"] = valid["error"] ** 2

    metrics = (
        valid.groupby(
            [
                "model",
                "horizon_months",
                "maturity_months",
                "maturity_series",
            ],
            as_index=False,
        )
        .agg(
            N=("error", "count"),
            MAE=("absolute_error", "mean"),
            MSE=("squared_error", "mean"),
        )
    )

    metrics["RMSE"] = np.sqrt(metrics["MSE"])
    metrics = metrics.drop(columns=["MSE"])

    return metrics


# ------------------------------------------------------------
# 4. READ ACTUAL YIELDS
# ------------------------------------------------------------

actual = pd.read_csv(ACTUAL_FILE)
actual["target_date"] = pd.to_datetime(actual["target_date"])

required_actual = [
    "target_date",
    "DGS1",
    "DGS2",
    "DGS10",
]

missing_actual = [
    c for c in required_actual if c not in actual.columns
]

if missing_actual:
    raise ValueError(
        f"Observed actual file thieu cot: {missing_actual}"
    )

actual = actual[
    actual["target_date"].between(START_DATE, END_DATE)
].copy()

if actual["target_date"].duplicated().any():
    raise ValueError(
        "Observed actual co target_date bi trung."
    )

if len(actual) != 24:
    raise ValueError(
        f"Expected 24 actual target months, got {len(actual)}."
    )

print("\n" + "=" * 80)
print("2. OBSERVED ACTUAL YIELDS")
print("=" * 80)
print("Rows:", len(actual))
print(
    "Target:",
    actual["target_date"].min().date(),
    "->",
    actual["target_date"].max().date(),
)


# ------------------------------------------------------------
# 5. READ YIELD MASTER FOR RANDOM WALK
# ------------------------------------------------------------

yield_master = pd.read_csv(YIELD_MASTER_FILE)
yield_master["date"] = pd.to_datetime(yield_master["date"])

required_master = [
    "date",
    "DGS1",
    "DGS2",
    "DGS10",
]

missing_master = [
    c for c in required_master
    if c not in yield_master.columns
]

if missing_master:
    raise ValueError(
        f"Yield master thieu cot: {missing_master}"
    )

yield_master = (
    yield_master[required_master]
    .drop_duplicates(subset=["date"])
    .sort_values("date")
    .reset_index(drop=True)
)

print("\n" + "=" * 80)
print("3. YIELD MASTER FOR RANDOM WALK")
print("=" * 80)
print("Rows:", len(yield_master))
print(
    "Date:",
    yield_master["date"].min().date(),
    "->",
    yield_master["date"].max().date(),
)


# ------------------------------------------------------------
# 6. CREATE RANDOM WALK FOR ALL HORIZONS
# ------------------------------------------------------------
#
# For every target month and horizon h:
#   origin = target month shifted back by h months
#   RW forecast = yield observed at origin
#
# The monthly master file may have a missing month (Oct 2025).
# Therefore:
#   1) use the master yield file whenever the origin exists;
#   2) use the common observed-yield file as a fallback only for
#      a missing origin month.
#
# This is valid for Random Walk because the fallback month is
# strictly BEFORE the target month.
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("4. BUILD RANDOM WALK - ALL HORIZONS")
print("=" * 80)

# Build a single monthly yield source.
# Start from the master and fill only missing dates from observed actuals.
master_long = yield_master[
    ["date", "DGS1", "DGS2", "DGS10"]
].copy()

observed_source = actual[
    ["target_date", "DGS1", "DGS2", "DGS10"]
].rename(
    columns={"target_date": "date"}
).copy()

yield_source = pd.concat(
    [master_long, observed_source],
    ignore_index=True,
)

# If the same month exists in both sources, keep the master value.
# Missing months in master are filled by the observed source.
yield_source = (
    yield_source
    .sort_values(["date"])
    .drop_duplicates(subset=["date"], keep="first")
    .sort_values("date")
    .reset_index(drop=True)
)

# The monthly master uses the last available TRADING day of each
# month (for example 2024-01-29), while the evaluation target uses
# calendar month-end (for example 2024-02-29). Therefore we must
# match Random Walk origins by YEAR-MONTH, not by exact date.
yield_source["year_month"] = yield_source["date"].dt.to_period("M")

# If both master and observed fallback contain the same month,
# the master observation is kept. For a missing month in master
# (e.g. Oct 2025), the observed-yield file supplies the month.
yield_source = (
    yield_source
    .sort_values(["year_month", "date"])
    .drop_duplicates(subset=["year_month"], keep="first")
    .sort_values("year_month")
    .reset_index(drop=True)
)

yield_source_by_period = {
    row["year_month"]: row
    for _, row in yield_source.iterrows()
}

# The 24 evaluation target months come from the common observed-yield file.
target_dates = actual["target_date"].sort_values().tolist()

rw_rows = []

for target_date in target_dates:

    target_period = target_date.to_period("M")

    for h in HORIZONS:

        # Origin is h MONTHS before the target month.
        origin_period = target_period - h

        if origin_period not in yield_source_by_period:
            raise ValueError(
                f"Khong co yield tai origin month={origin_period} "
                f"cho target={target_date.date()}, h={h}."
            )

        origin_row = yield_source_by_period[origin_period]
        origin_date = origin_row["date"]

        for maturity_months, series in MATURITY_MAP.items():
            rw_rows.append(
                {
                    "origin_date": origin_date,
                    "target_date": target_date,
                    "horizon_months": h,
                    "maturity_months": maturity_months,
                    "maturity_series": series,
                    "forecast_yield_pct": origin_row[series],
                    "model": "Random Walk",
                }
            )

rw = pd.DataFrame(rw_rows)

print("RW rows:", len(rw))

expected_rw = len(target_dates) * len(HORIZONS) * len(MATURITIES)

if len(rw) != expected_rw:
    raise ValueError(
        f"RW expected {expected_rw} rows, got {len(rw)}."
    )

print(
    "RW origin range:",
    rw["origin_date"].min().date(),
    "->",
    rw["origin_date"].max().date(),
)

# Show which RW origin dates were supplied by the observed-yield
# fallback rather than the master file.
master_periods = set(
    master_long["date"].dt.to_period("M")
)
rw_origin_periods = set(
    rw["origin_date"].dt.to_period("M")
)
fallback_origins = sorted(
    rw_origin_periods - master_periods
)

if fallback_origins:
    print(
        "RW fallback origin dates from observed actuals:",
        [str(d) for d in fallback_origins]
    )
else:
    print("RW fallback origin dates: none")

# ------------------------------------------------------------
# 7. ATTACH ACTUALS TO RANDOM WALK
# ------------------------------------------------------------

actual_long = actual.melt(
    id_vars=["target_date"],
    value_vars=["DGS1", "DGS2", "DGS10"],
    var_name="maturity_series",
    value_name="actual_yield_pct",
)

actual_long["maturity_months"] = (
    actual_long["maturity_series"]
    .map({"DGS1": 12, "DGS2": 24, "DGS10": 120})
)

rw = rw.merge(
    actual_long,
    on=["target_date", "maturity_series", "maturity_months"],
    how="left",
    validate="many_to_one",
)

if rw["actual_yield_pct"].isna().any():
    raise ValueError("RW co actual yield bi thieu.")

print(
    "RW missing forecasts:",
    rw["forecast_yield_pct"].isna().sum(),
)
print(
    "RW missing actuals:",
    rw["actual_yield_pct"].isna().sum(),
)


# ------------------------------------------------------------
# 8. READ AR / VAR / VAR+MACRO
# ------------------------------------------------------------

forecast_frames = []

print("\n" + "=" * 80)
print("5. READ MODEL FORECASTS")
print("=" * 80)

for model_name, path in MODEL_FILES.items():
    raw = pd.read_csv(path)
    df = standardize_forecast_file(raw, model_name)

    # Actuals are deliberately attached from the common observed
    # yield file below, so every model is evaluated against the
    # same actual series.
    forecast_frames.append(df)

    print(
        f"{model_name}: {len(df)} rows | "
        f"horizons={sorted(df['horizon_months'].dropna().unique().tolist())}"
    )

forecasts = pd.concat(
    forecast_frames,
    ignore_index=True,
)

# Check duplicates at model/horizon/target/maturity level.
dup_cols = [
    "model",
    "horizon_months",
    "target_date",
    "maturity_months",
]

duplicates = forecasts.duplicated(subset=dup_cols, keep=False)

if duplicates.any():
    print("\nDuplicate forecast rows:")
    print(
        forecasts.loc[
            duplicates,
            dup_cols + ["forecast_yield_pct"],
        ].sort_values(dup_cols).head(30)
    )
    raise ValueError(
        "Co forecast bi trung trong model/horizon/target/maturity."
    )


# ------------------------------------------------------------
# 9. ATTACH COMMON ACTUALS TO MODEL FORECASTS
# ------------------------------------------------------------

forecasts = forecasts.merge(
    actual_long,
    on=["target_date", "maturity_series", "maturity_months"],
    how="left",
    validate="many_to_one",
)

if forecasts["actual_yield_pct"].isna().any():
    bad = forecasts[
        forecasts["actual_yield_pct"].isna()
    ]
    raise ValueError(
        "Co model forecast khong match duoc actual yield.\n"
        + str(
            bad[
                [
                    "model",
                    "horizon_months",
                    "target_date",
                    "maturity_months",
                    "maturity_series",
                ]
            ].head(20)
        )
    )


# ------------------------------------------------------------
# 10. COMBINE ALL FOUR MODELS
# ------------------------------------------------------------

all_forecasts = pd.concat(
    [rw, forecasts],
    ignore_index=True,
)

all_forecasts["error"] = (
    all_forecasts["forecast_yield_pct"]
    - all_forecasts["actual_yield_pct"]
)

all_forecasts["absolute_error"] = all_forecasts["error"].abs()
all_forecasts["squared_error"] = all_forecasts["error"] ** 2

all_forecasts = all_forecasts.sort_values(
    [
        "horizon_months",
        "maturity_months",
        "target_date",
        "model",
    ]
).reset_index(drop=True)


# ------------------------------------------------------------
# 11. OBSERVATION COUNTS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("6. OBSERVATION COUNTS")
print("=" * 80)

counts = (
    all_forecasts.groupby(
        ["model", "horizon_months", "maturity_months"],
        as_index=False,
    )
    .size()
    .rename(columns={"size": "N"})
)

print(counts.to_string(index=False))

print("\nExpected full count per model/horizon/maturity = 24.")
print(
    "VAR+Macro h=1 may have fewer observations because "
    "the original VAR5 forecast has missing end-of-sample macro data."
)


# ------------------------------------------------------------
# 12. METRICS
# ------------------------------------------------------------

metrics = calculate_metrics(all_forecasts)

metrics = metrics.sort_values(
    [
        "horizon_months",
        "maturity_months",
        "model",
    ]
).reset_index(drop=True)

print("\n" + "=" * 80)
print("7. MAE / RMSE - ALL MODELS")
print("=" * 80)

print(metrics.round(6).to_string(index=False))


# ------------------------------------------------------------
# 13. DIRECT VAR VS VAR+MACRO TABLE
# ------------------------------------------------------------

var_vs_macro = metrics[
    metrics["model"].isin(["VAR", "VAR+Macro"])
].copy()

var_vs_macro = var_vs_macro.sort_values(
    [
        "horizon_months",
        "maturity_months",
        "model",
    ]
).reset_index(drop=True)

print("\n" + "=" * 80)
print("8. VAR VS VAR+MACRO")
print("=" * 80)

print(var_vs_macro.round(6).to_string(index=False))


# ------------------------------------------------------------
# 14. WIDE COMPARISON TABLE
# ------------------------------------------------------------

comparison_wide = metrics.pivot_table(
    index=[
        "horizon_months",
        "maturity_months",
        "maturity_series",
    ],
    columns="model",
    values=["N", "MAE", "RMSE"],
    aggfunc="first",
)

comparison_wide = comparison_wide.reset_index()

# Flatten multi-index column names.
flat_cols = []
for col in comparison_wide.columns:
    if isinstance(col, tuple):
        if col[1] == "":
            flat_cols.append(col[0])
        else:
            flat_cols.append(f"{col[0]}_{col[1].replace(' ', '_').replace('+', 'plus')}")
    else:
        flat_cols.append(col)

comparison_wide.columns = flat_cols


# ------------------------------------------------------------
# 15. SAVE RESULTS
# ------------------------------------------------------------

all_forecasts.to_csv(
    RESULT_DIR / "all_forecasts_multi_horizon.csv",
    index=False,
)

metrics.to_csv(
    RESULT_DIR / "forecast_metrics_multi_horizon.csv",
    index=False,
)

comparison_wide.to_csv(
    RESULT_DIR / "forecast_comparison_multi_horizon_wide.csv",
    index=False,
)

var_vs_macro.to_csv(
    RESULT_DIR / "forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv",
    index=False,
)

rw.to_csv(
    RESULT_DIR / "random_walk_forecasts_all_horizons.csv",
    index=False,
)


# ------------------------------------------------------------
# 16. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("HOAN THANH PERSON 7 - MULTI-HORIZON EVALUATION")
print("=" * 80)

print("Da tao:")
print("- random_walk_forecasts_all_horizons.csv")
print("- all_forecasts_multi_horizon.csv")
print("- forecast_metrics_multi_horizon.csv")
print("- forecast_comparison_multi_horizon_wide.csv")
print("- forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv")

print("\nMetrics dimensions:")
print("4 models x 4 horizons x 3 maturities")
print("= 48 model-horizon-maturity combinations (where forecasts exist).")

print("\nKet qua duoc luu tai:")
print(RESULT_DIR)

print("\n[OK] MAE/RMSE multi-horizon da hoan tat.")
