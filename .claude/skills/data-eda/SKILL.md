---
name: data-eda
description: Exploratory data analysis and quick quality check of a data file or folder - structure, grain, nulls, duplicates, outliers, distributions, correlations, join keys. Activate first whenever a new dataset is given, or when asked what is in the data or whether it is reliable.
argument-hint: <file-or-folder>
---

# Data EDA (programmatic-eda + data-quality-audit, simplified)

# When to use
- A new dataset arrives and must be understood before answering anything
- A result looks surprising and the underlying data needs checking
- Someone asks "what's in this data?" or "is this data reliable?"

# Process
1. **Overview** - run `python <this skill folder>/scripts/inspect_data.py <path>`: files, rows x cols, dtypes, missing %, unique counts, samples, ID/date/target hints, shared join keys.
2. **Read the docs** - open any README / codebook it lists; take column meanings and codes from there, not from column names.
3. **Confirm the grain** - state what one row represents in each file and which column(s) form the key (check uniqueness).
4. **Quality checks** (quick pandas snippet as needed):
   - nulls: flag columns > 5% missing; > 50% = barely usable
   - duplicates: full-row and key-level; are they errors or legitimate repeats?
   - ranges/validity: impossible values (negative counts, scores > max, dates in the future, unknown codes like "?")
   - joins: orphan keys between files; does a join multiply rows?
5. **Distributions & relations** - for numeric columns: skew, zeros, IQR outliers (real or error?); for categories: rare levels; flag numeric pairs with |r| > 0.8.
6. **Summarize** - the table below plus the top 3-5 issues that could affect answers.

# Inputs the skill needs
- Required: file or folder path
- Optional: what one row should represent; columns to skip

# Output
| File | Rows x Cols | One row = | Key | Date cols | Possible target | Issues |

Plus a "Top issues" list (issue -> evidence -> impact). Facts only from script output and docs.
