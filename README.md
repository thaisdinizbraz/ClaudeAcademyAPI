# ClaudeAcademyAPI

Code for the [Building with the Claude API](https://academy.claude.com/courses/building-with-the-claude-api/) course from Claude Academy.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
ant auth login   # or: export ANTHROPIC_API_KEY=...
```

## Run

Each lesson is a standalone script:

```bash
python lessons/multi_turn.py
```

Generate the eval dataset (never overwrites an existing one):

```bash
python evals/generate_dataset.py
```

## Current structure

```
ClaudeAcademyAPI/
├── src/
│   └── academy/
│       ├── __init__.py
│       └── client.py            # client, model, message helpers, chat
├── lessons/                     # one runnable script per lesson
│   ├── multi_turn.py
│   ├── system_prompts.py
│   ├── streaming.py
│   └── structured_data.py
├── evals/
│   ├── generate_dataset.py      # run manually
│   └── datasets/
│       └── aws_tasks.json       # versioned
├── pyproject.toml
└── README.md
```

## Ideal structure

Target layout as the course progresses:

```
ClaudeAcademyAPI/
├── src/
│   └── academy/
│       ├── __init__.py
│       └── client.py            # client, model, message helpers, chat
├── lessons/                     # one runnable script per lesson
│   ├── multi_turn.py
│   ├── system_prompts.py
│   ├── streaming.py
│   └── structured_data.py
├── evals/
│   ├── generate_dataset.py      # run manually
│   ├── run_eval.py              # reads dataset, runs prompt, grades
│   ├── graders.py               # code and model graders
│   ├── datasets/
│   │   └── aws_tasks.json       # versioned
│   └── results/                 # gitignored
├── tests/                       # pytest, no real API calls
│   ├── test_client.py
│   └── test_graders.py
├── pyproject.toml
└── README.md
```

## Branches

- `develop`: default branch, all development happens here
- `main`: releases only, updated by merging `develop`
