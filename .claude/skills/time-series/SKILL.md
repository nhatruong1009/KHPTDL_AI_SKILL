---
name: time-series
description: Analyze a metric over time - trend, seasonality, anomalies, period-over-period change, and a simple forecast with uncertainty. Use for "how has X changed over time", "is there a trend/seasonality", "any unusual spikes", "forecast X" questions.
argument-hint: <metric and time column>
---

# Time Series Analysis

# When to use
- Trend or growth over weeks/months/years
- Seasonal patterns (by week of term, month, weekday)
- Spotting unusual spikes/drops
- A simple forecast for planning

# Process
1. **Build the series** - parse dates; aggregate the metric to a regular grain (day/week/month); **fill missing periods with 0 or NaN explicitly** (don't let gaps disappear); note relative time fields (e.g. "day from course start").
2. **Describe the trend** - plot it; add a rolling mean; compute period-over-period and first-vs-last change.
3. **Seasonality** - if >= 2 full cycles, decompose (`statsmodels.tsa.seasonal_decompose`) and say whether the seasonal part is strong; otherwise compare averages by period-of-cycle.
4. **Anomalies** - flag points > 3 robust standard deviations from the rolling median; list the top few with dates; check whether they are data issues.
5. **Forecast** (only if asked) - baseline first (last value / seasonal naive / moving average), then a simple model (Holt-Winters `ExponentialSmoothing` or ARIMA). Hold out the last ~20% **in time order**; report MAE/MAPE vs baseline; show the forecast with an interval. Short series -> keep it simple and say so.
6. **Summarize** - direction and size of the trend, seasonality, anomalies, and forecast with uncertainty.

Run with `python` in `outputs/<slug>/analysis.py`.

# Inputs the skill needs
- Required: date/time column, metric column
- Optional: grain, forecast horizon, groups to compare over time

# Output
Line chart (with rolling mean / anomalies marked / forecast band), a period table, and a short summary.
