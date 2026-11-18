"""Reproduce the historical 2025 evaluation; run from any working directory."""
from pathlib import Path
import json
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.nonparametric.smoothers_lowess import lowess
from statsmodels.tsa.arima.model import ARIMA

ROOT = Path(__file__).resolve().parents[1]


def clean_season(frame, season):
    frame = frame.dropna(how="all")
    home = frame[frame["Unnamed: 4"].isna()].copy()
    home["Attendance"] = pd.to_numeric(home["Attendance"], errors="coerce")
    home = home.dropna(subset=["Attendance"])
    home["Attendance"] = home["Attendance"].astype(int)
    dates = home["Date"].astype(str).str.replace(r"\s\(\d+\)", "", regex=True)
    home["Date"] = pd.to_datetime(dates + f" {season}", format="%A %b %d %Y")
    home["DayOfWeek"] = home["Date"].dt.day_name()
    home["Season"] = season
    return home[["Date", "Attendance", "DayOfWeek", "Season"]].reset_index(drop=True)


def main():
    seasons = [clean_season(pd.read_csv(ROOT / "data/raw" / f"yankees_{y}.csv"), y)
               for y in range(2022, 2026)]
    data = pd.concat(seasons, ignore_index=True)
    data["t"] = np.arange(1, len(data) + 1)
    train = data.loc[data.Season < 2025].copy()
    test = data.loc[data.Season == 2025].copy()
    if (len(train), len(test)) != (237, 80):
        raise ValueError("Input counts differ from the original 237/80 evaluation.")
    if not data.Date.is_monotonic_increasing:
        raise ValueError("Home games must be in chronological order.")
    trend = lowess(train.Attendance, train.t, frac=0.15)[:, 1]
    train["Detrended"] = train.Attendance - trend
    weekday = train.groupby("DayOfWeek").Detrended.mean()
    residual = (train.Detrended - train.DayOfWeek.map(weekday)).to_numpy()
    deterministic = trend[-1] + test.DayOfWeek.map(weekday).to_numpy()
    records = []
    predictions = test.copy()
    orders = [(1,0,0),(2,0,0),(3,0,0),(0,0,1),(0,0,2),
              (0,0,3),(1,0,1),(1,0,2),(2,0,1),(2,0,2)]
    for order in orders:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = ARIMA(residual, order=order).fit()
        name = f"ARIMA{order}"
        row = {"model": name, "AIC": float(model.aic), "BIC": float(model.bic),
               "converged": bool(model.mle_retvals.get("converged", False)),
               "warnings": " | ".join(str(w.message) for w in caught)}
        # Only the two historically compared models receive test-set scores.
        if order in [(0,0,1), (2,0,1)]:
            forecast = deterministic + np.asarray(model.forecast(len(test)))
            predictions[name] = forecast
            row["RMSE"] = float(np.sqrt(np.mean((test.Attendance - forecast) ** 2)))
        records.append(row)
    comparison = pd.DataFrame(records).sort_values("AIC")
    scores = {r["model"]: r["RMSE"] for r in records if "RMSE" in r}
    # Additional simple references, not part of the submitted report.
    baselines = {
        "training_mean": np.repeat(train.Attendance.mean(), len(test)),
        "training_weekday_mean": test.DayOfWeek.map(train.groupby("DayOfWeek").Attendance.mean()).to_numpy(),
    }
    for name, forecast in baselines.items():
        predictions[name] = forecast
        scores[name] = float(np.sqrt(np.mean((test.Attendance - forecast) ** 2)))
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    comparison.to_csv(results / "model_comparison.csv", index=False)
    predictions.to_csv(results / "predictions_2025.csv", index=False)
    metrics = {"train_games": len(train), "test_games": len(test), "rmse_attendees": scores}
    (results / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(test.t, test.Attendance, color="#282a27", lw=1.2, label="Actual")
    ax.plot(test.t, predictions["ARIMA(0, 0, 1)"], color="#74805a", lw=2, label="LOWESS + weekday + MA(1)")
    ax.set(xlabel="Home-game event index", ylabel="Reported attendance",
           title="Yankees attendance: historical 2025 evaluation")
    ax.legend(frameon=False)
    fig.tight_layout()
    (ROOT / "figures").mkdir(exist_ok=True)
    fig.savefig(ROOT / "figures/reproduced_forecast.png", dpi=160)
    plt.close(fig)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
