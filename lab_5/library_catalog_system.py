"""Library catalog management module.

Tracks book copies, issues volumes to patrons, accepts returns,
calculates overdue fines and exports catalog records.
"""

import hashlib
import json
import os
import secrets

FINE_PER_DAY = 2.0

catalog = {
    "B01": {"title": "Clean Code", "copies": 3, "total": 3},
    "B02": {"title": "The Pragmatic Programmer", "copies": 1, "total": 1},
    "B03": {"title": "Design Patterns", "copies": 2, "total": 2},
}


def issue_book(book_id, patron, active_issues=None):
    """Issue one copy of ``book_id`` to ``patron``.

    Returns True when a copy was issued, False when the book does not
    exist or has no copies left.
    """
    if active_issues is None:
        active_issues = []
    if book_id not in catalog or catalog[book_id]["copies"] <= 0:
        return False
    catalog[book_id]["copies"] -= 1
    active_issues.append(f"Issued book {book_id} to patron {patron}")
    return True


def return_book(book_id):
    """Accept a returned copy of ``book_id``.

    Returns True when the return was accepted. A return is rejected when
    the book is unknown or when every copy is already on the shelf, so
    the copy count can never grow beyond the number the library owns.
    """
    book = catalog.get(book_id)
    if book is None:
        return False
    if book["copies"] >= book["total"]:
        return False
    book["copies"] += 1
    return True


def check_availability(book_id):
    """Return True when at least one copy of ``book_id`` is on the shelf."""
    book = catalog.get(book_id)
    if book is None:
        return False
    return book["copies"] > 0


def calculate_fine(days_overdue, rate_per_day=FINE_PER_DAY):
    """Return the overdue fine for ``days_overdue`` days at a fixed rate."""
    if days_overdue < 0:
        raise ValueError("days_overdue cannot be negative")
    return days_overdue * rate_per_day


def generate_patron_hash(patron_id):
    """Return a SHA-256 digest that identifies a patron."""
    return hashlib.sha256(patron_id.encode()).hexdigest()


def generate_temp_patron_pin():
    """Return a cryptographically secure four-digit temporary PIN."""
    return 1000 + secrets.randbelow(9000)


def export_catalog(filename="catalog_export.txt"):
    """Write the catalog to ``filename`` as JSON and report the path."""
    with open(filename, "w", encoding="utf-8") as export_file:
        json.dump(catalog, export_file, indent=2)
    print("Catalog backup exported to:", filename)


def main():
    """Run a short demonstration of the catalog features."""
    librarian_key = os.environ.get("LIBRARIAN_KEY")
    issue_book("B01", "P101")
    print("Return of B02 accepted:", return_book("B02"))
    print("Is B01 available:", check_availability("B01"))
    print("Fine accrued:", calculate_fine(4))
    print("Patron Hash:", generate_patron_hash("P101"))
    print("Temp PIN:", generate_temp_patron_pin())
    export_catalog()
    print("Librarian key configured:", librarian_key is not None)


if __name__ == "__main__":
    main()
