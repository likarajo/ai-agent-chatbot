"""Apply row access from the caller, never from the question text."""

from dataclasses import dataclass

from safe_agent.errors import Refusal
from safe_agent.schema import STATES, TABLE

# Demo row-level roles are only issued for these two states.
READER_STATES = {
    "TX": STATES["TX"],
    "CA": STATES["CA"],
}


@dataclass(frozen=True)
class Principal:
    role: str
    state: str | None = None

    def state_code(self) -> str | None:
        if self.state is None:
            return None
        token = self.state.strip()
        if token.upper() in STATES:
            return token.upper()
        for code, name in STATES.items():
            if name.lower() == token.lower():
                return code
        raise Refusal(f"{self.state} is not a state in this dataset.")


def apply_row_filter(sql: str, principal: Principal) -> tuple[str, list]:
    """Replace the base table with a filtered subquery for a state reader.

    The replacement is written here, after validation, so a question cannot
    widen it. The bound parameter is returned first because it appears first
    in the statement. Only Texas and California are valid reader assignments.
    """
    role = principal.role.strip().lower()
    if role == "analyst":
        return sql, []
    if role != "state_reader":
        raise Refusal("Choose the analyst role or the state reader role.")
    code = principal.state_code()
    if not code or code == "US":
        raise Refusal("A state reader has to be assigned one state.")
    if code not in READER_STATES:
        names = " or ".join(READER_STATES.values())
        raise Refusal(f"This demo only issues state-reader roles for {names}.")
    filtered = (
        "(SELECT year, state, energy_source, generation_mwh "
        f"FROM {TABLE} WHERE state = ?)"
    )
    rewritten, count = _replace_from(sql, filtered)
    if count != 1:
        raise Refusal("The query could not be limited to the assigned state, so it was not run.")
    return rewritten, [code]


def _replace_from(sql: str, filtered: str) -> tuple[str, int]:
    import re

    return re.subn(
        rf"\bFROM\s+{TABLE}\b",
        f"FROM {filtered} AS {TABLE}",
        sql,
        count=1,
    )
