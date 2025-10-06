# 5–10 min Video Script (talking points)

1) **Intro (30s)** — State the goal: ontology + MAS for bookstore ops (buying, inventory, restocking).
2) **Architecture (60–90s)** — Show the class diagram (Book, Customer, Employee, Order, Inventory) and
   the message topics. Mention SWRL for low-stock; orders assert `purchases(Customer, Book)`.
3) **Run demo (2–3 min)** — Start the sim:
   - Show console output of purchases/restocks.
   - Open `report/figures/metrics.png` and explain the trend.
   - Show `bookstore.owl` saved and quick peek (e.g., `needsRestock` disappears after restock).
4) **Rules (60s)** — Open `bms/rules.py` and read the two rules, explain the reasoner timing.
5) **Wrap-up (45s)** — Results summary, challenges, and 1–2 future extensions.
6) **Face cam visible** — Keep your face visible during narration, as required.
