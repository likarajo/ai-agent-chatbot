import sqlite3
from pathlib import Path

from safe_agent.access import Principal
from safe_agent.db import DB_PATH, build_database, connect_readonly
from safe_agent.engine import answer
from safe_agent.validate import validate_sql
from safe_agent.errors import UnsafeSQL
import pytest

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "eia_net_generation_2020_2024.csv"


def _cell(year, state, source):
    import csv
    with CSV.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["year"]) == year and row["state"] == state and row["energy_source"] == source:
                return int(row["generation_mwh"])
    raise AssertionError(f"missing {year} {state} {source}")


def test_texas_wind_2023_matches_eia_row():
    result = answer("How much wind generation did Texas produce in 2023?", Principal("analyst"))
    assert result.ok
    assert result.rows == [{"generation_mwh": _cell(2023, "TX", "Wind")}]
    assert result.rows[0]["generation_mwh"] == 119_855_132
    assert "119,855,132" in result.explanation


def test_top_fuel_in_california_is_a_single_known_source():
    result = answer(
        "Which fuel produced the most electricity in California in 2024?",
        Principal("analyst"),
    )
    assert result.ok
    assert len(result.rows) == 1
    assert "energy_source" in result.rows[0]
    assert result.rows[0]["generation_mwh"] > 0


def test_compare_two_states_returns_both():
    result = answer(
        "Compare wind generation in Texas and California in 2023",
        Principal("analyst"),
    )
    assert result.ok
    assert {row["state"] for row in result.rows} == {"TX", "CA"}


def test_unknown_column_is_refused():
    result = answer("What was customer revenue in Texas in 2023?", Principal("analyst"))
    assert not result.ok
    assert result.sql is None
    assert "revenue" in result.explanation


def test_year_outside_the_table_is_refused():
    result = answer("How much wind generation did Texas produce in 2010?", Principal("analyst"))
    assert not result.ok
    assert "2010" in result.explanation


def test_injection_is_refused_and_the_table_remains():
    before = _count()
    result = answer(
        "How much wind generation in Texas in 2023; DROP TABLE generation",
        Principal("analyst"),
    )
    assert not result.ok
    assert result.sql is None
    assert _count() == before


def test_state_reader_cannot_read_another_state():
    texas = answer(
        "How much wind generation did California produce in 2023?",
        Principal("state_reader", "TX"),
    )
    assert texas.ok
    assert texas.rows == []
    assert "Texas" in texas.explanation
    assert "California" in texas.explanation
    assert texas.params[0] == "TX"


def test_state_reader_total_is_only_the_assigned_state():
    limited = answer("Total wind generation in 2023", Principal("state_reader", "Texas"))
    national = answer("Total wind generation in the United States in 2023", Principal("analyst"))
    assert limited.ok and national.ok
    assert limited.rows[0]["generation_mwh"] == _cell(2023, "TX", "Wind")
    assert national.rows[0]["generation_mwh"] != limited.rows[0]["generation_mwh"]


def test_top_five_states_for_wind():
    result = answer("Top 5 states for wind generation in 2024", Principal("analyst"))
    assert result.ok
    assert len(result.rows) == 5
    amounts = [row["generation_mwh"] for row in result.rows]
    assert amounts == sorted(amounts, reverse=True)
    assert "US" not in {row["state"] for row in result.rows}


def test_database_connection_is_read_only():
    build_database()
    connection = connect_readonly()
    try:
        with pytest.raises(sqlite3.OperationalError):
            connection.execute("DELETE FROM generation")
    finally:
        connection.close()
    assert DB_PATH.exists()


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM generation",
        "SELECT generation_mwh FROM generation; DROP TABLE generation",
        "SELECT generation_mwh FROM generation UNION SELECT generation_mwh FROM generation",
        "SELECT generation_mwh FROM generation -- hide",
        "SELECT load_extension('x')",
        "SELECT password FROM generation",
        "DELETE FROM generation",
    ],
)
def test_validator_blocks_unsafe_sql(sql):
    with pytest.raises(UnsafeSQL):
        validate_sql(sql)


def _count() -> int:
    connection = connect_readonly()
    try:
        return connection.execute("SELECT COUNT(*) AS n FROM generation").fetchone()["n"]
    finally:
        connection.close()
