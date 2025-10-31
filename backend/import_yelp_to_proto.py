#!/usr/bin/env python3
"""
Import menu items from a yelp_*.sqlite (made by extract_menu.py)
into proto_db.sqlite/menu_items for a single restaurant.

Usage:
python import_yelp_to_proto.py --restaurant "Tacoria" \
  --source yelp_tacoria.sqlite --target proto_db.sqlite
"""

import argparse
import sqlite3
import re

NAME_PREFIX = "arrange_unit"
DESC_PREFIX = "menu-item-details-description"
PRICE_PREFIX = "menu-item-price-amount"

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--restaurant", required=True)
    p.add_argument("--source", required=True)  # yelp_*.sqlite
    p.add_argument("--target", default="proto_db.sqlite")
    return p.parse_args()

def get_restaurant_id(conn, name):
    row = conn.execute("SELECT id FROM restaurants WHERE name = ?", (name,)).fetchone()
    if not row:
        raise SystemExit(f"Restaurant not found in proto_db.sqlite: {name}")
    return row[0]

def column_suffix(col, prefix):
    # matches: prefix, prefix N
    if col == prefix:
        return ""
    m = re.match(rf"^{re.escape(prefix)}\s+(\d+)$", col)
    return m.group(1) if m else None

def money_to_cents(s):
    if not s:
        return None
    s = s.strip()
    # handles "$12.50", "12.50", "$12"
    s = s.replace("$","")
    try:
        return int(round(float(s) * 100))
    except:
        return None

def main():
    args = parse_args()

    # open target app DB
    tconn = sqlite3.connect(args.target)
    tconn.isolation_level = None

    rest_id = get_restaurant_id(tconn, args.restaurant)

    # open source yelp DB
    sconn = sqlite3.connect(args.source)
    sconn.isolation_level = None

    # figure out columns in yelp_raw
    cols = [r[1] for r in sconn.execute("PRAGMA table_info(yelp_raw)")]
    name_cols = {}
    desc_cols = {}
    price_cols = {}

    for c in cols:
        sfx = column_suffix(c, NAME_PREFIX)
        if sfx is not None:
            name_cols[sfx] = c
        sfx = column_suffix(c, DESC_PREFIX)
        if sfx is not None:
            desc_cols[sfx] = c
        sfx = column_suffix(c, PRICE_PREFIX)
        if sfx is not None:
            price_cols[sfx] = c

    # build column triplets by suffix
    suffixes = sorted(set(name_cols.keys()) | set(desc_cols.keys()) | set(price_cols.keys()),
                      key=lambda x: (x=="" and -1) or int(x or 0))

    # read all rows
    rows = sconn.execute("SELECT * FROM yelp_raw").fetchall()
    # map index -> column name
    idx2col = {i:c for i,(i, c, *_rest) in enumerate(sconn.execute("PRAGMA table_info(yelp_raw)"))}

    inserted = 0
    for row in rows:
        for sfx in suffixes:
            ncol = name_cols.get(sfx)
            if not ncol:
                continue
            name_val = row[[k for k,v in idx2col.items() if v == ncol][0]]
            if not name_val or not str(name_val).strip():
                continue

            dcol = desc_cols.get(sfx)
            pcol = price_cols.get(sfx)

            desc_val = None
            price_val = None

            if dcol:
                desc_val = row[[k for k,v in idx2col.items() if v == dcol][0]]
            if pcol:
                price_val = row[[k for k,v in idx2col.items() if v == pcol][0]]

            cents = money_to_cents(price_val if isinstance(price_val, str) else (price_val or ""))

            try:
                tconn.execute(
                    "INSERT OR IGNORE INTO menu_items (restaurant_id, name, description, price_cents) "
                    "VALUES (?, ?, ?, ?)",
                    (rest_id, str(name_val).strip(), (desc_val or None), cents)
                )
                inserted += 1
            except Exception as ex:
                print("skip:", ex)

    print(f"Imported {inserted} items into menu_items for restaurant_id={rest_id}")

if __name__ == "__main__":
    main()
