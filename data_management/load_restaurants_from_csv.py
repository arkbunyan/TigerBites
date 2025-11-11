"""
TigerBites CSV Loader
- Reads Restaurant Data.csv and upserts into public.restaurants
- Defaults to a CSV that lives right next to this file

load the CSV in the same folder 
python -m data_management.load_restaurants_from_csv

or pass a path explicitly
python -m data_management.load_restaurants_from_csv "data_management/Restaurant Data.csv"
"""

import csv
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

from data_management.db_manager import (
    create_restaurants_table,
    create_menu_items_table,
    create_users_table,
    ensure_restaurants_uniqueness,
    bulk_insert_restaurants,
)


def to_float(x):
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        try:
            return float(Decimal(s))
        except InvalidOperation:
            return None


def load_csv(csv_path: Path):
    rows = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {
                "name": (raw.get("name") or "").strip(),
                "description": (raw.get("description") or "").strip(),
                "location": (raw.get("location") or "").strip(),
                "hours": (raw.get("hours") or "").strip(),
                "category": (raw.get("category") or "").strip(),
                "avg_price": to_float(raw.get("avg_price")),
                "latitude": to_float(raw.get("latitude")),
                "longitude": to_float(raw.get("longitude")),
            }
            rows.append(row)
    return rows


def main():
    # If no arg, default to sibling CSV named "Restaurant Data.csv"
    if len(sys.argv) >= 2:
        csv_path = Path(sys.argv[1])
    else:
        csv_path = Path(__file__).resolve().parent / "Restaurant Data.csv"

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        sys.exit(2)

    # Ensure schema and uniqueness
    create_restaurants_table()
    create_menu_items_table()
    create_users_table()
    ensure_restaurants_uniqueness()

    rows = load_csv(csv_path)
    n = bulk_insert_restaurants(rows)
    print(f"Inserted/updated {n} restaurants from {csv_path.name}.")


if __name__ == "__main__":
    main()
