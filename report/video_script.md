# Video Script — Bookstore Management System (Ontology + MAS + SWRL)

Duration: 8–10 minutes
Audience: Assignment evaluators (overview, implementation walkthrough, and demo)
Recording setup: Screen + mic, 1080p, system font scaling 100%

---

## 0:00–0:30 — Intro and Objectives
- On screen: Project root in VS Code (folder `BMS_Project_Ready_To_Run`).
- Voice-over:
  - “Hello, this is my Bookstore Management System built with an OWL ontology (Owlready2), SWRL rules, and a Mesa multi-agent simulation. I’ll briefly explain the architecture, show how to run it, and demonstrate the key features and outputs required by the rubric.”

---

## 0:30–1:30 — Architecture Overview (Slide or quick diagram)
- On screen: A simple diagram or the repo tree. Point to key parts while speaking.
- Voice-over:
  - “The system has three layers:
    1) Ontology layer: OWL ontology plus SWRL rules in Python using Owlready2.
    2) Agent-based simulation: Mesa model with Customer and Service agents.
    3) Web UI: FastAPI backend + React frontend to visualize the simulation and ontology state.
    Data and results are saved to the `report/` folder.”

Key folders to show briefly:
- `bms/` — agents, model, ontology, rules, runner.
- `ontology-mas-ui/backend/` — FastAPI app; ontology files in `data/`.
- `ontology-mas-ui/frontend/` — React app (Vite + Tailwind + Recharts).
- `report/` — outputs like `run_summary.json` and `figures/metrics.png`.

---

## 1:30–2:40 — Backend Setup (FastAPI)
- On screen: Terminal 1 (PowerShell). Navigate to backend and start API.
- Voice-over:
  - “First, I’ll run the backend API that serves ontology and simulation endpoints.”

Commands (narrate while typing):
```powershell
Set-Location -Path 'f:\BMS_Project_Ready_To_Run\ontology-mas-ui\backend'
# optional: python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Explain: “This starts the API at http://localhost:8000 with auto-reload.”

---

## 2:40–3:30 — Frontend Setup (React)
- On screen: Terminal 2 (PowerShell). Navigate to frontend and start dev server.
- Voice-over:
  - “Next, I’ll start the React frontend to visualize the simulation.”

Commands:
```powershell
Set-Location -Path 'f:\BMS_Project_Ready_To_Run\ontology-mas-ui\frontend'
npm install   # first run only
npm run dev -- --host 0.0.0.0 --port 5173
```
- Explain: “The app opens at http://localhost:5173. I’ll switch to the browser.”

---

## 3:30–5:00 — UI Tour and Ontology View
- On screen: Browser at the app home; show top bar and panels.
- Voice-over:
  - “This dashboard shows live simulation status. The Ontology Inspector lists classes and instances from the OWL model. You can click a class to view individuals and their properties.”
  - “We use SWRL rules declaratively. For example, if `availableQuantity < thresholdQuantity`, the system infers `needsRestock = true` for that inventory. Python code then handles arithmetic updates like decrementing stock on purchase.”
- Action: Click Ontology Inspector, select a couple of classes, show properties.

---

## 5:00–7:20 — Run the Simulation + HMM Behavior + Results
- On screen: In the app, click Start Simulation. Alternatively, run CLI simulation.
- Voice-over:
  - “When I start the simulation, Customer agents interact with the bookstore. Hidden Markov Model (HMM) states—Happy, Neutral, Unhappy—drive observable actions: Purchase, Complaint, or Silence. This is why you may see complaints—they’re part of realistic behavior.”
  - “The Event Type Summary counts purchases, complaints, and silences. The Simulation Summary modal shows charts including revenue and event distributions.”
- Action: Start simulation, wait a few ticks, open the Simulation Summary modal, highlight charts.

Optional CLI run to generate artifacts (Terminal 3):
```powershell
Set-Location -Path 'f:\BMS_Project_Ready_To_Run'
python -m bms.run --steps 40 --customers 30 --threshold 5 --restock 10
```
- Voice-over: “The CLI writes a summary JSON to `report/run_summary.json` and a metrics figure to `report/figures/metrics.png`.”
- Action: Show `report/run_summary.json` in VS Code and `metrics.png` in the viewer.

Key talking points while charts are visible:
- “Revenue trend may use fallback estimation if event-level price data is sparse, but the totals align with purchases.”
- “Complaints are expected from Neutral/Unhappy states based on emission probabilities.”

---

## 7:20–8:30 — Mapping to Rubric and Wrap-up
- Voice-over:
  - “Rubric coverage: Ontology definitions and SWRL rules (demonstrated in Ontology Inspector and code), agent-based simulation with message passing, data collection, and results reporting. The UI supports live inspection and exporting outputs.”
  - “For the full written explanation, see the final PDF report included in the repository README.”
- On screen: Show `ASSIGNMENT_REPORT.md` or the final PDF filename in the repo root.

---

## Appendix — Quick Troubleshooting (use as needed on voice-over)
- If the frontend can’t reach the backend: confirm backend is running on port 8000, frontend on 5173, and browser shows no CORS errors.
- If Python deps fail: activate venv and `pip install -r requirements.txt`.
- If Node deps fail: delete `node_modules` and re-run `npm install`.
- If charts appear empty: ensure events are generated (let the simulation run several ticks) and check the console for warnings.

---

## Appendix — Optional B‑roll Ideas (no narration needed)
- 10–15 seconds of the simulation running with the Event Type Summary changing.
- Scrolling through ontology classes/instances.
- Opening the `run_summary.json` file and the `metrics.png` figure.

---

Good luck with your recording!
