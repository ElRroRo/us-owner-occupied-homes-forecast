"""Rebuild everything from data/raw: inputs, rate path, model, chart, workbook.

The console output of the rate path and the model is saved to data/processed/*_run.log.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
LOGS = {"mortgage_path.py": "mortgage_path_run.log", "tenure_model.py": "model_run.log"}
STEPS = ["tenure_data.py", "mortgage_path.py", "tenure_model.py", "tenure_chart.py", "build_forecast_workbook.py"]

(ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
(ROOT / "outputs").mkdir(exist_ok=True)
for step in STEPS:
    print(f"== {step}", flush=True)
    run = subprocess.run([sys.executable, step], cwd=SRC, capture_output=True, text=True, encoding="utf-8")
    if run.returncode:
        sys.exit(f"{step} failed:\n{run.stderr}")
    if step in LOGS:
        (ROOT / "data" / "processed" / LOGS[step]).write_text(run.stdout, encoding="utf-8")
    else:
        print(run.stdout[-500:].strip())
print("done")
