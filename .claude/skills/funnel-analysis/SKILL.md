---
name: funnel-analysis
description: Funnel analysis - measure how entities progress through an ordered sequence of steps (e.g. register -> first login -> first assessment -> submit all -> pass), step-to-step and overall conversion, drop-off counts, time between steps, and segment differences. Use for "where do people drop out of the process" questions.
argument-hint: <ordered steps and entity>
---

# Funnel Analysis

# When to use
- A process has ordered steps and the question is where people stop
- Comparing completion of a process between groups

# Process
1. **Define steps & window** - the ordered list of events/conditions and how each is detected in the data; the time window to complete (e.g. within the course presentation). Write the definitions down - ambiguity here invalidates the result.
2. **Build the entity-level table** - for each entity that reached step 1: a flag (and timestamp if available) per step. A step counts only if all previous steps were reached (strict funnel), unless stated otherwise.
3. **Conversion** - per step: entities reached, step-to-step conversion (N / N-1), overall conversion from step 1, absolute drop-off.
4. **Time between steps** - median and P75/P90 where timestamps exist; long gaps signal friction even when drop-off is low.
5. **Segment** - the same funnel per group (module, region, device...); find where the worst group diverges from the best. Use `/group-compare` to test the key gap.
6. **Rank drop-offs** - by absolute numbers lost; summarize the biggest leak and the segment where it is worst.

Run with `python` in `outputs/<slug>/analysis.py`.

# Inputs the skill needs
- Required: entity ID, the step definitions (columns/events), timestamps if available
- Optional: time window, segments

# Output
Funnel table (step, reached, step conversion, overall conversion, drop-off), funnel bar chart (horizontal, decreasing), segment comparison, short summary.
