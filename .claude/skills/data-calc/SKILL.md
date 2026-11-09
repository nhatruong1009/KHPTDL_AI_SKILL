---
name: data-calc
description: Calculate metrics from data with pandas - counts, percentages, rates, averages, medians, top-N, group breakdowns, crosstabs, simple trends. Use for any "how many / what % / which is highest / what is the average" question.
argument-hint: <precise sub-question>
---

# Data Calc (business-metrics-calculator, generalized)

# When to use
- How many / what share / what rate / average / median / top-N / breakdown by group
- A KPI must be computed from raw rows

# Process
1. **Write the metric formula** - numerator, denominator, filters, grouping (from `/analysis-plan`).
2. **Load & validate** - in `outputs/<slug>/analysis.py`: load, apply filters, join if needed. **Print row counts after each filter/join**; if a join increases rows, fix duplicate keys first.
3. **Handle missing values** - decide drop / exclude from denominator / own category; print how many rows are affected.
4. **Compute** - groupby/aggregate; for % print numerator, denominator, and %; sort meaningfully; include group sizes (n).
5. **Sanity-check** - totals add up to the overall count, % within 0-100, no group silently dropped (use `dropna=False` in groupby where relevant).
6. **Save & read** - save `result.csv`; write a 1-2 line plain reading. Hand off to `/data-chart` if a chart helps.

Run with `python`; use only printed results.

# Inputs the skill needs
- Required: precise sub-question; data path
- Optional: filters, period, grouping

# Output
- Result table (with n) printed and saved to `outputs/<slug>/result.csv`
- 1-2 line interpretation
