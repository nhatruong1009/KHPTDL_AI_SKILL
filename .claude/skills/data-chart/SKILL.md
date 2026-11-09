---
name: data-chart
description: Create clear, publication-ready charts with matplotlib/seaborn - pick the chart type from the message, build it from computed data, apply visual hierarchy, annotate, and save a PNG. Use when asked to plot/draw/visualize/show data, or when a chart makes an answer clearer.
argument-hint: <message the chart must show>
---

# Data Chart (visualization-builder, simplified)

# When to use
- The user asks for a chart/plot/visual
- A result (trend, comparison, distribution) reads better as a picture
- An existing chart is cluttered or misleading

# Process
1. **Name the message** - one sentence the chart must prove (e.g. "Module CCC has the highest withdrawal rate").
2. **Pick the type from the message**:

   | Message | Chart |
   |---|---|
   | comparison across categories | bar, sorted; horizontal if labels are long or > 6 bars |
   | trend over time | line (<= 6 series) |
   | distribution | histogram / box plot |
   | relationship | scatter (alpha for many points) + optional trend line |
   | part of whole (<= 5 parts) | 100% stacked bar (avoid pie) |
   | two categoricals | annotated heatmap of row % |
   | cohort / correlation matrix | heatmap |
   | model results | confusion matrix, ROC/PR curve, feature-importance bar |
3. **Prepare the data first** - aggregate in pandas to the right grain; plot only computed values, never hand-typed numbers.
4. **Build & design** - `matplotlib.use("Agg")`, `sns.set_theme(style="whitegrid")`, colorblind palette; remove top/right spines; highlight the key bar/line in a strong color and grey the rest; % axes formatted as %.
5. **Annotate** - the title states the finding; axis labels with units; value labels when there are few bars; n and data source in a caption; reference lines (average, target) where useful.
6. **Export & check** - `savefig(dpi=150, bbox_inches="tight")` to `outputs/<slug>/<name>.png`; open the PNG (Read tool) and check the message is clear in 5 seconds, with no overlapping labels; fix and re-save.

Run with `python`.

# Inputs the skill needs
- Required: the computed data (or the script that produces it); the key message
- Optional: audience, required style

# Output
PNG chart(s) in `outputs/<slug>/`, linked in the answer.
