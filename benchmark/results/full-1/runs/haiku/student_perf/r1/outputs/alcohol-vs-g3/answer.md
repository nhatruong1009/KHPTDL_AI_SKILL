# Is alcohol use associated with lower final grades (G3)?

**Short answer:** Yes in the raw data, but mostly not after accounting for background and earlier grades.

- **Raw association is clear.** Higher workday (Dalc) and weekend (Walc) alcohol use go with lower G3. Each step on the 1–5 scale is about **−0.6 (Dalc) and −0.4 (Walc) grade points** on the 0–20 scale (both p < 0.001 alone). Students with Dalc ≥ 4 average **10.4 vs 12.0** (Hedges g = −0.55). Students with Walc ≥ 4 average **10.9 vs 12.2** (g = −0.46).
- **Adjusted association is small and mostly not significant.** After controlling for course, school, sex, age, study time, past failures and absences, the joint estimates are Dalc −0.19 (95% CI −0.45 to +0.06, p = 0.13) and Walc −0.19 (CI −0.38 to +0.01, p = 0.06).
- **Controlling for earlier grades removes almost all of it.** With G1 and G2 added, Dalc −0.06 (CI −0.19 to +0.08) and Walc −0.02 (CI −0.07 to +0.04). The gap is already present in the first two periods. Heavy drinkers were already doing worse, so the raw gap largely reflects who drinks heavily, not a grade drop caused by drinking.
- **Weekend use shows the most persistent small signal.** Walc is negative in all five M1 variants (adjusted, without G1/G2) and is significant in two of them (Math-only: −0.34, p = 0.04; one-row-per-student: −0.26, CI −0.48 to −0.04, p = 0.02). That is roughly a quarter of a grade point per step, and it disappears once prior grades are added.

This is observational data, so these are associations, not causal effects.

## Data and handling decisions

| Issue | How it was handled |
|---|---|
| 382 students in both files | R merge on the 13 keys gives 382 rows, but 12 of these come from identical-key groups that multiply records. One-to-one linking gives **370 students**. The Math and Portuguese records are kept as separate course enrolments, because G3 is course-specific. Standard errors are clustered by student. |
| Overlapping students' alcohol values | Dalc and Walc agree for 98% and 97% of overlapping pairs, so the same person is not counted as two different exposures. A "one row per student" sensitivity check (dropping the Portuguese copy) is reported. |
| Suspicious G3 = 0 | 53 enrolments (38 Math, 15 Portuguese). 33 have G2 > 0, and their mean G2 is 4.4 (vs 11.6 for the rest), so they look like collapsed performance or non-completion, not real scores. They are **excluded in the primary analysis** and included in sensitivity. Their alcohol use does not differ from other students (Dalc p = 0.55, Walc p = 0.37). |
| Panel structure | Final sample: 1,044 enrolment rows (991 with G3 > 0), 674 unique students. |

## Method

- Exposure: Dalc and Walc as 1–5 ordinal scores, entered as numeric (one unit = one level). Heavy use = score ≥ 4 for group comparisons.
- Bivariate: Spearman rho, Welch t test, Mann–Whitney U, Hedges g with 95% CI.
- Regression: OLS with student-clustered standard errors (t reference with clusters − 1 df), 95% CIs, standardized betas.
  - M0 unadjusted
  - M1 adjusted for course, school, sex, age, study time, failures, absences
  - M2 = M1 + G1 + G2
- Sensitivity: keep G3 = 0; Math only; Portuguese only; one row per student.

## Key results (primary sample, G3 > 0)

| Model | Dalc per level (CI) | Walc per level (CI) |
|---|---|---|
| M0 unadjusted, Dalc alone | −0.57 (−0.79, −0.36) | |
| M0 unadjusted, Walc alone | | −0.43 (−0.59, −0.26) |
| M0 unadjusted, joint | −0.33 (−0.61, −0.05) | −0.28 (−0.49, −0.07) |
| M1 adjusted, joint | −0.19 (−0.45, +0.06) | −0.19 (−0.38, +0.01) |
| M2 + G1, G2, joint | −0.06 (−0.19, +0.08) | −0.02 (−0.07, +0.04) |

Bivariate: Spearman rho = −0.18 (Dalc) and −0.18 (Walc), both p < 0.001 (not adjusted for clustering).

Adjusted M1 across variants (Dalc / Walc):

| Variant | Dalc | Walc |
|---|---|---|
| Keep G3 = 0 (n = 1,044) | −0.28 (p = 0.09) | −0.08 (p = 0.52) |
| Math only (n = 357) | −0.05 (p = 0.81) | −0.34 (p = 0.04) |
| Portuguese only (n = 634) | −0.28 (p = 0.05) | −0.09 (p = 0.35) |
| One row per student (n = 626) | −0.11 (p = 0.41) | −0.26 (p = 0.02) |

## Caveats

- **Observational data.** Alcohol use is self-reported and measured once. Prior grades, study time and other factors are only partly captured.
- **Many specifications.** Five data variants × five models × two exposures were estimated (dozens of coefficient tests). The few p-values near 0.05 should be treated as exploratory.
- **Small heavy groups.** Only 49 enrolments have Dalc ≥ 4, so the Dalc group comparison is imprecise.
- **Overlap linking.** Pairing by identical keys is not certain for the ~16 rows in duplicated key groups, so a few links may be wrong. This is unlikely to change the conclusions.
- **G3 = 0 interpretation.** Treating these as non-completion is an assumption. Including them weakens the adjusted weekend estimate (−0.19 → −0.08), because these students already had very low G2.

## Files

- `analysis.py` – full analysis (runs from the project root with `python -I outputs/alcohol-vs-g3/analysis.py`)
- `eda_check.py` – initial data checks (nulls, duplicates, G3 = 0 counts, overlap agreement)
- `regression_results.csv` – all regression estimates and sensitivity variants
- `effect_sizes.csv` – bivariate effect sizes
- `g3_by_dalc.csv`, `g3_by_walc.csv` – descriptive means by alcohol level
- `g3_by_alcohol.png` – mean G3 by Dalc and Walc with 95% CIs
