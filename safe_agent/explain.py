"""Say what the query did, including the access limit."""

from safe_agent.access import Principal
from safe_agent.parse import Intent
from safe_agent.schema import STATES


def explain(intent: Intent, principal: Principal, rows: list[dict]) -> str:
    lines = [_what(intent)]
    access = _access(intent, principal)
    if access:
        lines.append(access)
    lines.append(
        "Columns used: year, state, energy_source, and generation_mwh."
    )
    lines.append(f"Rows returned: {len(rows)}.")
    if len(rows) == 1 and set(rows[0]) == {"generation_mwh"}:
        lines.append(f"Result: {_mwh(rows[0]['generation_mwh'])}.")
    elif len(rows) == 1:
        lines.append("Result: " + _row_phrase(rows[0]) + ".")
    return " ".join(lines)


def _what(intent: Intent) -> str:
    fuel = ", ".join(intent.fuels) if intent.fuels else "all listed energy sources"
    place = _places(intent.states) if intent.states else "every state in the table"
    if intent.years:
        when = ", ".join(str(year) for year in intent.years)
    else:
        when = "2020 through 2024"
    action = "Summed"
    if intent.group_by:
        grouped = ", ".join(intent.group_by)
        action = f"Grouped by {grouped} and summed"
    return f"{action} {fuel} net generation for {place} in {when}, in megawatthours."


def _access(intent: Intent, principal: Principal) -> str:
    if principal.role == "analyst":
        return "Access role: analyst, which can read every state."
    code = principal.state_code()
    name = STATES.get(code or "", code)
    message = (
        f"Access role: state reader for {name}. "
        "The state filter was added by the access wrapper before the query ran, not by the question."
    )
    blocked = [STATES[item] for item in intent.states if item != code]
    if blocked:
        message += f" The question also asked for {', '.join(blocked)}, and those rows were left out."
    return message


def _places(codes: list[str]) -> str:
    return ", ".join(STATES.get(code, code) for code in codes)


def _row_phrase(row: dict) -> str:
    bits = []
    for key, value in row.items():
        if key == "generation_mwh":
            bits.append(_mwh(value))
        elif key == "state":
            bits.append(STATES.get(str(value), str(value)))
        else:
            bits.append(f"{key} {value}")
    return ", ".join(bits)


def _mwh(value) -> str:
    return f"{int(value):,} megawatthours"
