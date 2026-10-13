# Demo recording script

About four minutes. Record the browser, plus a short terminal cut at the end. Use a quiet desktop and a window around 1100 pixels wide.

Before you start:

```bash
cd ai-agent-chatbot
python3 -m pytest
python3 -m safe_agent
```

Leave the server running. Open http://127.0.0.1:8642/. The role should say **Analyst, all states**.

Say, in your own words: this agent answers plain-language questions about a public electricity table. It does not paste the question into SQL. It checks one read-only query, and a state reader cannot see another state.

## 1. A real published figure (about 45 seconds)

Leave the question that is already in the box:

> How much wind generation did Texas produce in 2023?

Click **Ask**.

Point at three things on screen:

- The result **119,855,132 megawatthours**.
- The sentence that names the columns `year`, `state`, `energy_source`, and `generation_mwh`.
- The SQL underneath. It is a single `SELECT` with `?` parameters, and the parameters are `2023`, `TX`, and `Wind`.

Say that this number is the Energy Information Administration row for Texas wind in 2023, not a model estimate.

## 2. A question the schema cannot answer (about 30 seconds)

Click the example **What was customer revenue in Texas in 2023?** Then click **Ask**.

The page should refuse. It should say there is no revenue column, and it should not show SQL or a table.

Say that an unknown column is stopped before a query is built.

## 3. The state reader (about 60 seconds)

Change **Role** to **State reader, one state**. Set **Assigned state** to Texas.

Click the example **How much wind generation did California produce in 2023?** Then click **Ask**.

Point at the explanation:

- The role is a state reader for Texas.
- The filter was added before the query ran.
- California was asked for and left out.
- Rows returned: 0.

Point at the SQL. The table is a subquery with `WHERE state = ?`, and the first parameter is `TX`. The outer predicate still says California, so the two filters do not overlap.

Say that the question text cannot switch the role or widen the state. The page sends the role separately from the question.

## 4. A ranking, still as the analyst (about 40 seconds)

Switch the role back to **Analyst, all states**. Click **Top 5 states for wind generation in 2024**, then **Ask**.

You should see five states, largest first, and `US` should not be one of them. The national total is not a state.

## 5. Terminal, optional (about 30 seconds)

In a second terminal, from the same directory:

```bash
python3 -m safe_agent.cli \
  "How much wind generation in Texas in 2023; DROP TABLE generation"
```

The JSON has `"ok": false` and `"sql": null`. Then run:

```bash
python3 -m pytest -q
```

Stop on the passing summary. Say that the same tests run in GitHub Actions.

Stop the server with Ctrl-C when you are done.
