"""Quick overview of a data file or folder, to check whether it can answer a question.

Usage: python inspect_data.py <file-or-folder> [--rows 5] [--max-files 30]
Supports CSV/TSV/TXT, Excel (each sheet), JSON/JSONL, Parquet. Read-only.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

try:  # Windows consoles default to cp1252; force UTF-8 output
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_colwidth", 40)

TABULAR = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".json", ".jsonl", ".parquet"}
DOCS = {".md", ".pdf", ".docx", ".html", ".rtf"}
NA = ["?", "NA", "N/A", "null", "NULL", "", "-"]


def load(path: Path) -> dict:
    """Return {name: DataFrame}; Excel files may give several sheets."""
    s = path.suffix.lower()
    if s in {".xlsx", ".xls"}:
        return {f"{path.name}[{k}]": v for k, v in pd.read_excel(path, sheet_name=None).items()}
    if s == ".parquet":
        return {path.name: pd.read_parquet(path)}
    if s == ".jsonl":
        return {path.name: pd.read_json(path, lines=True)}
    if s == ".json":
        try:
            return {path.name: pd.read_json(path)}
        except ValueError:
            return {path.name: pd.read_json(path, lines=True)}
    last = None
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            df = pd.read_csv(path, sep=None, engine="python", na_values=NA, encoding=enc)
            if enc != "utf-8":
                print(f"(note: {path.name} read with encoding={enc})")
            return {path.name: df}
        except UnicodeDecodeError as e:
            last = e
    raise last


def hints(df: pd.DataFrame) -> list:
    out = []
    n = len(df)
    for c in df.columns:
        lc = str(c).lower()
        nun = df[c].nunique(dropna=True)
        id_name = lc.startswith("id") or lc.endswith("id") or "_id" in lc or lc.endswith(("code", "key"))
        datey = any(k in lc for k in ("date", "time"))
        if n and nun == n and df[c].notna().all() and not pd.api.types.is_float_dtype(df[c]) \
                and (id_name or (n >= 50 and not datey)):
            out.append(f"`{c}` is unique per row -> likely ID/key")
        elif id_name:
            out.append(f"`{c}` looks like an ID (not unique: {nun} distinct / {n} rows)")
        if not pd.api.types.is_numeric_dtype(df[c]) and any(k in lc for k in ("date", "time", "day", "month", "year")):
            parsed = pd.to_datetime(df[c], errors="coerce")
            if parsed.notna().mean() > 0.8:
                out.append(f"`{c}` parses as dates: {parsed.min()} -> {parsed.max()}")
        if 2 <= nun <= 10 and any(k in lc for k in ("result", "status", "label", "target", "outcome", "class", "pass", "grade")):
            out.append(f"`{c}` could be an outcome/target: {df[c].value_counts().to_dict()}")
    return out


def describe(name: str, df: pd.DataFrame, rows: int) -> None:
    print(f"\n{'=' * 80}\n{name}: {df.shape[0]:,} rows x {df.shape[1]} columns")
    dup = int(df.duplicated().sum())
    if dup:
        print(f"! {dup:,} fully duplicated rows")
    summary = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing%": (df.isna().mean() * 100).round(1),
        "unique": df.nunique(dropna=True),
        "example": [", ".join(map(str, df[c].dropna().unique()[:4])) for c in df.columns],
    })
    num = df.select_dtypes("number")
    if not num.empty:
        summary.loc[num.columns, "min"] = num.min()
        summary.loc[num.columns, "max"] = num.max()
        summary.loc[num.columns, "mean"] = num.mean().round(3)
    print(summary.to_string())
    print(f"\nFirst {rows} rows:")
    print(df.head(rows).to_string())
    h = hints(df)
    if h:
        print("\nHints:")
        for x in h:
            print("  -", x)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--rows", type=int, default=5)
    ap.add_argument("--max-files", type=int, default=30)
    a = ap.parse_args()

    p = Path(a.path)
    if not p.exists():
        sys.exit(f"Not found: {p}")
    files = [p] if p.is_file() else sorted(f for f in p.rglob("*") if f.is_file())

    docs = [f for f in files if f.suffix.lower() in DOCS or "readme" in f.name.lower()]
    data = [f for f in files if f.suffix.lower() in TABULAR and f not in docs]
    other = [f for f in files if f not in docs and f not in data]

    print(f"Path: {p}  |  data files: {len(data)}  docs: {len(docs)}  other: {len(other)}")
    if docs:
        print("Documentation to read (column meanings):", *[f"  - {d}" for d in docs], sep="\n")
    if other:
        print("Not inspected:", ", ".join(f.name for f in other[:20]))

    for f in data[: a.max_files]:
        try:
            for name, df in load(f).items():
                describe(name, df, a.rows)
        except Exception as e:
            print(f"\n{'=' * 80}\n{f.name}: could not read ({e})")
    if len(data) > a.max_files:
        print(f"\n... {len(data) - a.max_files} more data files not shown (use --max-files)")

    if len(data) > 1:
        print(f"\n{'=' * 80}\nColumns shared across files (possible join keys):")
        cols = {}
        for f in data[: a.max_files]:
            try:
                for name, df in load(f).items():
                    for c in df.columns:
                        cols.setdefault(c, []).append(name)
            except Exception:
                pass
        shared = {c: v for c, v in cols.items() if len(v) > 1}
        for c, v in shared.items():
            print(f"  `{c}`: {', '.join(v)}")
        if not shared:
            print("  none")


if __name__ == "__main__":
    main()
