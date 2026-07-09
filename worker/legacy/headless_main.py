"""
Headless entry point for the legacy SnapShot pipeline.

Reads job JSON (addresses + financial inputs), runs the processing portion of
address_capture_v1.58.py without Chrome capture or tkinter, and writes output.json.

Usage:
    python -m worker.legacy.headless_main /path/to/job.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

LEGACY_SCRIPT = Path(__file__).resolve().parent / "address_capture_v1.58.py"
SPLIT_MARKER = "SCRIPT SHOULD BE SPLIT HERE"


def _load_legacy_sections() -> tuple[str, str]:
    lines = LEGACY_SCRIPT.read_text(encoding="utf-8").splitlines()
    split_idx = next(i for i, line in enumerate(lines) if SPLIT_MARKER in line)
    import_block = "\n".join(lines[1:34])  # skip module docstring line
    pipeline_code = "\n".join(lines[split_idx + 2 :])
    return import_block, pipeline_code


def _inputs_namespace(inputs: dict[str, Any]) -> dict[str, Any]:
    addresses = [a.strip() for a in inputs.get("addresses", []) if a and str(a).strip()]
    if not addresses:
        raise ValueError("At least one address is required")

    return {
        "results": addresses,
        "user_em": inputs.get("recipient_email") or "",
        "interest_rate": float(inputs.get("interest_rate", 0.06)),
        "years": int(inputs.get("years", 30)),
        "discount_percentage": float(inputs.get("discount_percentage", 0.25)),
        "closing_costs_input": float(inputs.get("closing_costs_input", 0.04)),
        "money_down_input": float(inputs.get("money_down_input", 0.2)),
        "operating_expenses_input": float(inputs.get("operating_expenses_input", 0.02)),
        "additional_annual_income_input": float(inputs.get("additional_annual_income_input", 0)),
        "vacancy_allowance_percent_input": float(inputs.get("vacancy_allowance_percent_input", 0.05)),
        "lender_ltv_input": float(inputs.get("lender_ltv_input", 0.75)),
        "rehab_costs_est_input": float(inputs.get("rehab_costs_est_input", 0.25)),
        "refi_loan_amount_input": float(inputs.get("refi_loan_amount_input", 0.5)),
        "refi_closing_costs_est_input": float(inputs.get("refi_closing_costs_est_input", 0.04)),
        "num_months_holding": int(inputs.get("num_months_holding", 3)),
        "test_mode": 0,
    }


def _rows_from_listings(listings) -> list[dict[str, Any]]:
    import numpy as np
    import pandas as pd

    rows: list[dict[str, Any]] = []
    for record in listings.to_dict(orient="records"):
        clean: dict[str, Any] = {}
        for key, value in record.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                clean[key] = None
            elif pd.isna(value):
                clean[key] = None
            elif isinstance(value, (np.integer, np.floating)):
                clean[key] = value.item()
            else:
                clean[key] = value
        rows.append(clean)
    return rows


def _files_from_work_dir(work_dir: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for pdf in sorted(work_dir.glob("*.pdf")):
        files.append({"file_type": "pdf", "filename": pdf.name, "local_path": str(pdf), "s3_key": None})
    xlsx = work_dir / "Listings Report Data.xlsx"
    if xlsx.exists():
        files.append({"file_type": "xlsx", "filename": xlsx.name, "local_path": str(xlsx), "s3_key": None})
    return files


def run_job_config(config: dict[str, Any]) -> dict[str, Any]:
    work_dir = Path(config["work_dir"])
    work_dir.mkdir(parents=True, exist_ok=True)

    import_block, pipeline_code = _load_legacy_sections()
    namespace: dict[str, Any] = {
        "__name__": "__main__",
        "__file__": str(LEGACY_SCRIPT),
    }

    exec(compile(import_block, str(LEGACY_SCRIPT), "exec"), namespace)
    namespace.update(_inputs_namespace(config.get("inputs", {})))

    original_cwd = Path.cwd()
    try:
        import os

        os.chdir(work_dir)
        exec(compile(pipeline_code, str(LEGACY_SCRIPT), "exec"), namespace)
    finally:
        import os

        os.chdir(original_cwd)

    listings = namespace.get("listings")
    import pandas as pd

    if listings is None or not isinstance(listings, pd.DataFrame):
        raise RuntimeError("Legacy pipeline did not produce a listings dataframe")

    return {
        "rows": _rows_from_listings(listings),
        "files": _files_from_work_dir(work_dir),
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: python -m worker.legacy.headless_main <job.json>")

    config_path = Path(sys.argv[1])
    with config_path.open(encoding="utf-8") as handle:
        config = json.load(handle)

    output = run_job_config(config)
    out_path = Path(config["work_dir"]) / "output.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, default=str)


if __name__ == "__main__":
    main()
