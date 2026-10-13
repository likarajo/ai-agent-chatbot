"""Turn a plain-language question into a structured request.

The parser never copies the question into SQL. It only fills a fixed set of
filters, groupings, and a limit. Unknown columns are refused here.
"""

import re
from dataclasses import dataclass, field

from safe_agent.errors import Refusal
from safe_agent.schema import ENERGY_SOURCES, OUTSIDE_SCHEMA, STATES, YEARS

GENERATION_WORDS = re.compile(
    r"\b(generation|electricity|power|megawatthours|mwh|generated|produce|produced)\b",
    re.IGNORECASE,
)
RANGE_YEARS = re.compile(r"\b(20\d\d)\s*(?:to|through|-)\s*(20\d\d)\b", re.IGNORECASE)
YEAR = re.compile(r"\b(20\d\d)\b")
TOP_N = re.compile(r"\btop\s+(\d+)\b", re.IGNORECASE)
SUPERLATIVE_HIGH = re.compile(r"\b(most|highest|largest|greatest|top)\b", re.IGNORECASE)
SUPERLATIVE_LOW = re.compile(r"\b(least|lowest|smallest|fewest)\b", re.IGNORECASE)
INJECTION = re.compile(
    r"(--|;|/\*|\*/|\bor\s+1\s*=\s*1\b|\bdrop\b|\bdelete\b|\binsert\b|\bupdate\b|\balter\b|\battach\b|\bpragma\b|\bunion\b)",
    re.IGNORECASE,
)
RAW_SQL = re.compile(r"\bselect\b.+\bfrom\b", re.IGNORECASE | re.DOTALL)


@dataclass
class Intent:
    years: list[int] = field(default_factory=list)
    states: list[str] = field(default_factory=list)
    fuels: list[str] = field(default_factory=list)
    group_by: list[str] = field(default_factory=list)
    direction: str = "DESC"
    limit: int | None = None
    year_range: bool = False


def parse_question(question: str) -> Intent:
    text = (question or "").strip()
    if not text:
        raise Refusal("Enter a question about net electricity generation.")
    if INJECTION.search(text) or RAW_SQL.search(text):
        raise Refusal(
            "That question includes SQL or a second command, so it was not run. "
            "Ask in plain language about generation, a state, a year, and an energy source."
        )
    lowered = text.lower()
    outside = _outside_term(lowered)
    if outside:
        raise Refusal(
            f"This dataset has no {outside} column or energy source. "
            "Available columns are year, state, energy_source, and generation_mwh. "
            "Energy sources include coal, natural gas, nuclear, wind, solar, hydroelectric, "
            "geothermal, petroleum, biomass, wood, and pumped storage."
        )
    if not GENERATION_WORDS.search(text):
        raise Refusal(
            "I can answer questions about net electricity generation in megawatthours "
            "by state, year, and energy source for 2020 through 2024."
        )

    intent = Intent()
    intent.years = _years(text)
    intent.states = _states(text)
    intent.fuels = _fuels(lowered)
    intent.group_by = _groups(lowered)
    intent.direction, intent.limit, intent.year_range = _ordering(lowered, intent)
    if intent.year_range and "year" not in intent.group_by and not intent.limit:
        intent.group_by.insert(0, "year")
    if len(intent.states) > 1 and "state" not in intent.group_by:
        intent.group_by.append("state")
    if intent.limit and not intent.group_by:
        if not intent.fuels:
            intent.group_by.append("energy_source")
        elif not intent.states:
            intent.group_by.append("state")
        else:
            intent.limit = None
    return intent


def _outside_term(lowered: str) -> str | None:
    for term in OUTSIDE_SCHEMA:
        if re.search(rf"\b{re.escape(term)}\b", lowered):
            return term
    return None


def _years(text: str) -> list[int]:
    span = RANGE_YEARS.search(text)
    if span:
        start, end = int(span.group(1)), int(span.group(2))
        if start > end:
            start, end = end, start
        found = list(range(start, end + 1))
    else:
        found = [int(match) for match in YEAR.findall(text)]
    if not found:
        return []
    unique = list(dict.fromkeys(found))
    bad = [year for year in unique if year not in YEARS]
    if bad:
        raise Refusal(
            f"This dataset covers {YEARS[0]} through {YEARS[-1]}. "
            f"{bad[0]} is outside that range."
        )
    return unique


def _states(text: str) -> list[str]:
    found: list[str] = []
    consumed = text
    names = sorted(STATES.items(), key=lambda item: len(item[1]), reverse=True)
    for code, name in names:
        pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
        if pattern.search(consumed):
            found.append(code)
            consumed = pattern.sub(" ", consumed)
    if re.search(r"\b(?:nationwide|national)\b", text, re.IGNORECASE):
        found.append("US")
    for code in STATES:
        if code == "US":
            continue
        if re.search(rf"\b{code}\b", text):
            found.append(code)
    if re.search(r"\bUS\b", text) or re.search(r"\bU\.S\.\b", text):
        found.append("US")
    return list(dict.fromkeys(found))


def _fuels(lowered: str) -> list[str]:
    found: list[str] = []
    consumed = lowered
    for phrase, canonical in ENERGY_SOURCES:
        pattern = re.compile(rf"\b{re.escape(phrase)}\b")
        if pattern.search(consumed):
            found.append(canonical)
            consumed = pattern.sub(" ", consumed)
    return list(dict.fromkeys(found))


def _groups(lowered: str) -> list[str]:
    groups: list[str] = []
    if re.search(r"\b(by year|each year|over time|per year)\b", lowered):
        groups.append("year")
    if re.search(r"\b(by fuel|by source|by energy source|which fuel|what fuel|which energy source|what energy source)\b", lowered):
        groups.append("energy_source")
    if re.search(r"\b(by state|which state|what state|per state|which states|top\s+\d+\s+states)\b", lowered):
        groups.append("state")
    return groups


def _ordering(lowered: str, intent: Intent) -> tuple[str, int | None, bool]:
    top = TOP_N.search(lowered)
    high = SUPERLATIVE_HIGH.search(lowered)
    low = SUPERLATIVE_LOW.search(lowered)
    year_range = RANGE_YEARS.search(lowered) is not None
    if top:
        count = int(top.group(1))
        if count < 1 or count > 50:
            raise Refusal("Ask for a top list between 1 and 50.")
        return "DESC", count, year_range
    if high:
        return "DESC", 1, year_range
    if low:
        return "ASC", 1, year_range
    return "DESC", None, year_range
