# Sapir-Program

This repository contains a Streamlit dashboard for analyzing running events.

Important notes
- The CSV data files (`data.csv`, `data2.csv`) are intentionally excluded from this repository and are listed in `.gitignore`.
- The largest data file currently included is `data.parquet` (≈61 MB). Consider using Git LFS if you want to keep large files under version control.

Main runnable scripts
- `runners_dashboardXYZ.py` — the last full running version of the dashboard (recommended to run).
- `runners_dashboard.py` — the current version with dynamic boxplot UI.
- `runners_dashboardXY.py` — auxiliary variant(s).

How to run (PowerShell)

1. Create a Python virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements_dashboard.txt
```

3. Run the Streamlit app (replace filename if you prefer a different entry):

```powershell
streamlit run runners_dashboardXYZ.py
```

If the app cannot find local data files, place `data.csv` (or `data2.csv`) next to the script, or modify the `DATA_PATH` variable in the script to point to your data location.

Notes for maintainers
- If you need to remove large files from the remote history, consider using the BFG Repo Cleaner or `git filter-branch` and then force-pushing. Proceed with caution — rewriting remote history affects collaborators.
- To manage large assets, consider adding Git LFS and migrating `data.parquet` to LFS.

Contact
- Repository pushed by local workflow on your machine. If you'd like me to update the README further, add examples, or include screenshots, tell me what to include.
