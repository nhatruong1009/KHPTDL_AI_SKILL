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
2. **Remove leakage** - drop columns that reveal or come after the outcome (final scores, status/result fields, end/withdrawal dates, whole-period totals, IDs). List what was dropped and why.
3. **Split before fitting** - stratified `train_test_split` (test 20%) for classification; split by time for future prediction; `GroupShuffleSplit` when one entity has many rows. Put imputation, scaling, and encoding inside a `Pipeline`/`ColumnTransformer` (fit on train only).
4. **Models, simple first** - `DummyClassifier`/`DummyRegressor` baseline -> `LogisticRegression` (`class_weight="balanced"` if imbalanced) / `Ridge` -> `RandomForest` or `HistGradientBoosting` only if clearly better. `random_state=42`; optional 5-fold CV on train; evaluate on test once.
5. **Evaluate** - classification: confusion matrix, precision/recall/F1 per class, ROC-AUC, PR-AUC if imbalanced; say which error matters more. Regression: MAE, RMSE, R^2. Always show the baseline next to the model.
6. **Explain** - top 10 features (coefficients or `permutation_importance` on test); wording "helps predict", not "causes"; limits (test size, imbalance, missing features, generalization).

Run with `python` in `outputs/<slug>/model.py`.

# Inputs the skill needs
- Required: target column, candidate features
- Optional: prediction moment, which error is costlier

# Output
Metrics table (baseline vs models), confusion matrix or residual plot, feature-importance chart, 2-3 line verdict: can it be predicted, and how well.
