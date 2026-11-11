# Pre-call model for term-deposit subscription

**Question:** Before a call is made, can we predict which clients will subscribe to a term deposit, how much better is that than a naive baseline, and which factors matter most?

## Answer

Yes. A gradient-boosting model that uses only information known before the call ranks clients well. Calling the top 10% of clients by model score reaches about 4.5 times the subscription rate of calling at random, and captures 45% of all subscribers. Calling the top 20% captures 60%.

For a campaign run within one period, I recommend the **no-macro** model (ROC AUC 0.784). The version that also uses national economic indicators scores higher (AUC 0.813), but most of that gain comes from identifying the campaign period, not from separating clients within it (see caveats).

| Model (held-out 20% test set, n = 8,238) | ROC AUC | Subscribers in top 10% called | Lift in top 10% | Share of subscribers captured by top 10% / top 20% |
|---|---|---|---|---|
| Baseline A: predict "no" for everyone | 0.50 | 11.3% | 1.0x | 10% / 20% (no ranking) |
| Baseline B: call in random order | 0.50 | 12.1% | 1.1x | 11% / 23% |
| Baseline C: rule "previous campaign succeeded" | 0.57 | 27.3% | 2.4x | 24% / 32% |
| Logistic regression, no macro | 0.765 | 49.2% | 4.4x | 44% / 57% |
| **Gradient boosting, no macro (recommended)** | **0.784** | **50.7%** | **4.5x** | **45% / 60%** |
| Gradient boosting, with macro | 0.813 | 54.5% | 4.8x | 48% / 67% |

Five-fold cross-validation on the training set gives a stable ROC AUC for the recommended model: 0.773 ± 0.003. A cross-check on the other file (`bank-full.csv`, 45,211 rows, no macro indicators) gives 0.795 AUC, a top-10% lift of 4.4x, and 44% of subscribers captured in the top 10%. The result holds on the second dataset.

**Accuracy is the wrong yardstick here.** Only 11.3% of clients subscribe, so "predict no for everyone" is 88.7% accurate and beats every model on accuracy. For prioritising calls, the right measures are ranking (AUC) and subscribers captured per call.

## Which factors matter most

Permutation importance on the test set, recommended model (drop in ROC AUC when the feature is shuffled):

| Rank | Factor | AUC drop | What the data shows |
|---|---|---|---|
| 1 | Month of last contact | 0.087 | Mar, Sep, Oct, Dec: 44–51% subscribe. May: 6.4%. Jun–Aug: about 9–11%. |
| 2 | Contact type | 0.060 | Cellular: 14.7% subscribe. Telephone: 5.2%. |
| 3 | Age | 0.014 | Under 25: 21%. 65 and over: 47%. Ages 25–55: 8–12%. |
| 4 | Credit in default (`default`) | 0.009 | "No": 12.9% subscribe. "Unknown" (8,597 clients): 5.2%. Only three clients have "yes". |
| 5 | Campaign contacts this period | 0.008 | Falls with more calls: 13% at one contact, 12% at two, 9% at 4–5, 3% at more than 10. |
| 6 | Previously contacted (flag) | 0.007 | Prior contact is associated with a higher rate. |

Other drivers from the logistic model: a previous campaign success (65% subscribe, against 9% for clients never contacted before); students (31%) and retirees (25%) subscribe more than the average; blue-collar workers (7%) and services (8%) less.

With macro indicators included, the national employment level (`nr.employed`) becomes the strongest factor (AUC drop 0.058), followed by consumer price index, contact type, and employment variation rate.

## Method

- **Data:** `data/bank-additional/bank-additional-full.csv` (41,188 clients, May 2008–Nov 2010). This is the most complete version: it includes all 20 inputs, including five national economic indicators. The 12 exact duplicate rows were kept, since distinct clients can share all recorded attributes. There are no nulls. Missing values are coded as "unknown" and kept as a category.
- **Leakage control:** `duration` (call length in seconds) is excluded. The codebook says it is known only after the call, and it would make the model look near-perfect. The model uses only information available before dialling.
- **Feature engineering:** `pdays` = 999 means "never contacted before", so it is split into a flag plus a cleaned day count.
- **Split:** stratified 80/20 train/test (seed 42). Metrics are on the test set only; cross-validation is on the training set.
- **Models:** logistic regression (one-hot categories, standardised numbers) and histogram gradient boosting, both in scikit-learn.
- **Baselines:** predict "no" for everyone (naive accuracy), random call order, and the business rule "call previous successes first".

## Caveats

1. **Macro indicators are time proxies.** The five economic indicators take one value per quarter or month, and they track the campaign period. Subscription ranges from 3% to 57% across the observed employment-level groups (`nr.employed`). Within one campaign every client shares the same indicator values, so they cannot rank clients against each other. Their contribution to the all-client AUC is therefore mostly about period, not client choice. For a future campaign you would need to forecast those indicators, and the model would extrapolate outside the 2008–2010 range. I recommend the no-macro model for the call list.
2. **Time confounding in `month`.** Month also reflects campaign waves (May 2008–Nov 2010 are unevenly represented), so it may partly describe the period rather than a stable seasonal effect.
3. **Random split, not time-based.** The data has no full date (only day and month), so a time-ordered validation was not possible. Performance on a future campaign may be lower.
4. **Association, not causation.** These are historical campaign records. Factors like cellular contact or previous success are predictive, but calling a client differently will not necessarily change their decision.
5. **Importance is shared among correlated features.** `poutcome`, `pdays` and `previous` overlap, so their individual importance is understated. Permutation importance ranks features; it does not estimate causal effects.
6. **Calibration.** Scores are ranking scores. Use the top-decile lift for prioritisation rather than treating each score as a probability.

## Files

- `analysis.py`: the full pipeline (reproduces every number here)
- `model_metrics.csv`: metrics for all models and datasets
- `lift_by_decile.csv`: lift and cumulative capture by score decile (with-macro model)
- `permutation_importance.csv`, `logistic_coefficients.csv`: factor rankings and directions
- `roc_and_gains.png`, `feature_importance.png`: charts (gains curve and ROC are for the with-macro model)
- `run_summary.json`: dataset sizes and base rates
