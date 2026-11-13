---
name: data-predict
description: Build and evaluate a predictive model (classification or regression) with scikit-learn when a question asks to predict an unknown or future value - define target and prediction moment, remove leakage, split correctly, compare against a baseline, report metrics and top features. Use only when the question genuinely requires prediction.
argument-hint: <what to predict>
---

# Data Predict

# When to use
- "Can we predict which students will fail/withdraw?"
- "Estimate the score/value for new cases"
- NOT for "what is associated with Y" -> that is `/group-compare` or `/root-cause`

# Process
1. **Define** - target (classification or regression; show its distribution and imbalance), unit (one row = ?; aggregate events first), **prediction moment** (only features known before it are allowed).
2. **Remove leakage - feature timing audit** - make a table `feature | known when? | keep/drop | why`.
   - Drop columns that reveal or come after the outcome (final scores, status/result fields, end/withdrawal dates, whole-period totals, IDs).
   - A feature whose availability at the prediction moment is **unknown or unverifiable** (e.g. a grade whose release date is not in the data) is **not** in the main model; fit it only as a labelled sensitivity variant and compare.
   - Sensitive attributes (gender, age, disability, ethnicity, deprivation, region) are not predictors; keep them aside for a per-group error audit.
3. **Split before fitting** - if the data has a split/period/fold column, **use it as given**. Otherwise: split by time (or by later cohort/term) for future prediction; `GroupShuffleSplit` when one entity has many rows; stratified `train_test_split` (test 20%) only when rows are truly exchangeable. Put imputation, scaling, encoding (and log1p for skewed counts) inside a `Pipeline`/`ColumnTransformer` fit on train only. Check drift: base rate and the top features' distributions train vs test.
4. **Models, simple first** - `DummyClassifier`/`DummyRegressor` baseline -> `LogisticRegression` (`class_weight="balanced"` if imbalanced) / `Ridge` -> `RandomForest` or `HistGradientBoosting` only if clearly better. `random_state=42`; optional 5-fold CV on train; evaluate on test once.
5. **Evaluate** - pick the model and any decision threshold (e.g. "recall >= 70%") on validation, never on test; then report test once and say plainly whether the target holds on test. If the decision is a top-k list under capacity, rank within the unit the capacity applies to (per group/term) and report precision@k against that group's base rate. Classification: confusion matrix, precision/recall/F1 per class, ROC-AUC, PR-AUC if imbalanced; say which error matters more. Regression: MAE, RMSE, R^2. Always show the baseline next to the model.
6. **Explain** - top 10 features (coefficients or `permutation_importance` on test); wording "helps predict", not "causes"; limits (test size, imbalance, missing features, generalization).

Run with `python` in `outputs/<slug>/model.py`.

# Inputs the skill needs
- Required: target column, candidate features
- Optional: prediction moment, which error is costlier

# Output
Metrics table (baseline vs models), confusion matrix or residual plot, feature-importance chart, 2-3 line verdict: can it be predicted, and how well.
