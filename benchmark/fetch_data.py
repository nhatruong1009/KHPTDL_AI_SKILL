"""Download the REAL benchmark datasets from public online sources.

Every task gets its own folder benchmark/data/<task_id>/ holding the files
exactly as the source publishes them (archives are extracted, nested
archives too). Nothing is cleaned - the messiness is the point.

Sources (no login needed):
  - UCI Machine Learning Repository (classic public problems)
  - TidyTuesday weekly data challenge (rfordatascience/tidytuesday)
  - World Bank Open Data API

    python -I benchmark/fetch_data.py            # all tasks
    python -I benchmark/fetch_data.py retail_uk  # one task
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TT = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data"
WB = "https://api.worldbank.org/v2/en/indicator/{}?downloadformat=csv"
# prepared OULAD views from the N05 project (P3). Only data/processed is copied - no README,
# dictionary, decision logs or P4 results, so the agent starts from the data alone.
OULAD_P3 = Path(os.environ.get("OULAD_P3_DIR", ROOT.parent.parent / "da-oulad-early-warning" / "P3" / "data" / "processed"))

SOURCES: dict[str, dict] = {
    # Online Retail II - UK online gift shop, 2009-2011, 2 Excel sheets, ~1M lines
    "retail_uk": {
        "topic": "E-commerce / retail",
        "origin": "UCI #502 Online Retail II",
        "files": [("https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip", "zip")],
    },
    # Student Performance - 2 Portuguese schools, math + Portuguese course files
    "student_perf": {
        "topic": "Education",
        "origin": "UCI #320 Student Performance (Cortez & Silva, 2008)",
        "files": [("https://archive.ics.uci.edu/static/public/320/student+performance.zip", "zip")],
    },
    # Household power - 1 house, minute readings 2006-2010, '?' as missing, ';' separated
    "household_power": {
        "topic": "Energy / time series",
        "origin": "UCI #235 Individual Household Electric Power Consumption",
        "files": [("https://archive.ics.uci.edu/static/public/235/individual+household+electric+power+consumption.zip", "zip")],
    },
    # World Bank - 3 indicators, each a zip with data + country metadata (aggregates mixed in)
    "worldbank_health": {
        "topic": "Public health / development economics",
        "origin": "World Bank WDI: SP.DYN.LE00.IN, SH.XPD.CHEX.PC.CD, NY.GDP.PCAP.PP.CD",
        "files": [(WB.format("SP.DYN.LE00.IN"), "zip:life_expectancy"),
                  (WB.format("SH.XPD.CHEX.PC.CD"), "zip:health_expenditure_per_capita"),
                  (WB.format("NY.GDP.PCAP.PP.CD"), "zip:gdp_per_capita_ppp")],
    },
    # Himalayan Database - expeditions / members / peaks, 1905-2019
    "himalaya": {
        "topic": "Mountaineering / sports & safety",
        "origin": "TidyTuesday 2020-09-22 (The Himalayan Database)",
        "files": [(f"{TT}/2020/2020-09-22/{f}", "raw") for f in
                  ("expeditions.csv", "members.csv", "peaks.csv", "readme.md")],
    },
    # Wine Quality - red + white Vinho Verde physicochemical tests (relevance-gate task)
    "wine_quality": {
        "topic": "Food & beverage (relevance gate)",
        "origin": "UCI #186 Wine Quality (Cortez et al., 2009)",
        "files": [("https://archive.ics.uci.edu/static/public/186/wine+quality.zip", "zip")],
    },
    # Bank Marketing - Portuguese bank telemarketing, documented leakage column 'duration'
    "bank_marketing": {
        "topic": "Banking / marketing prediction",
        "origin": "UCI #222 Bank Marketing (Moro et al., 2014)",
        "files": [("https://archive.ics.uci.edu/static/public/222/bank+marketing.zip", "zip")],
    },
    # OULAD early warning - prepared analytic views (BBB+FFF, 2013B-2014J), local copy from project P3
    "oulad_early_warning": {
        "topic": "Education / early warning (prepared data)",
        "origin": "OULAD (Kuzilek et al., 2017, CC BY 4.0) - N05 prepared views, P3/data/processed only",
        "files": [(str(OULAD_P3), "local_dir")],
    },
}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "dataset-benchmark/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def _extract(blob: bytes, dest: Path) -> list[str]:
    """Extract a zip, recursing into nested zips; skip __MACOSX junk."""
    names = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for info in z.infolist():
            n = info.filename
            if info.is_dir() or n.startswith("__MACOSX") or "/." in n or n.startswith("."):
                continue
            target = (dest / n).resolve()
            if dest.resolve() not in target.parents:  # zip-slip guard
                continue
            data = z.read(info)
            if n.lower().endswith(".zip"):
                names += _extract(data, dest)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            names.append(str(target.relative_to(dest.resolve())))
    return names


def fetch(task: str) -> dict:
    spec = SOURCES[task]
    dest = DATA / task
    dest.mkdir(parents=True, exist_ok=True)
    manifest = {"task": task, "topic": spec["topic"], "origin": spec["origin"], "downloads": []}
    for url, kind in spec["files"]:
        print(f"  {task}: {url}", flush=True)
        if kind == "local_dir":  # flat copy of a local folder (files only, no subfolders)
            src = Path(url)
            if not src.is_dir():
                raise SystemExit(f"{task}: local source {src} not found - set OULAD_P3_DIR")
            files = sorted(f for f in src.iterdir() if f.is_file() and not f.name.startswith("."))
            for f in files:
                shutil.copy2(f, dest / f.name)
            manifest["downloads"].append({"local_dir": str(src), "files": [
                {"name": f.name, "bytes": f.stat().st_size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]})
            continue
        blob = _get(url)
        entry = {"url": url, "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
        if kind == "raw":
            (dest / url.rsplit("/", 1)[1]).write_bytes(blob)
        elif kind == "zip":
            entry["files"] = _extract(blob, dest)
        elif kind.startswith("zip:"):
            sub = dest / kind.split(":", 1)[1]
            sub.mkdir(exist_ok=True)
            entry["files"] = _extract(blob, sub)
        manifest["downloads"].append(entry)
    return manifest


def main() -> None:
    tasks = sys.argv[1:] or list(SOURCES)
    manifests = {}
    mpath = ROOT / "data_manifest.json"
    if mpath.exists():
        manifests = json.loads(mpath.read_text())
    for t in tasks:
        manifests[t] = fetch(t)
    mpath.write_text(json.dumps(manifests, indent=2))
    for t in tasks:
        files = sorted(p.relative_to(DATA / t) for p in (DATA / t).rglob("*") if p.is_file())
        print(t, "->", [str(f) for f in files])


if __name__ == "__main__":
    main()
