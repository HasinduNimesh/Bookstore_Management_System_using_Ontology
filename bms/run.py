"""Command-line entrypoint to run the Bookstore MAS simulation."""
import argparse, os, json
import matplotlib.pyplot as plt  # type: ignore

from .model import BMSModel

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default=42, type=int)
    parser.add_argument("--steps", default=40, type=int)
    parser.add_argument("--customers", default=30, type=int)
    parser.add_argument("--threshold", default=5, type=int)
    parser.add_argument("--restock", default=10, type=int)
    parser.add_argument("--seed_path", default=os.path.join(os.path.dirname(__file__), "data", "seed_books.json"))
    args = parser.parse_args()

    model = BMSModel(seed_path=args.seed_path, N_customers=args.customers, restock_threshold=args.threshold, restock_amount=args.restock, seed=args.seed)

    for _ in range(args.steps):
        model.step()

    outdir = os.path.join(os.path.dirname(__file__), "..", "report")
    figsdir = os.path.join(outdir, "figures")
    os.makedirs(figsdir, exist_ok=True)

    model.save_artifacts(outdir)

    # Plot basic metrics
    df = model.datacollector.get_model_vars_dataframe()
    ax = df.plot(title="BMS — Key Metrics vs. Step")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(os.path.join(figsdir, "metrics.png"))

    print(json.dumps({"summary": {
        "total_sales": model.total_sales,
        "sold_count": model.sold_count,
        "restocks": model.restocks,
        "stockouts": model.stockouts
    }}, indent=2))

if __name__ == "__main__":
    main()
