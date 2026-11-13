import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = "outputs/du_doan_dang_ky_tien_gui/"
imp = pd.read_csv(D + "feature_importance_blockCV.csv").head(8).iloc[::-1]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(imp.feature, imp.giam_roc_auc, xerr=imp.sd_giua_fold, color="#2a6f97")
ax.set_title("Bối cảnh kinh tế (emp.var.rate, nr.employed, euribor3m) chi phối dự đoán")
ax.set_xlabel("Mức giảm ROC-AUC khi xáo trộn biến (CV theo khối thời gian)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(D + "feature_importance.png", dpi=150)
