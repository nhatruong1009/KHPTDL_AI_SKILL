# Household energy, Dec 2006 – Nov 2010

## Answer
- **Forecast, December 2010: ≈ 970 kWh (95% range ≈ 740 – 1,190 kWh).** That is about 31 kWh/day.
- **Trend:** there is essentially none. Jan–Nov average use was 25.7, 25.3, 25.2 and 25.4 kWh/day in 2007, 2008, 2009 and 2010. Usage is flat to within ±2%. The 43.6 kWh/day figure for 2006 covers only 16–31 Dec, so it reflects December, not a higher baseline.
- **Annual seasonality is strong.** The winter-to-summer swing is about 2.5×: average 2007–09 use was 35 kWh/day in January and 34 in December, against 13.6 in August (monthly values in `month_profile.csv`).
- **Weekly pattern:** weekends use about 19% more than weekdays, 29–30 vs about 24–26 kWh/day. Thursday is the lowest at 23.5 kWh/day.
- **Daily pattern:** there is a night trough of about 0.45 kW at 03:00–05:00. A morning peak of about 1.5 kW comes at 07:00–08:00, and the main evening peak of about 1.9 kW at 20:00–21:00.

## Unusual periods
- **Gaps:** 25,979 of 2,075,259 minutes (1.25%) are missing. They are recorded as blanks, with no absent rows. The largest gaps:

| Gap | Length |
|---|---|
| 17–22 Aug 2010 | 5.0 days |
| 25–28 Sep 2010 | 3.6 days |
| 28–30 Apr 2007 | 2.6 days |
| 13–15 Jun 2009 | 2.3 days |
| 12–14 Jan 2010 | 2.2 days |
| 20–21 Mar 2010 | 1.4 days |

  There are also a few shorter gaps. Gaps are listed in `gaps.csv`.
- **Abnormal low weeks:** the most extreme run is **the four weeks ending 10–31 Aug 2008**, four straight weeks at 4.4–8.6 kWh/day against a normal 14–19. August 2008 totalled only 206 kWh. This looks like a household absence, such as a holiday, rather than missing data, because the readings are present and low. Other weeks that are low for their season:
  - 4 Mar 2007
  - 15 Apr 2007
  - 24 Jun 2007
  - 4 Nov 2007
  - 2 Mar 2008
  - 2 Nov 2008
  - 22 Feb 2009
  - 19–26 Jul 2009
  - 9 Aug 2009
  - 7 Mar 2010
  - 8–15 Aug 2010
- Every August from 2007 to 2010 has at least one or two low weeks, consistent with annual holidays. Whether any given low week is a real absence is an inference from the pattern.
- **Abnormal high weeks:** a few August weeks (2007, 2009, 2010) are above the August median. These are mild, with z up to about 3.
- The full list with robust z-scores is in `abnormal_weeks.csv`.

## Method
- I converted each minute's average active power (kW) to kWh by dividing by 60, then summed to days.
- Days with under 50% coverage are treated as missing. Partial days are scaled up by their coverage.
- Monthly kWh is the month's mean daily use × the number of days in the month.
- Weekly anomalies are weekly means compared with the median for the same calendar month, then scored with a robust z (median/MAD). Flagged weeks have |z| > 2.5.
- **Forecast:** I took the 2008 and 2009 Decembers (949 and 1,015 kWh, or 30.6 and 32.7 kWh/day) and rescaled each to 2010's level. The scaling uses two ratios, Jan–Nov and Sep–Nov usage in 2010 against the earlier year. The four resulting estimates are 955, 1,023, 898 and 989 kWh, averaging **966 kWh**.
- **Uncertainty:** the ratio of December use to Jan–Nov use varies across 2007, 2008 and 2009 (1.52, 1.21, 1.30). That is a coefficient of variation of 11.9%. I applied ±1.96 × 11.9% to the point forecast to get 741–1,192 kWh.

## Caveats
- The forecast rests on only three prior Decembers, and the interval is rough. The CV comes from three points, so a true 95% interval could be wider. It is also asymmetric in practice: the main upside risk is a repeat of December 2007.
- I excluded Dec 2007 (1,210 kWh, or 39 kWh/day) from the point estimate because it was well above the other two years. Including it would give about 1,040 kWh. A repeat of December 2007 would land near the top of the range.
- A backtest of the same method confirms the problem. Predicting Dec 2008 from 2007 overshot by 26%, and predicting Dec 2009 from 2007–08 overshot by 5%.
- Nov 2010 has only 26 days of data. The scaling treats its missing days as typical.
- The weather and household occupancy are not in the data, so the causes of the seasonal swing and of the abnormal weeks are inferences, not findings.
- kWh here is whole-house active energy (Global_active_power). Sub-metering was not analysed.

Files: `analysis.py`, `monthly.csv`, `daily.csv`, `gaps.csv`, `abnormal_weeks.csv`, `forecast.csv`, `trend.png`, `seasonality.png`.
