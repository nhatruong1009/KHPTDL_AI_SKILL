---
name: storytelling
description: Turn verified analysis results into a short data story - one core message, a narrative arc (context, tension, insight, action), ordered findings, charts that each carry one point, and audience framing. Use after analysis and QA when the result will be presented or shared, or when asked for a story, narrative, presentation or report. Never invents or changes numbers.
argument-hint: <question or topic> [audience]
---

# Storytelling (narrative layer on top of answer-write)

# When to use
- Results must be presented to others (manager, class, report, slides)
- The user asks for a story, narrative, storyline or "explain it to non-technical people"
- Many findings exist and need an order and a single takeaway
- NOT for a quick factual answer - use /answer-write for that

# Process
1. **Get the facts first** - list verified findings with their numbers and n from the run outputs. If analysis or QA is not done, stop and run it first. The story only arranges facts; it never adds, rounds away or changes them.
2. **Find the one core message** - one sentence a reader could repeat: "<who/what> <does/changes> <how much>, because/so <why it matters>". If you cannot write it, the findings are not ready.
3. **Know the audience** - who they are, what they already know, what decision they face. Technical -> keep method visible. Non-technical -> plain words, fewer numbers, no jargon (explain p-value, correlation etc. in a phrase or drop them).
4. **Build the arc** - 4 beats:
   - Context: what we looked at and why it matters (1-2 sentences, the data scope)
   - Tension: the question, surprise or problem (what is not as expected)
   - Insight: the finding that resolves it, with the key number
   - Action: what to do or watch next (label as suggestion, not finding)
5. **Order the findings** - lead with the core message, then 2-4 supporting points from strongest to weakest, each one claim + one number + one chart. Cut true-but-irrelevant findings; park them in an appendix line.
6. **One chart, one point** - for each supporting point choose the chart with /data-chart. Title states the takeaway ("Retention drops 30% after week 3"), not the topic. Highlight the one series or bar that matters, mute the rest, annotate the key value.
7. **Make it concrete** - use comparisons the audience understands (per 100 students, 1 in 4, vs last term). Keep units and denominators explicit.
8. **Be honest** - keep the main caveats inside the story (small n, proxy used, association != causation). A story that hides a limit fails QA.
9. **Write it** - `outputs/<slug>/story.md` and a short chat reply. Run /answer-qa on the final text.

# Rules
- Every number in the story must trace to a run output.
- No causal words (because, caused, led to) unless the analysis supports causation; otherwise use "is associated with".
- One message per chart, one idea per paragraph.
- Do not dramatize; clear beats clever.

# Inputs the skill needs
- Required: verified analysis results (outputs, tables, charts) and the question
- Optional: audience (default: smart non-expert), format (short text, slide outline, report), length limit

# Output
```
**Core message:** one sentence
**Audience:** who, and what they need to decide

**1. Context** ...
**2. Tension** ...
**3. Insight** ... [chart](outputs/<slug>/x.png)
   - supporting point 1 (number, chart)
   - supporting point 2 (number, chart)
**4. Action (suggestion)** ...

**Caveats:** only those that could change the reading
```
