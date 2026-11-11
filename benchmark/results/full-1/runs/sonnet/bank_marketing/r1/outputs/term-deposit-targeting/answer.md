# Who should the call centre phone? Pre-call subscription model

## Answer
A model built only on information available before dialling ranks clients meaningfully better than a naive baseline, but less than a casual cross-validation would suggest.

- **Realistic test (train on the earliest 70% of calls, test on the latest 30%):** ROC-AUC 0.66 (logistic regression) / 0.64 (gradient boosting) vs 0.50 for the naive baseline. Calling the top-scored 10% of clients gave a **46.6% subscription rate vs 24.6% for calling at random (1.9x lift)**. The top 20% gave 44.4%.
- **Optimistic test (random 5-fold CV, gradient boosting):** AUC 0.80, PR-AUC 0.46 vs 0.11 baseline (the subscription rate). Random folds mix time periods, so this overstates what you'd get on a future campaign. Treat 0.64–0.66 AUC as the planning number.
- **Naive baseline:** call everyone equally (or predict "no" for all). Overall subscription rate is 11.3%, so "always no" is 88.7% accurate but finds no buyers, which is why I judge on ranking (AUC, lift) rather than accuracy.

## Which factors matter most
Permutation importance (drop in held-out AUC, gradient boosting, `permutation_importance.csv`):
1. **Month of contact** (0.056) and **days since previous contact** (0.034), the strongest.
2. **Age** (0.022), **job** (0.011), **contact type** (0.007), **previous-campaign outcome** (0.005).

Raw conversion rates (`conversion_by_factor.csv`, whole dataset; association only):
- Previous campaign success: **65%** vs 8.8% for never contacted before. Anyone previously contacted: 64% vs 9%.
- Cellular 14.7% vs telephone 5.2%.
- Students 31% and retirees 25% vs blue-collar 6.9%.
- Mar/Sep/Oct/Dec convert at 44–51% but are tiny months (≤718 calls each). May is 6.4% on 13,769 calls.

Macro indicators (euribor, employment) did not help on the later-period test: removing them left AUC the same or higher (0.653 vs 0.637).

## Method
- Data: `bank-additional/bank-additional-full.csv`, the most complete version (41,188 rows, 20 inputs plus macro-economic indicators; the other files are subsets or older versions with fewer columns). 12 duplicate rows left in.
- Target: `y` (subscribed). Rows are ordered by date, so I split by time.
- **Excluded `duration`** (call length is only known after the call) and **`campaign`** (counts the current call's contacts). Both would inflate performance and be unusable for planning.
- Models: logistic regression and gradient boosting (HistGradientBoosting), compared against a constant-rate baseline. Bootstrap 95% CI for gradient-boosting AUC: 0.627–0.650.

## Caveats
- **Large drift:** the subscription rate is 5.6% in the training period vs 24.6% in the test period. Models rank well below what random CV shows because the client mix and conditions changed. Re-train on recent data, and check the lift on a small pilot before relying on it.
- Month and macro conditions reflect 2008–2010 Portuguese market conditions. A "month" effect might be campaign timing or selection (who gets called) and not something you can change by choosing when to call.
- Calibration is poor under drift (decile 1 predicted ≈27% vs 43% actual), so use scores for ranking, not as probabilities.
- Observational data: factors are associated with subscription, not shown to cause it.
- Previously contacted clients are only 3.7% of rows; their high conversion rate is robust but covers few clients.
- Gradient boosting was not tuned; logistic regression did slightly better on the later period, so more complexity wasn't clearly useful.

Files: `analysis.py`, `model_comparison_temporal.csv`, `decile_lift.csv`, `permutation_importance.csv`, `conversion_by_factor.csv`, `model_summary.png`.
