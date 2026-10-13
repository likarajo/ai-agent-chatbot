"""Load the EIA CSV into a read-only SQLite file."""

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "eia_net_generation_2020_2024.csv"
DB_PATH = ROOT / "data" / "generation.sqlite"


def connect_readonly(csv_path: Path = CSV_PATH, db_path: Path = DB_PATH) -> sqlite3.Connection:
    build_database(csv_path, db_path)
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def build_database(csv_path: Path = CSV_PATH, db_path: Path = DB_PATH) -> Path:
    if db_path.exists() and db_path.stat().st_mtime >= csv_path.stat().st_mtime:
        return db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = db_path.with_suffix(".sqlite.tmp")
    if temporary.exists():
        temporary.unlink()
    connection = sqlite3.connect(temporary)
    try:
        connection.execute(
            """
            CREATE TABLE generation (
                year INTEGER NOT NULL,
                state TEXT NOT NULL,
                energy_source TEXT NOT NULL,
                generation_mwh INTEGER NOT NULL
            )
            """
        )
        with csv_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            connection.executemany(
                "INSERT INTO generation (year, state, energy_source, generation_mwh) VALUES (?, ?, ?, ?)",
                (
                    (int(row["year"]), row["state"], row["energy_source"], int(row["generation_mwh"]))
                    for row in reader
                ),
            )
        connection.commit()
    finally:
        connection.close()
    temporary.replace(db_path)
    return db_path
