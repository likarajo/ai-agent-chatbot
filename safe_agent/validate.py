"""Reject anything other than a single read of the published columns."""

import re

from safe_agent.errors import UnsafeSQL
from safe_agent.schema import ALLOWED_IDENTIFIERS, FORBIDDEN_SQL, SQL_KEYWORDS

TOKEN = re.compile(
    r"\s+|(?:'(?:''|[^'])*')|\?|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*|<>|!=|>=|<=|[=(),]"
)


def validate_sql(sql: str) -> None:
    text = (sql or "").strip()
    if not text:
        raise UnsafeSQL("The query was empty, so it was not run.")
    if "--" in text or "/*" in text or "*/" in text:
        raise UnsafeSQL("Comments are not allowed in a generated query.")
    body = text[:-1] if text.endswith(";") else text
    if ";" in body:
        raise UnsafeSQL("Only one statement can run.")
    if "*" in body:
        raise UnsafeSQL("Select the published columns by name.")

    tokens = TOKEN.findall(body)
    if "".join(tokens) != body:
        raise UnsafeSQL("The query contains a character that is not allowed.")
    words = [token for token in tokens if token.strip() and not token.isspace()]
    if not words or words[0].lower() != "select":
        raise UnsafeSQL("Only a SELECT query can run.")

    for token in words:
        if token in {"?", "=", ",", "(", ")", "!=", "<>", ">=", "<="} or token.startswith("'") or token[0].isdigit():
            continue
        name = token.lower()
        if name in FORBIDDEN_SQL:
            raise UnsafeSQL(f"The query uses {token}, so it was not run.")
        if name not in SQL_KEYWORDS and name not in ALLOWED_IDENTIFIERS:
            raise UnsafeSQL(
                f"The query refers to {token}, which is not in the schema. "
                "Allowed columns are year, state, energy_source, and generation_mwh."
            )
