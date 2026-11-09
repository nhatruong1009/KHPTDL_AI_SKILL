---
name: root-cause
description: Investigate why a metric changed or why it is low/high for some group - validate the change, find when it started, decompose the metric, drill down by dimensions ranked by contribution, and test hypotheses. Use for "why did X drop/rise", "what drives X", "why is group Y worse" questions.
argument-hint: <metric and change to explain>
---

# Root Cause Investigation

# When to use
- "Why did the pass rate drop in 2014?"
- "Why is module X worse than the others?"
- A metric moved and someone needs an evidence-based explanation

# Process
1. **Validate the change** - compare against normal variation (previous periods / rolling mean +/- std). If it's within normal range, say so and stop.
2. **Timeline** - compute the metric per period; find when the change started (sudden step = an event; gradual drift = a structural shift).
3. **Decompose the metric** - split into components (e.g. pass rate = passes / registrations; average score = mix of groups x each group's score). Find which component moved.
4. **Drill down** - compare before vs after (or group vs rest) across every available dimension; rank segments by **contribution** = change in the segment's metric x the segment's share. Separate *mix shift* (the group composition changed) from *rate change* (the groups themselves got worse).
5. **Test hypotheses** - list candidates (volume change, mix shift, a specific segment, data issue such as missing periods or code changes); accept or reject each with numbers. Check the data issue hypothesis first.
6. **Conclude** - the primary driver with its quantified share, supporting evidence, rejected hypotheses, and what can't be determined from this data. Use "associated with" language; the data rarely proves the cause.

Run with `python` in `outputs/<slug>/analysis.py`.

# Inputs the skill needs
- Required: metric, the period or group showing the change, dimension columns
- Optional: known events in that period

# Output
- Metric timeline chart and a contribution table (segment, before, after, change, share of total change)
- Short driver statement + rejected hypotheses + limits
