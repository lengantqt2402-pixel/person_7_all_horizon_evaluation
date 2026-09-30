README.md
Person 7 – Forecast Evaluation
1. Overview

This folder contains the out-of-sample evaluation of four models for forecasting the U.S. Treasury yield curve:

Random Walk (RW)
AR
VAR using the Nelson–Siegel factors: Level, Slope and Curvature
VAR+Macro using Level, Slope, Curvature, U.S. inflation and the U.S. policy rate

The evaluation is performed for three Treasury maturities:

1Y (DGS1)
2Y (DGS2)
10Y (DGS10)

and four forecast horizons:

1 month
3 months
6 months
12 months

The evaluation period is January 2024 – December 2025.

2. Folder Structure
person7/
├── code/
│   ├── evaluation.py
│   └── dm_test.py
├── data_all/
│   ├── ar_yield_forecasts_with_actuals_all_horizons.csv
│   ├── us_monthly_master_with_ns.csv
│   ├── us_monthly_observed_yields_2024_2025.csv
│   ├── VAR3_yield_forecasts_all_horizons.csv
│   └── VAR5_yield_forecasts_all_horizons.csv
├── results/
│   ├── all_forecasts_multi_horizon.csv
│   ├── forecast_metrics_multi_horizon.csv
│   ├── forecast_comparison_multi_horizon_wide.csv
│   ├── forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv
│   ├── random_walk_forecasts_all_horizons.csv
│   ├── dm_test_results_all_horizons.csv
│   └── dm_test_VAR_vs_VARMacro_all_horizons.csv
└── README.md
3. Forecast Evaluation Method

The target period is:

2024-01-31 → 2025-12-31

For each forecast horizon h, the forecast origin is:

origin = target date − h months

Only information available up to the forecast origin is used.

For example, for a 3-month forecast:

Origin → t+1 → t+2 → t+3
                    ↑
              forecast evaluated

This procedure is applied to:

h = 1, 3, 6, 12
4. Models
4.1 Random Walk

Random Walk is the benchmark:

ŷ(t+h|t) = y(t)

The yield at the forecast origin is used as the forecast for the future horizon.

4.2 AR

The AR model forecasts the three Nelson–Siegel factors individually:

Level
Slope
Curvature

The AR lag is selected using BIC, with candidate lags from 1 to 6.

For horizons greater than one month, forecasts are generated recursively.

4.3 VAR

The VAR model contains:

Level
Slope
Curvature

The VAR lag is selected using BIC, with maximum lag 6.

For each forecast origin, the model is estimated using information available up to that origin and the forecast corresponding to the required horizon is retained.

4.4 VAR+Macro

The extended VAR model contains:

Level
Slope
Curvature
Inflation
Policy Rate

The lag is selected using BIC. The macro variables are forecast jointly with the yield-curve factors when producing multi-step forecasts.

5. From Factors to Treasury Yields

Forecasted Nelson–Siegel factors are converted into predicted yields for:

1Y, 2Y, 10Y

using the same Nelson–Siegel specification and lambda.

The predicted yields are then compared with observed Treasury yields.

6. Evaluation Metrics
MAE – Mean Absolute Error
MAE = mean(|actual − forecast|)

MAE measures the average absolute forecasting error.

RMSE – Root Mean Squared Error
RMSE = sqrt(mean((actual − forecast)^2))

RMSE gives greater weight to larger errors.

For both measures:

Lower values indicate smaller forecast errors.

7. Diebold–Mariano Test

The Diebold–Mariano (DM) test compares the predictive accuracy of two models.

The loss function is squared error:

Loss = error²

The loss differential is:

dₜ = Loss(model 1) − Loss(model 2)

Therefore:

DM > 0: model 2 has lower average loss than model 1.
DM < 0: model 1 has lower average loss than model 2.

For multi-step forecasts, the implementation uses HAC/Newey–West-style long-run variance with:

max_lag = h − 1

The test is two-sided.

The following model pairs are tested:

RW vs AR
RW vs VAR
RW vs VAR+Macro
AR vs VAR
AR vs VAR+Macro
VAR vs VAR+Macro

across all four horizons and three maturities.

8. Results

The main outputs are stored in results/.

Forecast accuracy

forecast_metrics_multi_horizon.csv

Contains model, horizon, maturity, number of observations, MAE and RMSE.

Wide comparison

forecast_comparison_multi_horizon_wide.csv

Provides a wider comparison across models, horizons and maturities.

VAR vs VAR+Macro

forecast_comparison_VAR_vs_VARMacro_multi_horizon.csv

Provides the direct comparison between VAR and VAR+Macro.

Diebold–Mariano

dm_test_results_all_horizons.csv

Contains DM results for all model pairs.

dm_test_VAR_vs_VARMacro_all_horizons.csv

Contains the specific VAR versus VAR+Macro comparison.

9. Main Empirical Findings

Forecasting performance varies with both forecast horizon and Treasury maturity.

The results do not show a single forecasting performance pattern across:

h = 1, 3, 6, 12

and:

1Y, 2Y, 10Y

In particular, adding inflation and the policy rate to VAR does not produce a uniform improvement in out-of-sample forecast accuracy relative to VAR using only Level, Slope and Curvature.

Most VAR versus VAR+Macro DM comparisons do not show a statistically significant difference at the 5% level. Significant differences occur for the 10-year maturity at:

6-month horizon: DM = -2.6057, p = 0.0092
12-month horizon: DM = -2.3980, p = 0.0165

Because the statistic is defined as:

Loss(VAR) − Loss(VAR+Macro)

the negative statistics indicate lower squared-error loss for VAR than VAR+Macro in these two cases.

At the 12-month horizon and 2-year maturity:

DM = -1.7454
p = 0.0809

which does not reach the 5% significance level.

These results are out-of-sample forecasting evidence and should not be interpreted as evidence of a causal relationship between macroeconomic variables and the yield curve.

10. Reproducibility

Run the forecast evaluation from the person7 folder:

python code/evaluation.py

Then run the Diebold–Mariano tests:

python code/dm_test.py

The scripts read the files in:

data_all/

and save the results to:

results/
11. Important Notes
Evaluation period: January 2024 – December 2025.
Forecast horizons: 1, 3, 6 and 12 months.
Maturities: 1Y, 2Y and 10Y.
VAR+Macro has fewer available observations in some cases because of missing end-of-sample macro-related observations in the original forecast output.
Missing observations are not replaced with zero.
Forecast accuracy is evaluated separately from the dynamic relationship between macro variables and yield-curve factors.
IRF analysis is separate from this forecasting evaluation.
