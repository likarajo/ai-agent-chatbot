"""Rebuild the committed CSV from EIA's annual_generation_state.xls.

Requires xlrd==1.2.0, which can read the legacy .xls workbook. The running
agent does not need xlrd. It reads the CSV this script writes.
"""

import csv
import sys
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "eia_net_generation_2020_2024.csv"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/build_csv.py annual_generation_state.xls")
    book = xlrd.open_workbook(sys.argv[1])
    sheet = book.sheet_by_index(0)
    rows = []
    for index in range(2, sheet.nrows):
        year, state, producer, energy, generation = [sheet.cell_value(index, col) for col in range(5)]
        if producer != "Total Electric Power Industry" or energy == "Total" or int(year) < 2020:
            continue
        code = str(state).strip().upper().replace("US-TOTAL", "US")
        if not code:
            continue
        rows.append((int(year), code, energy, int(round(float(generation)))))
    rows.sort()
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with DEST.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["year", "state", "energy_source", "generation_mwh"])
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {DEST}")


if __name__ == "__main__":
    main()
