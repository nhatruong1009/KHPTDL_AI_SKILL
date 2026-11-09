# Data Question Skills - How They Work Together

This folder holds 15 Claude skills that turn **"here is some data + a question"** into an
**evidence-backed answer** (numbers, tables, charts, or a model). This document explains the
flow for humans. Claude itself reads the individual `SKILL.md` files.

each skill follows the same shape - *When to use -> Process (about 6 steps) -> Inputs -> Output*.

---

## 1. The big picture

```
   data path + question
           |
           v
   +----------------+
   |    analyze     |   orchestrator skill: runs the steps below in order
   +----------------+
           |
   [1] data-eda ............ what is in the data? is it reliable?
           |
   [2] data-relevance ...... can THIS data answer THIS question?
           |
           +--- Not relevant ---> STOP: refuse, explain what is missing
           |
   [3] analysis-plan ....... make the question precise, split it, pick methods
           |
   [4] one or more analysis skills (per sub-question):
           |
           |   data-calc ........ how many / what % / average / top-N
           |   group-compare .... is A different from B? did it work?
           |   root-cause ....... why did X change? why is group Y worse?
           |   segmentation ..... what kinds of students/users are there?
           |   time-series ...... trend, seasonality, anomalies, forecast
           |   cohort-analysis .. retention by start period
           |   funnel-analysis .. drop-off through ordered steps
           |   data-predict ..... predict an outcome for new/future cases
           |
   [5] data-chart .......... draw the chart(s) that prove the answer
           |
   [6] answer-write ........ answer first, then evidence, method, caveats
           |
   [7] answer-qa ........... check before delivering; loop back to fix
           |
           v
       final answer (chat + outputs/<question-slug>/)
```

The flow is a **pipeline with two exits**:
- **Early exit** at step 2, if the data cannot answer the question (Claude refuses instead of guessing).
- **Loop back** from step 7, if QA finds a problem (Claude fixes the script and re-runs, then re-checks).

---

## 2. What each step does and hands to the next

| # | Skill | Input | Does | Hands over |
|---|---|---|---|---|
| 1 | `data-eda` | data path | runs `scripts/inspect_data.py`; reads README/codebook; finds the grain, keys, date columns, possible target; checks nulls, duplicates, odd values, joins | EDA summary table + top data issues |
| 2 | `data-relevance` | question + EDA summary | maps each concept of the question to real columns ([OK] / [PARTIAL] / [MISSING]); checks what the data's design allows (no causal claims from observational data, no prediction without an outcome column) | decision: Relevant / Partially relevant (narrowed question) / Not relevant (refuse) |
| 3 | `analysis-plan` | final question wording | defines metric, denominator, filters, grouping, time window, unit; splits into sub-questions; picks a skill for each; lists risks | plan table: sub-question -> columns -> skill -> output |
| 4 | analysis skills | one sub-question each | writes and runs `outputs/<slug>/analysis.py`; prints counts so numbers can be checked | result tables (CSV), statistics, model metrics |
| 5 | `data-chart` | computed results + the message | picks the chart type from the message, saves a PNG, opens it to check | `outputs/<slug>/*.png` |
| 6 | `answer-write` | all results | writes the direct answer first, then evidence, method, assumptions and caveats | `outputs/<slug>/answer.md` + chat reply |
| 7 | `answer-qa` | the outputs folder | checks question fit, number tracing, denominators/joins, statistics, claims, charts | pass, or a list of fixes (then back to step 4/5/6) |

---

## 3. How step 4 picks the analysis skill

`analysis-plan` classifies each sub-question by its shape:

| The question sounds like... | Skill | Typical output |
|---|---|---|
| "How many...?", "What % ...?", "Which module is highest?" | `data-calc` | table with n, %, numerator/denominator |
| "Do A and B differ?", "Is X related to Y?", "Did the change work?" | `group-compare` | group stats + test + effect size + one-line verdict |
| "Why did the pass rate drop?", "Why is group Y worse?" | `root-cause` | timeline + contribution table + main driver |
| "What types of learners are there?" | `segmentation` | segment profiles + labels |
| "How has X changed over time?", "Forecast X" | `time-series` | trend chart, anomalies, forecast with interval |
| "Do newer intakes retain better?" | `cohort-analysis` | cohort x period retention matrix + heatmap |
| "Where do people drop out of the process?" | `funnel-analysis` | step table with conversion and drop-off |
| "Can we predict who will fail?" | `data-predict` | baseline vs model metrics + top features |

Rules of thumb:
- **Prefer the simplest skill that fully answers the question.** Most questions are `data-calc` or `group-compare`.
- **"What affects Y?" is not a prediction question.** It goes to `group-compare` or `root-cause`. `data-predict` is only for predicting new or future cases.
- A compound question can use **several skills**. For example, "why are students failing module X?" -> `data-calc` (fail rate) + `group-compare` (what differs between pass and fail) + `data-chart`.

