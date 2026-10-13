"""Ask a question. Validation and row access run before SQLite sees it."""

from dataclasses import dataclass, field

from safe_agent.access import Principal, apply_row_filter
from safe_agent.db import connect_readonly
from safe_agent.errors import Refusal, UnsafeSQL
from safe_agent.explain import explain
from safe_agent.parse import Intent, parse_question
from safe_agent.sql import build_sql
from safe_agent.validate import validate_sql


@dataclass
class Answer:
    ok: bool
    explanation: str
    sql: str | None = None
    params: list = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "explanation": self.explanation,
            "sql": self.sql,
            "params": self.params,
            "columns": self.columns,
            "rows": self.rows,
        }


def answer(question: str, principal: Principal) -> Answer:
    try:
        intent = parse_question(question)
        sql, params = build_sql(intent)
        validate_sql(sql)
        limited_sql, access_params = apply_row_filter(sql, principal)
        rows = _run(limited_sql, [*access_params, *params])
        return Answer(
            ok=True,
            explanation=explain(intent, principal, rows),
            sql=limited_sql,
            params=[*access_params, *params],
            columns=list(rows[0].keys()) if rows else _columns(intent),
            rows=rows,
        )
    except (Refusal, UnsafeSQL) as exc:
        return Answer(ok=False, explanation=exc.message)


def _run(sql: str, params: list) -> list[dict]:
    connection = connect_readonly()
    try:
        cursor = connection.execute(sql, params)
        rows = [dict(row) for row in cursor.fetchall()]
        if len(rows) == 1 and all(value is None for value in rows[0].values()):
            return []
        return rows
    finally:
        connection.close()


def _columns(intent: Intent) -> list[str]:
    return [*intent.group_by, "generation_mwh"]
