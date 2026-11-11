# Is alcohol consumption associated with lower final grades (G3)?

**Answer: Yes, modestly.** Higher workday and weekend drinking go with lower G3. The association is small to moderate, is statistically significant, and is observational only.

Setup: 686 unique students, one row each (358 take both courses). G3 is the mean over the courses a student takes. Alcohol is scored 1–5, with "high" defined as ≥3.

| Sample | Alcohol | Spearman ρ [95% bootstrap CI] | Slope (G3 pts per 1 level) | High vs low (≥3 vs ≤2) mean G3 | Cohen's d | Welch p |
|---|---|---|---|---|---|---|
| **Main (zeros kept)**, n=686 | Workday | −0.17 [−0.24, −0.10] | −0.54 ± 0.28 | 10.4 vs 11.3 (−0.95) | −0.28 | 0.007 |
| | Weekend | −0.13 [−0.20, −0.05] | −0.34 ± 0.20 | 10.7 vs 11.5 (−0.78) | −0.23 | 0.003 |
| **Excluding students with any G3=0**, n=635 | Workday | −0.18 [−0.25, −0.11] | −0.54 ± 0.22 | 10.8 vs 12.0 (−1.21) | −0.46 | <0.001 |
| | Weekend | −0.17 [−0.25, −0.09] | −0.39 ± 0.16 | 11.3 vs 12.2 (−0.95) | −0.36 | <0.001 |

- **Size:** The high-drinking group scores about 1 grade point lower on the 0–20 scale, which is a small-to-medium effect (d ≈ −0.2 to −0.5). Alcohol explains roughly 2–3% of the variance in G3 (r ≈ −0.13 to −0.19).
- **Adjusted:** I adjusted for sex, study time, past failures, wanting higher education, school and age, and used zeros-excluded data. The workday coefficient is −0.37 points per level (p=0.0005). The weekend coefficient is −0.30 (p=0.0001).
- **Both together:** With workday and weekend in one model, the two share the effect because they are correlated. The weekend coefficient stays −0.22 (p=0.02) and the workday coefficient is −0.20 (p=0.12). I can't separate the two cleanly.
- **Zeros kept, adjusted:** Estimates shrink (workday −0.32, p=0.02; weekend −0.19, p=0.06). Treat the adjusted effect as about −0.2 to −0.4 points per level.
- **Charts and tables:** `g3_by_alcohol.png` shows mean G3 by alcohol level. `results.csv`, `adjusted_ols.csv`, `zero_rate.csv` and `student_level_table.csv` hold the numbers.

## Handling students in both files
- There is no student ID. I matched on the 13 attributes from the dataset's own `student-merge.R`.
- 4 keys in Math and 12 in Portuguese are duplicated within a file, so they are ambiguous. I matched only keys that are unique in both files, giving 358 students. The R script's 382 pairs would include ambiguous matches.
- Alcohol answers are identical across the two files for all 358 matched students (100% agreement). The two G3s correlate at only 0.48.
- Stacking all 1,044 rows would count the same student twice and overstate precision. Each student is therefore one row, with their G3 averaged across courses.
- The unmatched rows stay as separate students. This may split a few real students in two, but it is conservative.

## Suspicious G3 values
- 38 Math rows and 15 Portuguese rows have G3=0. Those students have 0 absences, versus 6.3 (Math) and 3.8 (Portuguese) for everyone else.
- In 25 Math and 8 Portuguese cases the prior-term G2 was above 0, so the 0 looks like a missed exam or dropout rather than a true score.
- The Math file is hit hardest (38 zeros of 395 rows), and the effect nearly vanishes when they are kept. In Math-only data the workday effect is d≈0 (p=0.99). Excluding zeros gives d≈−0.31.
- I report both versions. Primary: zeros kept, because they are real students. Sensitivity: students with any G3=0 excluded (51 students).
- Dropping zeros strengthens the effect, so the zeros add noise, which weakens the association in the zeros-kept analysis.
- Zero-G3 rates are not higher among heavy drinkers (workday 5.0% vs 7.8%, Fisher p=0.50; weekend 5.7% vs 8.5%, p=0.18). Alcohol therefore does not predict dropout here, and excluding zeros doesn't selectively remove heavy drinkers.

## Caveats
- This is association, not causation. Study habits, motivation and family background could drive both drinking and grades. Adjustment is partial.
- Alcohol is self-reported on a coarse 1–5 scale. Only 80 students are high workday drinkers.
- The Portuguese course carries most of the signal (d≈−0.5). Math with zeros kept shows almost none.
- The matching is heuristic.
- Significance was judged at α=0.05 with no multiple-comparison correction. The main results are p<0.01, so they would survive one.

Method: Spearman with bootstrap CIs (1,000 resamples), OLS slopes, Welch t-test and Mann-Whitney on high vs low, Cohen's d, Fisher exact test. Everything is reproducible with `python -I outputs/alcohol-vs-g3/analysis.py` from the project root.