---

## 4. Ground rules shared by every skill

1. **No invented numbers.** Every number, table and chart comes from code actually run on the given data.
2. **Raw data is read-only.** All work goes into `outputs/<question-slug>/`.
3. **Association is not causation.** Observational data gets "associated with", never "causes".
4. **Refuse rather than guess.** If the data cannot answer the question, say so and say what data would be needed.
5. **State assumptions.** Vague words ("active", "at risk", "best") get a stated, data-based definition.
6. **Portable.** No hardcoded machine paths; Python is any interpreter that has pandas, numpy, scipy, matplotlib, seaborn and scikit-learn.

---

## 5. Worked examples

### A. Relevant question (simple)
> data: `data/oulad/`, question: "Which module has the highest withdrawal rate?"

1. `data-eda`: `studentInfo.csv` has one row per student-module-presentation; `final_result` holds Pass / Fail / Withdrawn / Distinction.
2. `data-relevance`: module -> `code_module` [OK]; withdrawal -> `final_result == "Withdrawn"` [OK] => **Relevant**.
3. `analysis-plan`: % of registrations with Withdrawn per `code_module`, where the denominator is all registrations in that module -> `data-calc` + bar chart.
4. `data-calc` -> `result.csv`.
5. `data-chart` -> sorted horizontal bar chart, with the top module highlighted.
6. `answer-write` -> "Module X has the highest withdrawal rate (N%, n=...)" plus the chart and caveats.
7. `answer-qa` -> the denominators and counts check out -> deliver.

### B. Partially relevant question
> "Does watching more videos make students pass?"

- `data-relevance`: "watching videos" -> VLE `activity_type` / `sum_click` [PARTIAL] (clicks are a proxy for watching); "make ... pass" is a causal claim on observational data.
- Narrowed question: "Is the number of VLE clicks associated with passing?" -> `group-compare` (Mann-Whitney U + effect size) + box-plot chart. The answer states that this shows association, not cause.

### C. Not relevant question
> "What is the average teacher salary per module?"

- `data-relevance`: salary -> [MISSING]. **Refuse**: the dataset has no staff or salary data. It covers students, modules, assessments and VLE activity, so a staff/HR dataset would be needed. Claude may suggest a related question this data *can* answer.

### D. Prediction question
> "Can we predict which students will withdraw, using the first 4 weeks of activity?"

- `analysis-plan` -> `data-predict`. The prediction moment is week 4, so only features from before day 28 are used, and `final_result` / `date_unregistration` are dropped as leakage. Stratified split, dummy baseline -> logistic regression -> gradient boosting. Report PR-AUC, recall and the top features. `data-chart` draws the confusion matrix and the feature-importance chart.

---

## 6. How to use

| You want... | Type |
|---|---|
| the full flow | `/analyze <data file or folder> : <question>` |
| just look at a dataset | `/data-eda <path>` |
| just check if a question is answerable | `/data-relevance <question>` |
| a specific analysis | `/time-series ...`, `/group-compare ...`, etc. |
| a chart from existing results | `/data-chart <message>` |
| a review of an answer | `/answer-qa outputs/<slug>/` |

Example:

```
/analyze data/oulad/ : Which module has the highest withdrawal rate?
/analyze data/students.csv : Is study time associated with the final grade?
/analyze "my data/sales.xlsx" : Draw the monthly revenue trend for 2024
```

The data path is everything before the first ` : ` and the question is everything after it.

You can also just ask in plain words ("here's data/, which module has the most withdrawals?").
Claude matches the request to `analyze` through the skill descriptions.

---

## 7. Folder layout

```
.claude/skills/
  ORCHESTRATOR.md          <- this file (for humans)
  analyze/SKILL.md         <- orchestrator skill (for Claude)
  data-eda/
    SKILL.md
    scripts/inspect_data.py
  data-relevance/SKILL.md
  analysis-plan/SKILL.md
  data-calc/SKILL.md
  group-compare/SKILL.md
  root-cause/SKILL.md
  segmentation/SKILL.md
  time-series/SKILL.md
  cohort-analysis/SKILL.md
  funnel-analysis/SKILL.md
  data-predict/SKILL.md
  data-chart/SKILL.md
  answer-write/SKILL.md
  answer-qa/SKILL.md

outputs/<question-slug>/   <- created per question
  analysis.py | model.py   <- reproducible code
  result.csv               <- computed tables
  *.png                    <- charts
  answer.md                <- final answer
```

---

## 8. Adding or changing a skill

1. Create `.claude/skills/<new-name>/SKILL.md` with frontmatter `name` and `description`.
   The description decides when Claude picks the skill, so say *what it does* and *when to use it*.
2. Keep the four sections: When to use / Process / Inputs the skill needs / Output.
3. Use ASCII characters only and no machine-specific paths.
4. Add the skill to the routing table in `analyze/SKILL.md` and in section 3 of this file.
