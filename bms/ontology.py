"""Ontology definition for the Bookstore MAS (Owlready2).

- Classes: Book, Customer, Employee, Order, Inventory
- Properties: hasAuthor, hasGenre, hasPrice, availableQuantity, thresholdQuantity, restockAmount,
             purchases, worksAt, hasBook, orderedBy, forBook, quantity, needsRestock

This module exposes helpers to build the ontology and seed sample data.
"""

from typing import Dict, List, Tuple, Any
from owlready2 import (  # type: ignore[import-not-found]
    get_ontology,
    Thing,
    ObjectProperty,
    DataProperty,
    FunctionalProperty,
)
import os, json

BASE_IRI = "http://example.org/bookstore.owl#"

def build_ontology() -> Any:
    onto = get_ontology(BASE_IRI)
    with onto:
        class Book(Thing):
            pass
        class Customer(Thing):
            pass
        class Employee(Thing):
            pass
        class Order(Thing):
            pass
        class Inventory(Thing):
            pass

        # Object Properties
        class purchases(ObjectProperty):
            domain = [Customer]
            range = [Book]

        class worksAt(ObjectProperty):
            domain = [Employee]
            range = [Inventory]

        class hasBook(ObjectProperty):
            domain = [Inventory]
            range = [Book]

        class orderedBy(ObjectProperty):
            domain = [Order]
            range = [Customer]

        class forBook(ObjectProperty):
            domain = [Order]
            range = [Book]

        # Data Properties
        class hasAuthor(DataProperty, FunctionalProperty):
            domain = [Book]
            range = [str]

        class hasGenre(DataProperty, FunctionalProperty):
            domain = [Book]
            range = [str]

        class hasPrice(DataProperty, FunctionalProperty):
            domain = [Book]
            range = [float]

        class availableQuantity(DataProperty, FunctionalProperty):
            domain = [Inventory]
            range = [int]

        class thresholdQuantity(DataProperty, FunctionalProperty):
            domain = [Inventory]
            range = [int]

        class restockAmount(DataProperty, FunctionalProperty):
            domain = [Inventory]
            range = [int]

        class quantity(DataProperty, FunctionalProperty):
            domain = [Order]
            range = [int]

        class needsRestock(DataProperty, FunctionalProperty):
            domain = [Inventory]
            range = [bool]

    return onto

def seed_from_json(onto: Any, path: str, default_threshold: int = 5, default_restock: int = 10):
    """Create Book + Inventory individuals from a JSON file.
    JSON rows must have: title, author, genre, price, qty
    Returns: dicts of created individuals.
    """
    data = json.load(open(path, "r", encoding="utf-8"))
    Book = onto.Book
    Inventory = onto.Inventory
    hasAuthor = onto.hasAuthor
    hasGenre = onto.hasGenre
    hasPrice = onto.hasPrice
    availableQuantity = onto.availableQuantity
    thresholdQuantity = onto.thresholdQuantity
    restockAmount = onto.restockAmount
    hasBook = onto.hasBook
    needsRestock = onto.needsRestock

    books = {}
    inventories = {}

    for row in data:
        b = Book(iri = BASE_IRI + f"book_{slug(row['title'])}")
        b.hasAuthor = row["author"]
        b.hasGenre = row["genre"]
        b.hasPrice = float(row["price"])
        inv = Inventory(iri = BASE_IRI + f"inv_{slug(row['title'])}")
        inv.availableQuantity = int(row["qty"])
        inv.thresholdQuantity = int(default_threshold)
        inv.restockAmount = int(default_restock)
        inv.needsRestock = False
        hasBook[inv] = [b]
        books[row["title"]] = b
        inventories[row["title"]] = inv

    return books, inventories

def slug(s: str) -> str:
    return ''.join(c.lower() if c.isalnum() else '_' for c in s).strip('_')

def save_ontology(onto: Any, out_file: str):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    onto.save(file=out_file, format="rdfxml")
