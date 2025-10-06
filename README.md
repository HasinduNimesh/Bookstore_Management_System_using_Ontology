# Bookstore Management System (BMS) — Ontology + Mesa + SWRL

This repository contains a **complete, rubric-aligned** implementation of a Bookstore Management System using
**Owlready2** (ontology + SWRL) and **Mesa** (multi-agent simulation).

> Created: 2025-09-29

## Quick start

```bash
# 1) Create a virtual env (recommended)
python -m venv .venv && source .venv/bin/activate   # (Linux/Mac)
# or: .venv\Scripts\activate                      # (Windows PowerShell)

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run a baseline simulation (prints summary + saves figures)
python -m bms.run --steps 40 --customers 30 --threshold 5 --restock 10
```

Outputs are written to `report/figures/` and a final **`run_summary.json`** is saved in `report/`.

## Project layout

```
bms_project/
  bms/
    agents.py
    messaging.py
    model.py
    ontology.py
    rules.py
    run.py
    experiments.py
    data/
      seed_books.json
  report/
    report_template.md
    video_script.md
  tests/
    test_smoke.py
requirements.txt
README.md
```

## What this implements

- **Ontology**: `Book, Customer, Employee, Order, Inventory` + required properties and a few helper ones.
- **SWRL rules**:
  - If `availableQuantity < thresholdQuantity` ⇒ mark `needsRestock = true` for that `Inventory`.
  - If an `Order` exists with `orderedBy` and `forBook` ⇒ assert `purchases(Customer, Book)` (audit trail).
- **Agents** (Mesa): `CustomerAgent`, `EmployeeAgent`, and `BookAgent` (lightweight, tracks book meta).
- **Message Bus**: In-memory pub/sub for `purchase_request`, `purchase_result`, `restock_request`, `restock_done`.
- **Simulation**: `BMSModel` with `RandomActivation`, `DataCollector`, deterministic seeding, and scenario runner.
- **Reports**: summary JSON + ready-to-fill markdown report and a 5–10 min video script.

> Notes: SWRL is used **declaratively** (e.g., low-stock inference). Arithmetic updates (decrement stock) are
> performed in Python after consulting the ontology, a common pattern for MAS + OWL setups.

## How to export the report to PDF

Open `report/report_template.md` in VS Code (or any Markdown editor) → **Export as PDF**,
or use Pandoc:

```bash
pandoc report/report_template.md -o report/BMS_Report.pdf
```

## License

For academic use in your course.


# Backend
Set-Location -Path 'f:\BMS_Project_Ready_To_Run\ontology-mas-ui\backend'
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
Set-Location -Path 'f:\BMS_Project_Ready_To_Run\ontology-mas-ui\frontend'
npm install    # once, if needed
npm run dev -- --host 0.0.0.0 --port 5173