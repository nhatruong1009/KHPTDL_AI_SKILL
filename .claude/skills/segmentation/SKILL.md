---
name: segmentation
description: Find and profile distinct groups in the data - rule-based segments or k-means clustering on a few behaviour/attribute variables, with profiles, names, and validation. Use for "what types of students/customers/users exist", "group them", "who are the high/low performers" questions.
argument-hint: <entities to segment and goal>
---

# Segmentation Analysis

# When to use
- "What kinds of learners are there based on activity and scores?"
- Grouping entities to treat them differently
- Checking whether an existing grouping is meaningful

# Process
1. **Goal & unit** - what the segments are for, and one row = one entity (aggregate events per student/customer first).
2. **Pick 3-7 variables** related to the goal; handle missing values; scale numeric ones (`StandardScaler`); log-transform heavy skews.
3. **Segment** -
   - **Rule-based** (preferred when simple thresholds make sense, e.g. activity quartiles x pass/fail), or
   - **k-means**: try k = 2...8, choose k by elbow + silhouette (> 0.25 is acceptable, > 0.5 strong) and interpretability; `random_state=42`.
4. **Profile** - per segment: size (n, %), mean/median of each variable, and % above/below the overall average; outcome rate per segment if there is an outcome.
5. **Name & validate** - give each segment a descriptive name from its 2-3 defining traits; drop or merge segments < ~5% unless meaningful; check stability (rerun with another seed).
6. **Report** - profile table + what differs between segments; suggested use per segment only if the question asks for it.

Run with `python` in `outputs/<slug>/analysis.py`.

# Inputs the skill needs
- Required: entity-level data (or events to aggregate), the purpose
- Optional: preferred number of segments

# Output
Segment profile table, a chart (scatter of 2 main variables coloured by segment, or a heatmap of standardized profiles), segment labels saved to `segments.csv`.
