---
name: answer-write
description: Turn analysis results into a clear final answer - direct answer first, evidence, method, assumptions and caveats, and (if asked) so-what / next steps. Combines insight synthesis, executive summary and assumptions log in a light form. Use at the end of any data question.
argument-hint: <question>
---

# Answer Write (insight-synthesis + executive-summary + assumptions-log, simplified)

# When to use
- Analysis is done and the result must be communicated
- Results are a pile of numbers with no clear "so what"

# Process
1. **List findings as facts** - each a plain statement with its number and n, taken from the run outputs.
2. **Answer the exact question first** - 1-3 sentences, conclusion first (pyramid style), key numbers included. If the question has sub-questions, answer each in one line.
3. **Pick the evidence** - the 1-3 tables/charts that prove the answer; drop interesting-but-irrelevant findings.
4. **So what (only if useful or asked)** - why it matters and a concrete next step; label it a suggestion, not a finding.
5. **Assumptions & caveats** - definitions chosen for vague terms, filters, missing-value handling, proxies, small groups, association != causation, model limits. Only those that could change the reading.
6. **Write it** - `outputs/<slug>/answer.md` and the chat reply.

If the question was refused at `/data-relevance`: reply only with why, what the data contains, and what would be needed.

# Inputs the skill needs
- Required: the question; analysis outputs (printed results, CSVs, charts)
- Optional: audience (default: the user; if for a manager/report, keep it shorter and less technical)

# Output
```
**Answer:** ...
**Evidence:** table / [chart](outputs/<slug>/x.png)
**How:** 2-4 bullets - data, filters, method
**Assumptions & caveats:** ...
```
