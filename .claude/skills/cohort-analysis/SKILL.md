---
name: cohort-analysis
description: Cohort analysis - group entities by their start period (registration term, signup month, first activity) and track retention or behaviour over the following periods as a cohort x period matrix with heatmap and curves. Use for "are we retaining students/users better than before", "when do people drop off", "how do intake groups compare over time".
argument-hint: <entity, start date, activity date>
---

# Cohort Analysis

# When to use
- Retention / continued activity by intake group
- Comparing how cohorts (by start period, channel, module) behave over their lifetime
- Finding at which period people typically leave

# Process
1. **Define** - cohort = start period of each entity (e.g. first registration month / presentation); activity = the event that counts as "still active"; period grain (week/month/term).
2. **Build the table** - per entity: cohort period; per activity: period index = activity period - cohort period. Keep one row per entity per active period (deduplicate).
3. **Retention matrix** - cohort x period index: active entities / cohort size. Show cohort sizes alongside; mark cohorts < ~30-100 as noisy.
4. **Visualize** - heatmap of the matrix (`seaborn.heatmap`, % annotations) and retention curves per cohort.
5. **Interpret** - where the biggest drop happens (period 0->1?), whether newer cohorts retain better or worse, and plateaus. Note cohorts that are too young to have later periods (right-censoring) - don't read their blanks as zero.
6. **Summarize** - 3-5 sentences with the key numbers.

Run with `python` in `outputs/<slug>/analysis.py`.

# Inputs the skill needs
- Required: entity ID, start date (or start period), activity date
- Optional: grain, number of periods, a dimension to split cohorts by

# Output
`retention_matrix.csv`, heatmap + curves PNGs, short interpretation.
