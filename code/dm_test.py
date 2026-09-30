import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import norm

# ============================================================
# PERSON 7 - DIEBOLD-MARIANO TEST - MULTI HORIZON
# ============================================================

# ============================================================
# 1. DUONG DAN FILE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Dung data_all vi day la bo forecast multi-horizon da chuan bi
DATA_DIR = BASE_DIR / "data_all"
RESULT_DIR = BASE_DIR / "results"

DATA_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# ============================================================
# 2. FILE DU LIEU DAU VAO
# ============================================================

AR_FILE = DATA_DIR / "ar_yield_forecasts_with_actuals_all_horizons.csv"
VAR_FILE = DATA_DIR / "VAR3_yield_forecasts_all_horizons.csv"
VAR_MACRO_FILE = DATA_DIR / "VAR5_yield_forecasts_all_horizons.csv"

# Random Walk da duoc tao va kiem tra trong evaluation.py
RW_FILE = RESULT_DIR / "random_walk_forecasts_all_horizons.csv"

# Co the dung file tong hop do evaluation.py tao.
ALL_FORECASTS_FILE = RESULT_DIR / "all_forecasts_multi_horizon.csv"

# ============================================================
# 3. THIET LAP DANH GIA
# ============================================================

START_DATE = pd.Timestamp("2024-01-31")
END_DATE = pd.Timestamp("2025-12-31")

MATURITIES = [12, 24, 120]
HORIZONS = [1, 3, 6, 12]

# ============================================================
# 4. KIEM TRA FILE DAU VAO
# ============================================================

input_files = {
    "AR": AR_FILE,
    "VAR": VAR_FILE,
    "VAR + Macro": VAR_MACRO_FILE,
    "Random Walk": RW_FILE,
}

print("\n" + "=" * 80)
print("PERSON 7 - DIEBOLD-MARIANO TEST - MULTI-HORIZON")
print("=" * 80)
print("Data directory:", DATA_DIR)
print("Result directory:", RESULT_DIR)
print("Target period:", START_DATE.date(), "->", END_DATE.date())
print("Horizons:", HORIZONS)
print("Maturities: 1Y, 2Y, 10Y")

for name, file_path in input_files.items():
    if not file_path.exists():
        raise FileNotFoundError(
            f"Khong tim thay file {name}: {file_path}"
        )
    print(f"[OK] {name}: {file_path.name}")

# ============================================================
# 5. HAM CHUAN HOA FORECAST FILE
# ============================================================

def parse_mixed_date(series):
    """
    Chuan hoa ngay thang trong cac file forecast.

    Mot so file VAR/VAR+Macro duoc xuat tu R co the luu
    Date thanh so ngay tinh tu 1970-01-01 (vi du 19753).
    AR/RW co the luu Date duoi dang chuoi YYYY-MM-DD.

    Ham nay xu ly ca hai dang:
        - Date string -> datetime
        - So nguyen -> 1970-01-01 + so ngay
    """
    s = pd.Series(series).copy()

    numeric = pd.to_numeric(s, errors="coerce")
    parsed = pd.to_datetime(s, errors="coerce")

    numeric_mask = numeric.notna()

    if numeric_mask.any():
        parsed.loc[numeric_mask] = (
            pd.Timestamp("1970-01-01")
            + pd.to_timedelta(
                numeric.loc[numeric_mask],
                unit="D"
            )
        )

    return parsed


