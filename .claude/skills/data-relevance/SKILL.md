---
name: data-relevance
description: Check whether a given dataset can actually answer a question - map each concept in the question to real columns, decide Relevant / Partially relevant / Not relevant, and refuse when the data cannot answer it. Use after EDA and before any analysis.
argument-hint: <question>
---

# Data Relevance Gate

# When to use
- Always, after `/data-eda` and before analysis
- When a question mentions things that might not be in the data

# Process
1. **Split the question into concepts** - population, measure, grouping, time window, outcome, conditions.
2. **Map each concept to columns**:

   | Concept | Column(s) | Status |
   |---|---|---|
   | "students" | `id_student` | [OK] |
   | "final grade" | `final_result` (Pass/Fail/Withdrawn) | [PARTIAL] proxy |
   | "teacher salary" | - | [MISSING] |

   [OK] = measured directly; [PARTIAL] = proxy, derivable (write the formula), or partial coverage; [MISSING] = absent.
3. **Check what the data's design allows**:
   - "does X cause Y?" on observational data -> only association
   - "which action works?" with no action/treatment column -> not answerable
   - "predict the future" with no outcome or time order -> not possible
   - fewer than ~30 rows in a relevant group -> continue but flag
4. **Decide**:
   - **Relevant** -> continue.
   - **Partially relevant** -> state the narrowed question that *can* be answered; continue (ask only if the meaning changes a lot).
   - **Not relevant** -> **refuse**: which concepts are missing, what the data does contain, what data would be needed, and 1-2 related questions it *can* answer. Never answer from general knowledge as if it came from the data.

# Inputs the skill needs
- Required: the question; the `/data-eda` summary

# Output
Mapping table + decision + (if continuing) the final question wording.
