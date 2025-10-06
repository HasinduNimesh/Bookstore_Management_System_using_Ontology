"""SWRL rules + reasoning utilities (Owlready2).

We use SWRL to derive declarative facts that agents can act upon. Arithmetic
updates (like decrementing stock) are performed by agents in Python.

Rules:
1) Low stock => needsRestock(true)
    Inventory(?i) ^ availableQuantity(?i, ?q) ^ thresholdQuantity(?i, ?t) ^ swrlb:lessThan(?q, ?t)
    -> needsRestock(?i, true)

2) If Order exists => assert purchases(Customer, Book) (audit trail)
    Order(?o) ^ orderedBy(?o, ?c) ^ forBook(?o, ?b) -> purchases(?c, ?b)
"""

from typing import Any
from owlready2 import Imp, sync_reasoner_pellet, sync_reasoner  # type: ignore

def attach_rules(onto: Any):
    with onto:
        # Rule 1: low inventory triggers needsRestock flag via SWRL built-in comparison
        try:
            onto.world.get_ontology("http://www.w3.org/2003/11/swrlb#").load()
            r1 = Imp()
            r1.set_as_rule("Inventory(?i) ^ availableQuantity(?i, ?q) ^ thresholdQuantity(?i, ?t) ^ swrlb:lessThan(?q, ?t) -> needsRestock(?i, true)")
        except Exception:
            r1 = None  # Built-ins unavailable; fallback handled in Python

        # Rule 2: order implies purchases relation (ontology bookkeeping)
        r2 = Imp()
        r2.set_as_rule("Order(?o) ^ orderedBy(?o, ?c) ^ forBook(?o, ?b) -> purchases(?c, ?b)")

def run_reasoner(onto: Any):
    """Trigger Pellet/HermiT via Owlready2. Requires Java on the machine."""
    try:
        sync_reasoner_pellet([onto], infer_property_values=True)
    except Exception:
        # Fallback: some installs expose sync_reasoner only
        try:
            sync_reasoner([onto], infer_property_values=True)
        except Exception:
            # If reasoning fails, continue without it
            pass