def read_forecast_file(file_path, model_name):
    """
    Doc forecast file va chuan hoa cac cot:
        target_date
        horizon_months
        maturity_months
        maturity_series
        actual_yield_pct
        forecast_yield_pct
    """
    df = pd.read_csv(file_path)

    required = [
        "target_date",
        "horizon_months",
        "maturity_months",
        "maturity_series",
        "forecast_yield_pct",
        "actual_yield_pct",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"{model_name} thieu cot: {missing}\n"
            f"Cot hien co: {df.columns.tolist()}"
        )

    # Quan trong: xu ly ca Date string va Date dang so tu R
    df["target_date"] = parse_mixed_date(df["target_date"])

    df["horizon_months"] = pd.to_numeric(
        df["horizon_months"], errors="coerce"
    )

    df["maturity_months"] = pd.to_numeric(
        df["maturity_months"], errors="coerce"
    )

    print(
        f"\\n--- DEBUG {model_name} ---"
    )
    print("Raw rows:", len(df))
    print(
        "target_date:",
        df["target_date"].min(),
        "->",
        df["target_date"].max()
    )
    print(
        "horizon_months unique:",
        sorted(
            df["horizon_months"]
            .dropna()
            .unique()
            .tolist()
        )
    )
    print(
        "maturity_months unique:",
        sorted(
            df["maturity_months"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    df = df[
        df["target_date"].between(START_DATE, END_DATE)
        & df["horizon_months"].isin(HORIZONS)
        & df["maturity_months"].isin(MATURITIES)
    ].copy()

    print("Rows AFTER filter:", len(df))

    df["model"] = model_name

    # Chi giu cac cot can thiet
    return df[
        [
            "target_date",
            "horizon_months",
            "maturity_months",
            "maturity_series",
            "actual_yield_pct",
            "forecast_yield_pct",
            "model",
        ]
    ].copy()


# ============================================================
# 6. DOC 3 MODEL
# ============================================================

print("\n" + "=" * 80)
print("1. DOC DU LIEU FORECAST")
print("=" * 80)

ar = read_forecast_file(AR_FILE, "AR")
var = read_forecast_file(VAR_FILE, "VAR")
var_macro = read_forecast_file(VAR_MACRO_FILE, "VAR+Macro")

print("AR:", len(ar), "rows")
print("VAR:", len(var), "rows")
print("VAR+Macro:", len(var_macro), "rows")

# ============================================================
# 7. DOC RANDOM WALK
# ============================================================

rw = read_forecast_file(RW_FILE, "RW")

print("Random Walk:", len(rw), "rows")

# ============================================================
# 8. GHEP 4 MODEL
# ============================================================

all_models = pd.concat(
    [rw, ar, var, var_macro],
    ignore_index=True
)

print("\nSo dong sau khi concat:", len(all_models))

# ============================================================
# 9. KIEM TRA SO LUONG QUAN SAT
# ============================================================

print("\n" + "=" * 80)
print("2. OBSERVATION COUNTS")
print("=" * 80)

counts = (
    all_models
    .groupby(
        ["model", "horizon_months", "maturity_months"]
    )
    .size()
    .reset_index(name="N")
    .sort_values(
        ["horizon_months", "maturity_months", "model"]
    )
)

print(counts.to_string(index=False))

# ============================================================
# 10. HAM DIEBOLD-MARIANO TEST
# ============================================================

def diebold_mariano_test(
    actual,
    forecast_1,
    forecast_2,
    h=1
):
    """
    Diebold-Mariano test.

    H0:
        Hai mo hinh co do chinh xac du bao bang nhau.

    Loss:
        Squared Error.

    Loss differential:
        d_t = e1_t^2 - e2_t^2

    DM > 0:
        model_2 co loss trung binh nho hon model_1.

    DM < 0:
        model_1 co loss trung binh nho hon model_2.

    Với forecast horizon h > 1:
        dung Newey-West HAC voi max_lag = h - 1.
    """

    actual = np.asarray(actual, dtype=float)
    forecast_1 = np.asarray(forecast_1, dtype=float)
    forecast_2 = np.asarray(forecast_2, dtype=float)

    valid = (
        np.isfinite(actual)
        & np.isfinite(forecast_1)
        & np.isfinite(forecast_2)
    )

    actual = actual[valid]
    forecast_1 = forecast_1[valid]
    forecast_2 = forecast_2[valid]

    n = len(actual)

    if n < 5:
        return np.nan, np.nan, n

    error_1 = actual - forecast_1
    error_2 = actual - forecast_2

    loss_1 = error_1 ** 2
    loss_2 = error_2 ** 2

    d = loss_1 - loss_2
    mean_d = np.mean(d)

    d_centered = d - mean_d

    # Gamma 0
    gamma_0 = np.mean(d_centered * d_centered)

    # Multi-step forecast:
    # horizon 1 -> lag 0
    # horizon 3 -> lag 2
    # horizon 6 -> lag 5
    # horizon 12 -> lag 11
    max_lag = max(h - 1, 0)

    long_run_variance = gamma_0

    for lag in range(1, max_lag + 1):
        covariance = np.mean(
            d_centered[lag:] * d_centered[:-lag]
        )

        weight = 1 - lag / (max_lag + 1)

        long_run_variance += (
            2 * weight * covariance
        )

    if long_run_variance <= 0:
        return np.nan, np.nan, n

    dm_stat = (
        mean_d
        / np.sqrt(long_run_variance / n)
    )

    p_value = 2 * (
        1 - norm.cdf(abs(dm_stat))
    )

    return dm_stat, p_value, n


# ============================================================
# 11. CAC CAP MO HINH
# ============================================================

MODEL_PAIRS = [
    ("RW", "AR"),
    ("RW", "VAR"),
    ("RW", "VAR+Macro"),
    ("AR", "VAR"),
    ("AR", "VAR+Macro"),
    ("VAR", "VAR+Macro"),
]

# ============================================================
# 12. CHAY DM TEST
# ============================================================

results = []

print("\n" + "=" * 80)
print("3. DIEBOLD-MARIANO TEST - ALL HORIZONS")
print("=" * 80)

for horizon in HORIZONS:

    print("\n" + "#" * 80)
    print(f"HORIZON = {horizon} MONTH(S)")
    print("#" * 80)

    horizon_data = all_models[
        all_models["horizon_months"] == horizon
    ].copy()

    for maturity in MATURITIES:

        maturity_data = horizon_data[
            horizon_data["maturity_months"] == maturity
        ].copy()

        if maturity_data.empty:
            print(
                f"\nMATURITY {maturity}: khong co du lieu"
            )
            continue

        maturity_name = (
            maturity_data["maturity_series"]
            .dropna()
            .iloc[0]
        )

        print("\n" + "-" * 80)
        print(
            f"MATURITY: {maturity_name} "
            f"({maturity} months)"
        )
        print("-" * 80)

        # ----------------------------------------------------
        # Tach tung model
        # ----------------------------------------------------

        model_tables = {}

        for model in ["RW", "AR", "VAR", "VAR+Macro"]:

            tmp = maturity_data[
                maturity_data["model"] == model
            ][
                [
                    "target_date",
                    "actual_yield_pct",
                    "forecast_yield_pct",
                ]
            ].copy()

            tmp = tmp.rename(
                columns={
                    "forecast_yield_pct": model
                }
            )

            model_tables[model] = tmp

        # ----------------------------------------------------
        # Chay tung cap model
        # ----------------------------------------------------

        for model_1, model_2 in MODEL_PAIRS:

            # Merge theo target_date thay vi merge ca actual.
            # Actual cua cac model duoc kiem tra lai sau khi merge.
            pair = model_tables[model_1].merge(
                model_tables[model_2],
                on=["target_date"],
                how="inner",
                suffixes=("_1", "_2"),
            )

            # Loai missing forecast.
            pair = pair.dropna(
                subset=[model_1, model_2]
            ).sort_values("target_date")

            # Actual co the nam o cot _1/_2.
            # Dung actual cua model_1 lam actual chung va kiem tra
            # sai lech neu hai file co actual khac nhau.
            actual_1 = pair["actual_yield_pct_1"].to_numpy(
                dtype=float
            )
            actual_2 = pair["actual_yield_pct_2"].to_numpy(
                dtype=float
            )

            actual_valid = (
                np.isfinite(actual_1)
                & np.isfinite(actual_2)
            )

            if np.any(
                np.abs(
                    actual_1[actual_valid]
                    - actual_2[actual_valid]
                ) > 1e-8
            ):
                raise ValueError(
                    f"Actual cua {model_1} va {model_2} "
                    f"khong giong nhau tai horizon={horizon}, "
                    f"maturity={maturity}."
                )

            actual = actual_1

            forecast_1 = pair[
                model_1
            ].values

            forecast_2 = pair[
                model_2
            ].values

            dm_stat, p_value, n = (
                diebold_mariano_test(
                    actual,
                    forecast_1,
                    forecast_2,
                    h=horizon
                )
            )

            results.append(
                {
                    "horizon_months": horizon,
                    "maturity_months": maturity,
                    "maturity_series": maturity_name,
                    "model_1": model_1,
                    "model_2": model_2,
                    "N": n,
                    "DM_stat": dm_stat,
                    "p_value": p_value,
                }
            )

            print(
                f"{model_1:10s} vs "
                f"{model_2:10s} | "
                f"N = {n:2d} | "
                f"DM = {dm_stat:8.4f} | "
                f"p-value = {p_value:8.4f}"
            )


# ============================================================
# 13. TAO BANG KET QUA
# ============================================================

dm_results = pd.DataFrame(results)

# ============================================================
# 14. THEM DIEN GIAI P-VALUE
# ============================================================

def interpret_p_value(p):

    if pd.isna(p):
        return "Khong tinh duoc"

    if p < 0.01:
        return "Co y nghia o muc 1%"

    elif p < 0.05:
        return "Co y nghia o muc 5%"

    elif p < 0.10:
        return "Co y nghia o muc 10%"

    else:
        return "Khong co y nghia thong ke"


dm_results["interpretation"] = (
    dm_results["p_value"]
    .apply(interpret_p_value)
)

# ============================================================
# 15. IN BANG KET QUA
# ============================================================

print("\n" + "=" * 80)
print("4. BANG KET QUA DM TEST")
print("=" * 80)

print(
    dm_results.round(6).to_string(
        index=False
    )
)

# ============================================================
# 16. RIENG VAR VS VAR + MACRO
# ============================================================

var_macro_result = dm_results[
    (dm_results["model_1"] == "VAR")
    & (dm_results["model_2"] == "VAR+Macro")
].copy()

print("\n" + "=" * 80)
print("5. DM TEST QUAN TRONG NHAT: VAR VS VAR+MACRO")
print("=" * 80)

print(
    var_macro_result.round(6).to_string(
        index=False
    )
)

# ============================================================
# 17. LUU KET QUA
# ============================================================

dm_results.to_csv(
    RESULT_DIR / "dm_test_results_all_horizons.csv",
    index=False
)

var_macro_result.to_csv(
    RESULT_DIR / "dm_test_VAR_vs_VARMacro_all_horizons.csv",
    index=False
)

# ============================================================
# 18. TOM TAT SO LUONG KET QUA
# ============================================================

print("\n" + "=" * 80)
print("6. TOM TAT")
print("=" * 80)

print(
    "So dong DM test:",
    len(dm_results)
)

print(
    "Expected:",
    len(HORIZONS)
    * len(MATURITIES)
    * len(MODEL_PAIRS)
)

print(
    "\nDa tao:"
)

print(
    "- dm_test_results_all_horizons.csv"
)

print(
    "- dm_test_VAR_vs_VARMacro_all_horizons.csv"
)

print(
    "\nKet qua da duoc luu tai:"
)

print(RESULT_DIR)

print("\n[OK] DM TEST MULTI-HORIZON HOAN TAT.")
