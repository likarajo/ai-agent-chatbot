"""Ask one question from the terminal."""

import argparse
import json

from safe_agent.access import Principal
from safe_agent.engine import answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the safe generation agent one question.")
    parser.add_argument("question")
    parser.add_argument("--role", default="analyst", choices=("analyst", "state_reader"))
    parser.add_argument("--state", default=None, help="Assigned state for a state reader, such as TX")
    args = parser.parse_args()
    result = answer(args.question, Principal(args.role, args.state))
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
