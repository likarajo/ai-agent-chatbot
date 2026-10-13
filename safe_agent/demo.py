"""Print a short scripted session. Nothing here is sent to a model provider."""

from safe_agent.access import Principal
from safe_agent.engine import answer

STEPS = (
    ("analyst", None, "How much wind generation did Texas produce in 2023?"),
    ("analyst", None, "Which fuel produced the most electricity in California in 2024?"),
    ("analyst", None, "What was customer revenue in Texas in 2023?"),
    ("state_reader", "TX", "How much wind generation did California produce in 2023?"),
    ("analyst", None, "How much wind generation in Texas in 2023; DROP TABLE generation"),
)


def main() -> None:
    for role, state, question in STEPS:
        print("=" * 72)
        print(f"role={role} state={state or '-'}")
        print(question)
        result = answer(question, Principal(role, state))
        print(result.explanation)
        if result.rows:
            print(result.rows)
        print()


if __name__ == "__main__":
    main()
