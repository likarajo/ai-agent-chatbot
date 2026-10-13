# Design patterns for safe natural-language-to-SQL agents

A plain-language question is a convenient way to ask a table something. It is also an easy way to let a user, or a confused generator, run a statement nobody reviewed. The agent in [ai-agent-chatbot](https://github.com/likarajo/ai-agent-chatbot) is a small public reference for one table: U.S. net electricity generation for 2020–2024, published by the Energy Information Administration. The patterns below are the ones that code actually uses. They do not depend on a particular model, because this agent does not call one.

## 1. Keep the question out of the SQL string

The unsafe pattern is to embed the user’s sentence in the statement, or to ask a model for a full SQL string and run it. This agent never does that. `safe_agent/parse.py` maps the sentence onto a closed intent: years, state codes, energy sources, a grouping, and an optional limit. `safe_agent/sql.py` then fills one fixed shape, `SELECT … SUM(generation_mwh) … FROM generation`, and puts every value in a `?` parameter.

If the sentence cannot be mapped, the result is a refusal. There is no fallback that “tries the SQL anyway.”

## 2. Refuse columns the schema does not have

A generator that is trying to be helpful will invent `revenue`, `customer`, or `password` when those words appear. Here those words are a stop, not a hint. The parser checks them before it builds anything. The query checker repeats the rule on the statement itself: an identifier must be the table `generation`, one of `year`, `state`, `energy_source`, and `generation_mwh`, the function `SUM`, or an ordinary SQL word such as `WHERE` and `GROUP`.

The refusal for a revenue question names the missing idea and lists the real columns. It does not return an empty table that looks like a successful zero.

## 3. Check the statement before the database sees it

Parameterization is not the whole check. `safe_agent/validate.py` still rejects a second statement, a comment, `SELECT *`, `UNION`, and words such as `DROP`, `INSERT`, `ATTACH`, and `load_extension`. A question that ends in `; DROP TABLE generation` is refused at the parser, and the same shape is refused again if it shows up as SQL.

The tests pin both layers down. They include the unsafe strings, and they count the table before and after an injection attempt.

## 4. Apply row access outside the question

People will ask an agent to “ignore the previous rules.” If the access rule lives in the prompt, that request is a feature. In this agent the role is a `Principal` supplied by the caller. The web page sends it in a separate field from the question.

For a state reader, `safe_agent/access.py` runs after the checker. It replaces `FROM generation` with a subquery:

```sql
FROM (
  SELECT year, state, energy_source, generation_mwh
  FROM generation
  WHERE state = ?
) AS generation
```

The bound state is the assigned one. A Texas reader who asks about California still produces a predicate for California, and the wrapper adds Texas. The intersection is empty, and the explanation says California was left out. An analyst does not get the wrapper. The national `US` row stays available to analysts and stays out of state rankings, because it is a total rather than a state.

## 5. Open the database so it cannot write

The last control is the connection. `safe_agent/db.py` builds a local SQLite file from the committed CSV, then opens it with `mode=ro`. A test attempts `DELETE FROM generation` on that connection and expects the database to refuse. The agent has no insert, update, or schema path.

## 6. Explain the query that ran

A number with no trail is hard to trust. Every successful answer says what was summed, which place and years were used, which columns were touched, which role was applied, and how many rows came back. The demo also shows the statement and the bound parameters. A refusal explains the stop and does not pretend a query ran.

## What this reference leaves out

The parser only covers one public table and a narrow set of English questions. It will not answer an arbitrary warehouse. The demo lets a person pick the role, so the wrapper is visible. An application would take the role from the session instead. There is no model call to swap in. Adding one would still have to end at the same checker and the same access wrapper. The model would be allowed to propose an intent, not a statement.

The dataset notes, the recording script, and the file-by-file diagram are in the repository: `data/SOURCE.md`, `docs/demo-script.md`, and `docs/architecture.md`.
