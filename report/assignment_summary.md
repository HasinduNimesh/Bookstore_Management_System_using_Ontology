# Bookstore Management System — Assignment Summary

This document maps each assignment requirement to the implementation inside this
repository and explains how to run and evaluate the simulation.

## 1. Environment setup & imports
- Python 3.11 virtual environment (`.venv`) with dependencies tracked in
  `requirements.txt` (root) and `ontology-mas-ui/backend/requirements.txt`.
- Key libraries: **Owlready2** (ontology), **Mesa** (multi-agent simulation),
  **FastAPI** (REST + WebSocket API), **hmmlearn** (HMM inference).
- Frontend tooling: React + Vite + Tailwind + Recharts for dashboard visuals.

### Quick start
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r ontology-mas-ui/backend/requirements.txt
npm install --prefix ontology-mas-ui/frontend
```

## 2. Ontology definition (`bms/ontology.py`)
- Classes: `Book`, `Customer`, `Employee`, `Order`, `Inventory`.
- Object properties: `purchases`, `worksAt`, `hasBook`, `orderedBy`, `forBook`.
- Data properties: `hasAuthor`, `hasGenre`, `hasPrice`, `availableQuantity`,
  `thresholdQuantity`, `restockAmount`, `quantity`, `needsRestock`.
- Helper `seed_from_json` creates individuals from `bms/data/seed_books.json`,
  wiring books to inventories and initializing stock thresholds.
- `save_ontology` exports the ontology snapshot (used in `bms/run.py`).

## 3. Agent implementation (`bms/agents.py`)
- `CustomerAgent` randomly selects books (with genre bias) and posts purchase
  requests via the message bus.
- `EmployeeAgent` processes purchases, decrements inventory, logs sales metrics,
  publishes purchase outcomes, and restocks low items.
- `BookAgent` encapsulates book metadata and is ready for future behaviors.
- Agents communicate through `MessageBus` (`bms/messaging.py`).

## 4. SWRL rules (`bms/rules.py`)
- **Low stock rule:** if an inventory quantity falls below its threshold,
  the ontology infers `needsRestock = true` using the built-in
  `swrlb:lessThan` predicate. Employees call `run_reasoner` and restock flagged
  items (with Python fallback if Pellet is unavailable).
- **Purchase rule:** an `Order` individual implies `purchases(Customer, Book)`,
  providing an audit trail of buyers to books.

## 5. Message bus (`bms/messaging.py`)
- Topics: `purchase_request`, `purchase_result`, `restock_done`.
- Simple publish/drain API keeps Mesa agents decoupled while still enabling
  deterministic replay in the simulation loop.

## 6. MAS model (`bms/model.py`)
- Builds ontology, seeds inventory, instantiates agents, registers them with the
  Mesa scheduler, tracks metrics (sales, stockouts, restocks, unique books in
  stock), and stores OWL customer handles for linking orders.
- `BMSModel.step()` advances schedule, collects metrics, and increments ticks.

## 7. Running the simulation
### From the command line
```powershell
python -m bms.run --steps 50 --customers 30
```
Outputs metrics, saves `report/bookstore.owl`, `report/run_summary.json`, and a
metrics plot in `report/figures/`.

### Via the web dashboard
Run backend and frontend (see README instructions). The React UI streams
simulation events, ontology diffs, and HMM KPIs in real time. Buttons allow you
to load the sample ontology, configure agent counts/ticks, and start/stop.

## 8. Evidence for marking rubric
| Criterion | Implementation evidence |
|-----------|-------------------------|
| **Ontology Definition (20)** | `bms/ontology.py`, exported `report/bookstore.owl` |
| **Agent Implementation (25)** | `bms/agents.py`, `bms/model.py`, message bus |
| **SWRL Rules (20)** | `bms/rules.py` low-stock & purchase rules, invoked in `EmployeeAgent._check_restock` |
| **Simulation Execution (15)** | `bms/run.py`, backend `/simulation` endpoints, real-time UI (screenshots in `report/figures/`) |
| **Documentation & Report (10)** | `README.md`, this summary, `report/report_template.md` filled by generated run |
| **Video Presentation (10)** | Script outline in `report/video_script.md`; run simulation with frontend to capture demo |

## 9. Next steps (optional)
- Enable automated Trivy/Scout scans for Docker images and pin safe digests.
- Expand BookAgent behavior (discounting, recommendations).
- Persist run histories to a database for longitudinal analysis.
