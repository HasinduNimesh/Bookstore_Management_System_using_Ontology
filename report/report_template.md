# Bookstore Management System — Ontology + MAS + SWRL (≤20 pages)

**Author:** _<Your Name>_

> **How to use this template:** Replace placeholders, insert your screenshots from `report/figures/`,
> and export to PDF. Keep the emphasis on **implementation**.

---

## 1. Goal & Setup (≤1 page)

- Business goal: simulate core bookstore operations with ontology-aware agents and rules.
- Stack: Owlready2 for ontology + SWRL; Mesa for agents, message bus + scheduling; Matplotlib for plots.
- How to run: `python -m bms.run --steps 40 ...`

> _Assignment requirements_ — implementation-focused PDF (≤ 20 pages), working code, and a demo video. [Assignment brief]()

---

## 2. Method — From analysis to design (2–3 pages)

Summarize the analysis→design method you followed:
- **Agent types**: Customer, Employee, Book.
- **Responsibilities** (table): who does what and why (buying, processing orders, restocking, auditing).
- **Acquaintances diagram**: who must talk to whom; message topics used.
- **Interaction table**: purchase flow (initiator/responder), restock flow, message template/IDs.

Insert figures/diagrams here.

---

## 3. Ontology (3–4 pages)

- **Classes**: `Book`, `Customer`, `Employee`, `Order`, `Inventory`.
- **Object properties**: `purchases`, `worksAt`, `hasBook`, `orderedBy`, `forBook`.
- **Data properties**: `hasAuthor`, `hasGenre`, `hasPrice`, `availableQuantity`, `thresholdQuantity`, `restockAmount`, `quantity`, `needsRestock`.
- Rationale for ontology boundaries (why these concepts belong in the ontology).
- Screenshot(s) of Protegé/OWL file or generated graph.

---

## 4. Agents & Simulation (3–4 pages)

- **CustomerAgent**: picks a book (pref-biased), issues an `Order` individual + a `purchase_request` message.
- **EmployeeAgent**: handles purchases (decrements stock), runs the reasoner, restocks inferred low-stock.
- **BookAgent**: holder for book state (for future behaviors).
- **Message bus**: topics, conversation IDs; how conflicts are avoided.
- **Model**: `RandomActivation`, `DataCollector` metrics.

Include: code excerpts + sequence diagram of one time step.

---

## 5. SWRL Rules + Reasoning (2–3 pages)

Rules implemented:
1. `availableQuantity < thresholdQuantity` ⇒ `needsRestock(i, true)`.
2. `Order` ⇒ `purchases(Customer, Book)` (audit trail).

Explain where `sync_reasoner_pellet()` is called and how Python performs arithmetic updates
(decrementing stock) **after** semantic checks.

---

## 6. Results (2–3 pages)

- Insert plots from `report/figures/metrics.png`.
- Report totals: sales, units sold, restocks, stockouts.
- Compare scenarios (baseline vs. high demand vs. low threshold).

---

## 7. Challenges & Mitigations (1–2 pages)

- Reasoner cadence vs. performance; ordering of updates.
- Ensuring ontology and agent state don’t diverge.
- Message ordering / idempotency.

---

## 8. Conclusion & Future Work (≤1 page)

- What worked well.
- Possible extensions (discount rules, genre-specific employees, RL reorder policy).

---

## Appendix — How to Reproduce

- Commands used.
- Python versions.
- Any platform notes (Java for Pellet).
