#!/usr/bin/env python3
"""
extract_menu.py

Usage:
python extract_menu.py yelp.csv [yelp.sqlite]

Opens or creates an SQLite database file (default: yelp.sqlite)
Imports the CSV into a table named yelp_raw.
Finds any columns whose header begin with arrange unit
Prints every non-empty value under those columns
"""

# imports
import sys
import csv
import re
import sqlite3
import contextlib
from pathlib import Path

# sqlite file uri template
DATABASE_URL_TEMPLATE = "file:{name}?mode=rwc"


def quote_name(name: str) -> str:
    """ quote a column or table name """
    # double any internal quotes
    return '"' + name.replace('"', '""') + '"'


def quote_text(text: str) -> str:
    """ quote a string literal """
    # double any internal single quotes
    return "'" + text.replace("'", "''") + "'"


def import_csv_to_sqlite(cur: sqlite3.Cursor, csv_path: Path) -> list[str]:
    """
    Create table yelp_raw and load all rows from the CSV.
    Returns the header list in order.
    """
    # open csv
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        # read header
        try:
            headers = next(reader)
        except StopIteration:
            raise RuntimeError("CSV is empty.")

        # reset table
        cur.execute("DROP TABLE IF EXISTS yelp_raw")

        # create table with TEXT columns
        column_defs = ", ".join(f"{quote_name(h)} TEXT" for h in headers)
        cur.execute(f"CREATE TABLE yelp_raw ({column_defs})")

        # prepare insert
        placeholders = ", ".join(["?"] * len(headers))
        insert_sql = f"INSERT INTO yelp_raw VALUES ({placeholders})"

        # normalize rows to header width
        rows = []
        for row in reader:
            if len(row) < len(headers):
                row += [""] * (len(headers) - len(row))
            elif len(row) > len(headers):
                row = row[:len(headers)]
            rows.append(row)

        # bulk insert
        if rows:
            cur.executemany(insert_sql, rows)

        # return headers
        return headers


def find_arrange_columns(cur: sqlite3.Cursor) -> list[str]:
    """ return all column names that match the arrange_unit pattern """
    # get schema info
    info = cur.execute("PRAGMA table_info(yelp_raw)").fetchall()
    names = [row[1] for row in info]

    # arrange_unit pattern
    pattern = re.compile(r"^arrange[_\s-]*unit(?:\s*#?\s*\d+)?$", re.IGNORECASE)

    # match headers
    matches = []
    for name in names:
        if pattern.match(name.strip()):
            matches.append(name)

    # return matches
    return matches


def build_union_sql(arrange_cols: list[str]) -> str:
    """ Build a UNION ALL query that selects non-empty values from each arrange unit column """
    # parts holder
    parts = []

    # add select per column
    for col in arrange_cols:
        col_q = quote_name(col)
        src_q = quote_text(col)
        part = (
            f"SELECT {src_q} AS source_col, {col_q} AS item "
            f"FROM yelp_raw "
            f"WHERE {col_q} IS NOT NULL AND TRIM({col_q}) <> ''"
        )
        parts.append(part)

    # join parts
    return " UNION ALL ".join(parts)


def main() -> None:
    """ Entry point. Parses args, loads CSV, extracts and prints arrange_unit items. """
    # parse args
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python extract_menu.py yelp.csv [yelp.sqlite]", file=sys.stderr)
        sys.exit(1)

    # check csv path
    csv_file = Path(sys.argv[1])
    if not csv_file.exists():
        print(f"CSV not found: {csv_file}", file=sys.stderr)
        sys.exit(1)

    # choose db path
    db_file = Path(sys.argv[2]) if len(sys.argv) == 3 else Path("yelp.sqlite")
    db_url = DATABASE_URL_TEMPLATE.format(name=str(db_file))

    try:
        # connect to sqlite
        with sqlite3.connect(db_url, isolation_level=None, uri=True) as conn:
            # open cursor
            with contextlib.closing(conn.cursor()) as cur:
                # import csv
                import_csv_to_sqlite(cur, csv_file)

                # find arrange columns
                arrange_cols = find_arrange_columns(cur)

                # nothing found
                if not arrange_cols:
                    return

                # build union
                union_sql = build_union_sql(arrange_cols)

                # final query
                final_sql = (
                    "SELECT item "
                    "FROM (" + union_sql + ") "
                    "WHERE TRIM(item) <> '' "
                    "ORDER BY item"
                )

                # print items
                for (item,) in cur.execute(final_sql):
                    print(item)

    except Exception as exc:
        # error out
        print(exc, file=sys.stderr)
        sys.exit(1)


# run
if __name__ == "__main__":
    main()
