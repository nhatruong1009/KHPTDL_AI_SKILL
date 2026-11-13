---
name: answer-qa
description: Pre-delivery QA for a data answer - check the question was answered as asked, numbers trace to real outputs, denominators and joins are right, statistics and charts are valid, and claims don't overreach. Use before sending any analysis result.
argument-hint: <outputs folder>
---

# Answer QA (analysis-qa-checklist, simplified)

# When to use
- Every time, before giving the final answer
- When reviewing someone else's analysis output

# Process
1. **Question fit** - does the answer address the exact question (metric, population, period) or a slightly different one? Was any narrowing stated?
2. **Numbers trace** - every number in `answer.md` appears in the script output/CSVs; re-run the script and confirm it reproduces them.
3. **Calculation checks** -
   - denominators correct; % sum to ~100 where they should
   - row counts before/after joins (no duplication), no silently dropped groups or NaN rows
   - filters match the stated population/period
   - units and scales right (%, vs fraction, currency, days)
4. **Statistics checks** - group sizes shown; effect sizes reported, not just p-values; test fits the data type; a baseline shown. Models: a feature timing audit exists and no feature of unknown availability is in the main model; the data's own split was used; thresholds/model choice made without the test set; no sensitive attribute among predictors.
5. **Claim checks** - no causal wording on observational data; no generalizing beyond the data's population; caveats present; the conclusion follows from the evidence. Every sensitivity/robustness check you ran is reflected in the headline - if one contradicts it, rewrite the headline. Every target or constraint in the question is answered met / not met.
6. **Chart checks** - open each PNG and read its title aloud: it must state the finding, not name the content. Axes labelled, the bar axis starts at 0, readable, and the chart matches the numbers.

Fix every failure and re-run before replying.

# Inputs the skill needs
- Required: question; `outputs/<slug>/` (script, results, charts, answer.md)

# Output
| Check | Pass/Fail | Note/fix |
Then a one-line verdict: ready / fixed (list) / blocked (why).
