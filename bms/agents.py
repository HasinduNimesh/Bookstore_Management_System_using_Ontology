from __future__ import annotations
"""Agents for the Bookstore MAS (Mesa)."""
import random
from typing import List, Optional, Tuple, Any

from mesa import Agent  # type: ignore[import-not-found]

from bms.messaging import Message, MessageBus
from bms.rules import run_reasoner

class CustomerAgent(Agent):
    def __init__(self, unique_id, model, name: str, preferred_genres: Optional[List[str]] = None, buy_prob: float = 0.35):
        super().__init__(unique_id, model)
        self.name = name
        self.buy_prob = buy_prob
        self.preferred_genres = preferred_genres or []

    def step(self):
        # Customers randomly decide to buy based on probability
        if random.random() > self.buy_prob:
            return

        # Pick a book (bias by preference if possible)
        m: Any = self.model
        book_list = list(getattr(m, "books", {}).values())
        if not book_list:
            return

        if self.preferred_genres and random.random() < 0.7:
            filtered = [b for b in book_list if (b.hasGenre and b.hasGenre in self.preferred_genres)]
            candidates = filtered or book_list
        else:
            candidates = book_list
        b = random.choice(candidates)

        # Build order OWL individual
        onto = getattr(m, "onto")
        Order = onto.Order
        orderedBy = onto.orderedBy
        forBook = onto.forBook
        quantity = onto.quantity

        o = Order(iri = onto.base_iri + f"order_{self.unique_id}_{getattr(m, 'current_step', 0)}")
        orderedBy[o] = [getattr(m, "customers")[self.unique_id].owl]  # point to OWL Customer
        forBook[o] = [b]
        quantity[o] = [1]

        # Emit message
        m.bus.publish("purchase_request", Message(topic="purchase_request", sender=self.name, payload={
            "order_iri": o.iri,
            "book_iri": b.iri,
            "qty": 1
        }))

class EmployeeAgent(Agent):
    def __init__(self, unique_id, model, name: str):
        super().__init__(unique_id, model)
        self.name = name
        # Subscribe to bus topics
        # We use polling in step() to avoid cross-thread complexity.

    def _process_purchase(self, m: Message):
        m_model: Any = self.model
        onto = getattr(m_model, "onto")
        # Resolve order + book
        order = onto.world[ m.payload["order_iri"] ]
        book = onto.world[ m.payload["book_iri"] ]
        qty = m.payload.get("qty", 1)

        # Find matching inventory
        inv = None
        for i in onto.Inventory.instances():
            if onto.hasBook[i] and onto.hasBook[i][0] is book:
                inv = i
                break
        if inv is None:
            getattr(m_model, "logs").append(f"[WARN] No inventory found for {book.name}")
            return

        available = int(inv.availableQuantity)
        if available >= qty:
            inv.availableQuantity = available - qty
            m_model.total_sales = getattr(m_model, "total_sales", 0.0) + qty * float(book.hasPrice)
            m_model.sold_count = getattr(m_model, "sold_count", 0) + qty
            m_model.bus.publish("purchase_result", Message(topic="purchase_result", sender=self.name, payload={
                "status": "success", "book": book.name, "qty": qty, "remaining": int(inv.availableQuantity)
            }))
        else:
            m_model.stockouts = getattr(m_model, "stockouts", 0) + 1
            m_model.bus.publish("purchase_result", Message(topic="purchase_result", sender=self.name, payload={
                "status": "stockout", "book": book.name, "qty": qty, "remaining": available
            }))

    def _check_restock(self):
        m_model: Any = self.model
        onto = getattr(m_model, "onto")
        # Try to infer low-stock state via SWRL rules (falls back if reasoner unavailable)
        run_reasoner(onto)

        needs = []
        for inv in onto.Inventory.instances():
            needs_flag = getattr(inv, "needsRestock", None)
            if isinstance(needs_flag, (list, tuple)):
                needs_flag = needs_flag[0] if needs_flag else False
            if needs_flag:
                needs.append(inv)

        # Fallback in case the reasoner could not run (e.g., Java missing)
        if not needs:
            for inv in onto.Inventory.instances():
                available = int(inv.availableQuantity) if inv.availableQuantity else 0
                threshold = int(inv.thresholdQuantity) if inv.thresholdQuantity else 5
                if available < threshold:
                    needs.append(inv)

        for inv in needs:
            # Restock
            current = int(inv.availableQuantity)
            add = int(inv.restockAmount) if inv.restockAmount else 10
            inv.availableQuantity = current + add
            try:
                inv.needsRestock = False
            except Exception:
                pass
            m_model.restocks = getattr(m_model, "restocks", 0) + 1
            m_model.bus.publish("restock_done", Message(topic="restock_done", sender=self.name, payload={
                "inv": inv.name, "added": add, "now": int(inv.availableQuantity)
            }))

    def step(self):
        # Deliver bus messages (one per step)
        # Process all purchase requests
        m_model: Any = self.model
        for msg in m_model.bus.drain("purchase_request"):
            self._process_purchase(msg)

        # After processing purchases, check restock conditions (SWRL-inferred)
        self._check_restock()


class BookAgent(Agent):
    """A lightweight agent holding a view of a Book + Inventory. It doesn't act actively in this model
    but provides a natural landing place for future behaviors (e.g., discounting, recommendations)."""
    def __init__(self, unique_id, model, book_iri: str):
        super().__init__(unique_id, model)
        self.book_iri = book_iri

    def step(self):  # no-op
        return


class CustomerHandle:
    """Convenience wrapper to access the OWL Customer individual by the same id."""
    def __init__(self, owl):
        self.owl = owl
