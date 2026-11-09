---
name: group-compare
description: Compare groups with significance testing - is A different from B, did a treatment/variant/change make a difference, is a factor associated with an outcome. Covers A/B tests, two-group and multi-group comparisons, and categorical associations, with effect sizes and confidence intervals. Use for "is there a difference / does X relate to Y / did it work" questions.
argument-hint: <groups and metric to compare>
---

# Group Compare (ab-test-analysis, generalized)

# When to use
- "Do students in group A score higher than group B?"
- "Is gender/region/device associated with the outcome?"
- An A/B test or before/after comparison needs a verdict

# Process
1. **Define** - groups (column + values), metric (rate or mean), unit (one row = one person?). For an experiment: control vs treatment and the expected split.
2. **Check balance** - group sizes; for a randomized test run a chi-square on actual vs expected split (sample ratio mismatch -> stop and report).
3. **Describe each group** - n, rate/mean/median with 95% CI.
4. **Test** - pick by data type:

   | Comparing | Test (scipy) | Effect size |
   |---|---|---|
   | rate between 2 groups | two-proportion z-test / chi-square | difference in pp, relative lift, CI |
   | category x category | `chi2_contingency` (Fisher if counts < 5) | Cramer's V, % differences |
   | numeric, 2 groups | Mann-Whitney U (default) / Welch t-test | median/mean diff, Cohen's d |
   | numeric, 3+ groups | Kruskal-Wallis / ANOVA | group medians, eta^2 |
   | numeric x numeric | Spearman / Pearson | r |
   | several factors at once | logistic / linear regression | odds ratios / coefficients |
5. **Interpret honestly** - report the effect size and CI, not just p; statistically significant != important; with many tests, some hits are chance. Observational data -> "associated with", never "causes". Only a randomized test supports a causal verdict.
6. **Verdict** - one sentence (e.g. "Group A's pass rate is 8 pp higher, 95% CI 5-11 pp, p < 0.001"); for an A/B test: ship / don't ship / need more data.

Run with `python` in `outputs/<slug>/analysis.py`.

# Inputs the skill needs
- Required: group column(s), metric/outcome column
- Optional: whether the groups were randomized; significance level (default 0.05)

# Output
Comparison table (group, n, metric, CI) + test result + effect size + one-line verdict; hand off to `/data-chart` (bar with CI or box plot).
