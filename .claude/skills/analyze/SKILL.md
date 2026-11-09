---
name: analyze
description: Main entry point - answer a question from a given data file or folder. Routes through EDA -> relevance check -> plan -> the right analysis skill -> chart -> answer -> QA. Use whenever the user gives data plus a question, or asks to analyze, chart, or predict something from a dataset.
argument-hint: <data file or folder> : <question>
---

# Analyze (orchestrator)

Arguments: $ARGUMENTS

# Reading the arguments
- Format: `<data file or folder> : <question>` - split on the **first** ` : ` (space-colon-space). Left = data path, right = question.
  Example: `/analyze data/oulad/ : Which module has the highest withdrawal rate?`
- Paths with spaces may be quoted: `"my data/file.csv" : question`.
- No ` : ` found: if the first token is an existing path, treat it as the path and the rest as the question.
- Path missing or not found: list candidate data files in the project and ask which one. Question missing: show what the data contains (`data-eda`) and ask what to answer.

# When to use
- The user gives a data file/folder and a question about it
- The user asks to "analyze", "chart", "find out", or "predict" something from a dataset

# Process
1. **Explore** - `/data-eda` on the data path.
2. **Gate** - `/data-relevance` with the question. If **Not relevant -> stop and refuse** (explain what's missing).
3. **Plan** - `/analysis-plan`: make the question precise, split it into sub-questions, pick a skill for each.
4. **Analyze** - run the chosen skill(s) for each sub-question:

   | Question looks like... | Skill |
   |---|---|
   | how many / what % / average / top-N | `/data-calc` |
   | is A different from B? did the change/treatment work? | `/group-compare` |
   | why did X drop/rise? what drives X? | `/root-cause` |
   | what kinds of students/customers/items are there? | `/segmentation` |
   | trend / seasonality / anomalies / forecast over time | `/time-series` |
   | retention or behaviour of groups by start period | `/cohort-analysis` |
   | conversion through ordered steps | `/funnel-analysis` |
   | predict an outcome for new/future cases | `/data-predict` |
5. **Visualize** - `/data-chart` whenever a chart makes the answer clearer (or was asked for).
6. **Answer** - `/answer-write`.
7. **Check** - `/answer-qa` before replying; fix anything it flags.

For a simple question, do these steps briefly; no ceremony.

# Inputs the skill needs
- Required: data path; the question
- Optional: who the answer is for (default: the user themselves)

# Output
- `outputs/<question-slug>/` with `analysis.py`, result CSVs, `*.png` charts, `answer.md`
- Chat reply: answer first, evidence, method, caveats

# Ground rules (all skills)
- Every number and chart comes from code actually run on the given data. Never estimate or invent data.
- Raw data is read-only.
- Python: use any interpreter that can `import pandas, numpy, scipy, matplotlib, seaborn, sklearn` (check once with `python -c "import pandas, sklearn"`). If several are installed and `python` lacks them, find one that has them; if none does, `pip install` the missing ones. Never hardcode an interpreter or machine path in scripts - use paths relative to the project.
- Observational data shows association, not causation.
