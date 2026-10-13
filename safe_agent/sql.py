"""Build a parameterized SELECT from a parsed question."""

from safe_agent.parse import Intent
from safe_agent.schema import TABLE


def build_sql(intent: Intent) -> tuple[str, list]:
    select = [column for column in intent.group_by]
    select.append("SUM(generation_mwh) AS generation_mwh")
    where: list[str] = []
    params: list = []

    if intent.years:
        where.append(_in_clause("year", intent.years, params))
    if "state" in intent.group_by:
        named = [code for code in intent.states if code != "US"]
        if named:
            where.append(_in_clause("state", named, params))
        else:
            where.append("state != 'US'")
    elif intent.states:
        where.append(_in_clause("state", intent.states, params))
    if intent.fuels and "energy_source" not in intent.group_by:
        where.append(_in_clause("energy_source", intent.fuels, params))

    sql = f"SELECT {', '.join(select)} FROM {TABLE}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    if intent.group_by:
        sql += " GROUP BY " + ", ".join(intent.group_by)
        sql += f" ORDER BY generation_mwh {intent.direction}"
    if intent.limit is not None:
        sql += f" LIMIT {int(intent.limit)}"
    return sql, params


def _in_clause(column: str, values: list, params: list) -> str:
    params.extend(values)
    if len(values) == 1:
        return f"{column} = ?"
    marks = ", ".join("?" for _ in values)
    return f"{column} IN ({marks})"
