# Portfolio draft

## Yankees Attendance Forecasting

Explored how historical attendance and weekday patterns can support forecasting
for Yankees home games. Used LOWESS decomposition and ARMA modeling, comparing
forecasts across 80 games in the 2025 evaluation period after fitting on
2022-2024 data.

The MA(1) approach achieved an RMSE of approximately 3,024 attendees. Added
baseline comparisons show about 7% lower error than a training weekday-average
forecast. The evaluation also identified opportunities for stronger validation,
schedule-aware forecasts, and external predictors.

**Methods:** time series analysis, LOWESS, weekday effects, ARMA, ACF/PACF,
spectral analysis, RMSE.

**Tools:** Python, pandas, NumPy, statsmodels, Matplotlib.

**Suggested image:** `figures/reproduced_forecast.png`.

**GitHub link:** https://github.com/IanKimura/Yankees_Attendance_Forecasting

**Attribution:** original course analysis by Ian Kimura; portable tooling and
additional baseline comparisons prepared subsequently. Confirm individual
contributions before adding more detailed ownership statements.
