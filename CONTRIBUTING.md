# Contributing

This repository is a small reference agent. Changes should stay easy to read and easy to test.

## Setup

Python 3.11 or newer. From the repository root:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
```

## What belongs here

- A clearer parser for questions this table can already answer.
- A tighter check, with a test that shows the query does not run.
- Documentation that matches the code.

## What does not belong here

- Data, schemas, prompts, or code from an employer.
- A second dataset slipped in without a public source note in `data/SOURCE.md`.
- A path that executes a question as SQL, or that lets the question text choose the access role.
- Generated files (`data/generation.sqlite`, `__pycache__`).

## Pull requests

Open a small pull request. Say what question now works, or what unsafe statement is now refused. Run `python3 -m pytest` before you ask for review. The GitHub Actions workflow runs the same tests.

The code is under the MIT license in `LICENSE`.
