"""Predefined scenarios to collect results quickly."""
import os
from .model import BMSModel

def scenario_baseline(outdir: str):
    m = BMSModel(seed_path=os.path.join(os.path.dirname(__file__), "data", "seed_books.json"), N_customers=30, restock_threshold=5, restock_amount=10, seed=42)
    for _ in range(40):
        m.step()
    m.save_artifacts(os.path.join(outdir, "baseline"))

def scenario_high_demand(outdir: str):
    m = BMSModel(seed_path=os.path.join(os.path.dirname(__file__), "data", "seed_books.json"), N_customers=60, restock_threshold=5, restock_amount=10, seed=7)
    for _ in range(40):
        m.step()
    m.save_artifacts(os.path.join(outdir, "high_demand"))

def scenario_low_threshold(outdir: str):
    m = BMSModel(seed_path=os.path.join(os.path.dirname(__file__), "data", "seed_books.json"), N_customers=30, restock_threshold=2, restock_amount=10, seed=99)
    for _ in range(40):
        m.step()
    m.save_artifacts(os.path.join(outdir, "low_threshold"))

if __name__ == "__main__":
    outdir = os.path.join(os.path.dirname(__file__), "..", "report", "experiments")
    os.makedirs(outdir, exist_ok=True)
    scenario_baseline(outdir)
    scenario_high_demand(outdir)
    scenario_low_threshold(outdir)
