
"""
Load menu items CSVs into public.menu_items, mapped to the correct restaurant.
Expected CSV headers: Item, Price, Description
- If called with a directory, loads all *_menu.csv files inside.
- If called with file paths, loads those.
Restaurant is inferred from filename prefix before ' - '.
"""

import sys
import re
from pathlib import Path
import csv
from statistics import mean
from decimal import Decimal, InvalidOperation

from data_management.db_manager import (
    create_restaurants_table,
    create_menu_items_table,
    create_users_table,
    ensure_restaurants_uniqueness,
    ensure_menu_items_uniqueness,
    find_restaurant_id_by_name,
    bulk_upsert_menu_items,
)


def to_avg_price(s):
    if s is None:
        return None
    text = str(s).strip()
    if not text or text.lower() == "nan":
        return None
    nums = re.findall(r"\d+(?:\.\d+)?", text.replace(',', ''))
    if not nums:
        try:
            return float(Decimal(text))
        except InvalidOperation:
            return None
    vals = [float(n) for n in nums]
    try:
        return float(mean(vals))
    except Exception:
        return vals[0] if vals else None


def read_menu_csv(csv_path: Path):
    items = []
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        def pick(d, *names):
            for n in names:
                if n in d:
                    return d[n]
            return None
        for row in reader:
            name = pick(row, 'Item', 'item', 'name', 'Name')
            desc = pick(row, 'Description', 'description', 'desc', 'Details')
            price = pick(row, 'Price', 'price', 'avg_price', 'cost')
            item = {
                'name': (name or '').strip(),
                'description': ('' if desc is None else str(desc).strip()),
                'avg_price': to_avg_price(price),
            }
            if item['name']:
                items.append(item)
    return items


def infer_restaurant_name_from_filename(p: Path):
    base = p.stem
    if ' - ' in base:
        return base.split(' - ', 1)[0].strip()
    return base.replace('_', ' ').strip().title()


def expand_targets(arg: str):
    path = Path(arg)
    if path.is_dir():
        return sorted(path.glob("*_menu.csv"))
    if any(ch in arg for ch in ['*', '?', '[']):
        return sorted(Path('.').glob(arg))
    return [path]


def main(argv):
    if len(argv) <= 1:
        print("Usage: python -m data_management.load_menu_items_from_csv <csv|dir with *_menu.csv> [...]")
        return 2

    create_restaurants_table()
    create_menu_items_table()
    create_users_table()
    ensure_restaurants_uniqueness()
    ensure_menu_items_uniqueness()

    all_paths = []
    for a in argv[1:]:
        all_paths.extend(expand_targets(a))

    if not all_paths:
        print("No CSV files found.")
        return 2

    total_items = 0
    for p in all_paths:
        if p.suffix.lower() != '.csv':
            continue
        rname = infer_restaurant_name_from_filename(p)
        rest_id = find_restaurant_id_by_name(rname)
        if not rest_id:
            print(f"[SKIP] Restaurant not found for '{rname}' from file {p.name}.")
            continue

        items = read_menu_csv(p)
        n = bulk_upsert_menu_items(rest_id, items)
        total_items += n
        print(f"Upserted {n} items for {rname} from {p.name}")

    print(f"Done. Total menu items upserted: {total_items}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
