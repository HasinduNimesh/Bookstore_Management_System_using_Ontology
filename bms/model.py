from __future__ import annotations
"""Mesa model for the Bookstore MAS."""
import random, os, json, pathlib
from typing import Dict

from mesa import Model  # type: ignore
from mesa.time import RandomActivation  # type: ignore
from mesa.datacollection import DataCollector  # type: ignore

from bms.messaging import MessageBus
from bms import ontology as ontomod
from bms import rules as rulesmod
from bms.agents import CustomerAgent, EmployeeAgent, BookAgent, CustomerHandle

class BMSModel(Model):
    def __init__(self, seed_path: str, N_customers: int = 30, restock_threshold: int = 5, restock_amount: int = 10, seed: int = 42):
        super().__init__()
        random.seed(seed)
        self.random = random.Random(seed)

        self.bus = MessageBus()
        self.schedule = RandomActivation(self)

        # Build ontology + data
        self.onto = ontomod.build_ontology()
        self.onto.base_iri = ontomod.BASE_IRI  # convenience
        rulesmod.attach_rules(self.onto)

        # Seed books + inventory
        self.books, self.inventories = ontomod.seed_from_json(self.onto, seed_path, default_threshold=restock_threshold, default_restock=restock_amount)

        # Create Customers (OWL + agent)
        self.customers: Dict[int, CustomerHandle] = {}
        for i in range(N_customers):
            c_owl = self.onto.Customer(iri = self.onto.base_iri + f"cust_{i}")
            self.customers[i] = CustomerHandle(c_owl)
            # Prefer a random genre
            genres = list({b.hasGenre for b in self.books.values() if b.hasGenre})
            prefs = self.random.sample(genres, k=min(2, len(genres))) if genres else []
            a = CustomerAgent(unique_id=i, model=self, name=f"Customer_{i}", preferred_genres=prefs)
            self.schedule.add(a)

        # Create 1 Employee (OWL + agent)
        self.employee_owl = self.onto.Employee(iri = self.onto.base_iri + "employee_1")
        emp = EmployeeAgent(unique_id=N_customers + 1, model=self, name="Employee_1")
        self.schedule.add(emp)

        # Optional: Book agents as placeholders
        uid = N_customers + 2
        for b in self.books.values():
            self.schedule.add(BookAgent(unique_id=uid, model=self, book_iri=b.iri))
            uid += 1

        # Metrics
        self.total_sales = 0.0
        self.sold_count = 0
        self.restocks = 0
        self.stockouts = 0
        self.logs = []
        self.current_step = 0

        self.datacollector = DataCollector(
            model_reporters={
                "total_sales": lambda m: m.total_sales,
                "sold_count": lambda m: m.sold_count,
                "restocks": lambda m: m.restocks,
                "stockouts": lambda m: m.stockouts,
                "unique_books_in_stock": lambda m: sum(1 for inv in m.onto.Inventory.instances() if inv.availableQuantity and int(inv.availableQuantity) > 0),
            }
        )

    def step(self):
        self.current_step += 1
        self.datacollector.collect(self)
        self.schedule.step()

    def save_artifacts(self, outdir: str):
        os.makedirs(outdir, exist_ok=True)
        # Save ontology snapshot
        ontopath = os.path.join(outdir, "bookstore.owl")
        ontomod.save_ontology(self.onto, ontopath)
        # Save run summary
        summary = {
            "total_sales": self.total_sales,
            "sold_count": self.sold_count,
            "restocks": self.restocks,
            "stockouts": self.stockouts,
            "steps": self.current_step
        }
        json.dump(summary, open(os.path.join(outdir, "run_summary.json"), "w"), indent=2)
