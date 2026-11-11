# Household electricity use, Dec 2006 – Nov 2010: trend, seasonality, anomalies, and December 2010 forecast

## Answer

- **Trend:** Use is essentially flat to slightly declining. Same-period totals (1 Jan – 26 Nov) fell from 8,355 kWh (2007) to 8,068 kWh (2010), about −1.2% a year. Full calendar years fell from 9,707 kWh (2007) to 9,369 kWh (2009), about −1.7% a year. A trend model that controls for season and weekday gives +0.9% a year, so the sign of the trend depends on method. Treat it as flat within about ±1% a year.
- **Seasonality:** Strong and predictable. Mean daily use is 35.1 kWh in January, bottoms at 13.7 kWh in August, and rises to 34.1 kWh in December. Weekends run about 20% above weekdays (Sat 29.6, Sun 28.9, Mon–Fri 23.5–25.9 kWh/day).
- **Unusual periods:**
  - **August 2008** is an abnormal low: 6.6 kWh/day against 14–18 kWh/day in the other Augusts (2007, 2009, and 2010, which is partly gap-affected). Weeks starting 10, 17, 24 and 31 August 2008 are all flagged, with |z| between 4.7 and 9.4. There is no matching data gap, so this looks like a real drop in use, consistent with the household being away. The data cannot confirm the cause.
  - **Data gaps:** 1.25% of minutes (25,979) are missing, in 71 runs. Six runs last a day or more. The longest is 17–22 Aug 2010 (5.0 days), followed by 25–28 Sep 2010 (3.6 days). Twenty days have under 50% coverage.
  - **Other abnormal weeks:** 13 weeks in total are flagged, and every one is *below* the expected pattern. None are spikes.
- **December 2010 forecast:** about **1,050 kWh** (mean 1,046; median 1,052), with a 90% range of **878 – 1,196 kWh**. A simple cross-check gives 994 kWh, so a rounded range of roughly **880 – 1,200 kWh** is reasonable.

## Evidence

| Item | Value |
|---|---|
| Calendar-year totals (gap-adjusted) | 2007: 9,707 · 2008: 9,418 · 2009: 9,369 kWh |
| Same period (1 Jan – 26 Nov) | 2007: 8,355 · 2008: 8,318 · 2009: 8,243 · 2010: 8,068 kWh |
| Mean kWh/day by month | Jan 35.1 · Feb 31.2 · Mar 29.6 · Apr 25.2 · May 24.7 · Jun 21.8 · Jul 16.8 · Aug 13.7 · Sep 23.4 · Oct 27.3 · Nov 31.0 · Dec 34.1 |
| Mean kWh/day by weekday | Mon 23.9 · Tue 25.5 · Wed 25.9 · Thu 23.5 · Fri 24.8 · Sat 29.6 · Sun 28.9 |
| December totals (actual) | 2007: 1,210 · 2008: 949 · 2009: 1,015 kWh |

**Forecast method.** The model fits log daily kWh on 1,403 complete days (2007-01-01 to 2010-11-26). Its terms are a linear trend, three annual Fourier harmonics, and weekday dummies. The 90% interval comes from 4,000 simulations. Each draws the coefficients from their estimated distribution and adds 7-day block-bootstrapped residuals.

**Backtest (1-month-ahead, 28 months, Jan 2008 – Oct 2010):**
- Overall: mean absolute error 16.7%, and the 90% interval covered 79% of months. The early-2008 forecasts had only about one year of training, and August 2008 was unforeseeable.
- From January 2009 on (16 months, at least two years of training): mean absolute error 6.5%, the 90% interval covered 94% of months, and errors ranged from −17% to +7%. December 2008 was off by +14% and December 2009 by +3.5%.

## Method

1. Loaded the minute-level file (2,075,259 rows, 1 Dec 2006 – 26 Nov 2010, `;` separated, `?` for missing). No duplicate timestamps were found.
2. Energy: `Global_active_power` (kW, average over each minute) ÷ 60 gives kWh per minute, summed to days. Only the active power of the main meter is used; sub-metering and reactive power are not included.
3. Gap handling: each day's available minutes are scaled up to a full day. Days with under 50% coverage are excluded from the adjusted series. The longest gaps (5 and 3.6 days) therefore rely on the average of the remaining minutes in those days and are approximate.
4. Trend and seasonality from the daily model and the monthly, weekly and weekday summaries.
5. Abnormal weeks: each week's mean residual against the model's expected value. Flagged where the robust z-score (MAD) exceeds 3.

## Caveats

- **The December 2010 total is a forecast.** The data ends on 26 November 2010, so 27–30 November are also unobserved.
- The forecast assumes no structural change in the household. The 2008 episode shows that abrupt changes in occupancy are not predictable from the data.
- The model's own interval is narrower than its backtest error before 2009, so the wider 880 – 1,200 kWh range is the safer one to quote.
- Partial months (Dec 2006, Nov 2010, and months with gaps) are flagged in `monthly.csv`. Compare calendar years only on usable days or on the same-period totals.
- These are observational patterns. They do not show what caused the changes in use.

## Files

- `analysis.py` reproduces every number here. Run it from the project root.
- `summary.json` holds every value quoted above. `run_log.txt` is the script's output.
- CSVs: `daily.csv`, `monthly.csv`, `weekly_vs_expected.csv`, `gap_runs.csv`, `anomalous_days.csv`, `backtest_monthly.csv`, `forecast_dec2010.csv`, `same_period_by_year.csv`, `calendar_year_totals.csv`, `seasonality_dow.csv`, `seasonality_month.csv`.
- Charts: `chart_monthly_kwh.png`, `chart_seasonality.png`, `chart_weekly_anomalies.png`, `chart_forecast_dec2010.png`.
