# Has climbing Everest become safer over time?

**Yes, for both expedition members and hired staff, measured per person.** The death rate after 1990 is about half the pre-1990 rate for members and about a third for hired staff. Hired staff saw the bigger drop. The member rate has been flat at about 1 death per 100 climbers since 2000, so the gain is not still accelerating.

## Evidence

Source: Himalayan Database extract in `data/`, Everest only (`peak_id = EVER`), 2,149 expeditions, 1921–2019. Script: `analysis.py`. Full output: `run_log.txt`.

| Era | Expedition members: deaths / people (rate, 95% CI) | Hired staff: deaths / people (rate, 95% CI) |
|---|---|---|
| Pre-commercial, 1921–1989 | 58 / 2,961 = **2.0%** (1.5–2.5%) | 52 / 2,530 = **2.1%** (1.6–2.7%) |
| Commercial, 1990–2019 | 128 / 12,320 = **1.0%** (0.9–1.2%) | 68 / 10,211 = **0.7%** (0.5–0.8%) |

- Rate ratio, commercial vs pre-commercial: members 0.53 (chi-square p = 4e-5); hired staff 0.32 (p = 9e-11).

Decade rates (deaths per 100 people):

| Decade | 1960 | 1970 | 1980 | 1990 | 2000 | 2010 |
|---|---|---|---|---|---|---|
| Expedition members | 2.2 | 1.6 | 2.0 | 1.4 | 1.0 | 0.9 |
| Hired staff | 0.6 | 2.4 | 2.0 | 1.1 | 0.3 | 0.8 |

Hired-staff deaths are lumpy. 2014 (17 deaths) and 2015 (11) account for 28 of the 40 hired-staff deaths in the 2010s. Excluding those two years, the hired-staff rate for the 2010s is 0.27% (12 / 4,365), and the commercial-era rate is 0.42%. The member rate does not depend on those years: it is 1.10% without them.

Deaths per 100 summits (expedition members): 26.5 before 1990 vs 2.6 after. Part of this is denominator: the share of members who reached the summit rose from 7.8% to 39.9%.

## What changed in the commercial era

- **Who goes:** average expedition size fell from 14.5 members to 6.3. Hired staff per expedition fell from 12.4 to 5.3.
- **Equipment and support:** oxygen use among members rose from 20% to 53%. A named trekking agency appears on 97% of expeditions, up from 26%.
- **Causes of death (share of each era's deaths):** avalanche fell from 31% to 22%; icefall collapse from 11% to 1.5%; falls from 29% to 20%. Altitude sickness (AMS) rose from 5% to 15%, exhaustion from 2% to 12%, and non-AMS illness from 5% to 10%.

## Method

1. **Scope:** Everest only. Death counts and headcounts come from the expedition-level totals (`members`, `member_deaths`, `hired_staff`, `hired_staff_deaths`). Death totals reconcile exactly with the member-level death records for the 1970s–2010s, so I used them as the complete count. Hired-staff headcounts do not reconcile at the member level (see caveats).
2. **Member-level records** were used only for roles, causes of death, oxygen, and summit detail.
3. **Commercial era** = 1990 onward, as requested.
4. **Confidence intervals** are Wilson 95% intervals. The tests are person-level chi-square tests, which ignore clustering within expeditions, so treat the p-values as indicative.

## Caveats

- **Association, not causation.** Guided, oxygen-supported, smaller expeditions became common at the same time as the death rates fell. The data cannot separate these from other changes such as better forecasting, rescue, or route fixing.
- **Who the rate describes changed.** Per-person rates compare different mixes of people across eras (more clients, fewer staff-heavy expeditions).
- **Early decades are thin.** Before 1960 there are fewer than 30 expeditions per decade, so the 1950s and earlier are excluded from the chart.
- **Hired-staff detail is incomplete at the member level** before about 2000. Hired-staff rates use the expedition-level totals, which do include them.
- **Data ends in 2019.** Seasons after 2019 are not covered.
- **Event names** (2014 Khumbu icefall, 2015 base-camp avalanche) are outside context; the data only shows the years.

## Files

- `analysis.py` — full pipeline (run with `python -I analysis.py` from this folder)
- `chart1_death_rate_by_decade.png`, `chart2_era_comparison.png`, `chart3_people_by_decade.png`
- `decade_death_rates.csv`, `era_death_rates.csv`, `era_tests.csv`, `sensitivity_excl_2014_2015.csv`, `top_years_hired_deaths.csv`, `era_member_profile.csv`, `death_causes_by_era.csv`, `era_expedition_profile.csv`
