---
name: analysis-plan
description: Turn a relevant question into a precise, answerable plan - define metric, denominator, population, grouping, time window and unit; split into sub-questions; pick the analysis skill for each; list data dependencies and risks. Use after the relevance check and before writing analysis code.
argument-hint: <question>
---

# Analysis Plan

# When to use
- After `/data-relevance` passes, before any analysis code
- When a question is vague ("best", "active", "at risk", "performance") or has several parts

# Process
1. **Make it precise** - metric (count / % / mean / median / rate), **denominator** for any %, population/filters, grouping, time window, unit (one row = ?).
   Example: "Which module do students drop most?" -> "% of registrations with `final_result == 'Withdrawn'` per `code_module`, denominator = all registrations in that module."
2. **Resolve vague words** - choose a reasonable data-based definition and state it; ask the user only if alternatives give very different answers.
3. **Decompose** - split into sub-questions Q1, Q2, ... each answerable with one calculation.
4. **Pick the method per sub-question** - `/data-calc`, `/group-compare`, `/root-cause`, `/segmentation`, `/time-series`, `/cohort-analysis`, `/funnel-analysis`, `/data-predict` (only if predicting new/future cases). Prefer the simplest method that answers it. Note where a chart helps.
5. **Dependencies & risks** - files/columns, joins (keys, uniqueness), quality issues from EDA that touch these columns, small groups.
6. **Sequence** - order the sub-questions so each feeds the next.

# Inputs the skill needs
- Required: final question wording from `/data-relevance`; EDA summary

# Output
| # | Sub-question (precise) | Columns | Method/skill | Output (number/table/chart/model) | Risk |

Output folder: `outputs/<question-slug>/`.
