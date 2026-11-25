# Lesson: prompt evaluation - generating test datasets
import json
from pathlib import Path

from academy.client import add_user_message, chat

DATASET_PATH = Path(__file__).parent / "datasets" / "aws_tasks.json"

DATASET_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    # Tells the grader which syntax validation to apply
                    "format": {"type": "string", "enum": ["python", "json", "regex"]},
                },
                "required": ["task", "format"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["tasks"],
    "additionalProperties": False,
}


def generate_dataset():
    prompt = """
Generate an evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
each representing a task that requires Python, JSON, or a Regex to complete.

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code

* Set "format" to the output format the task requires: "python", "json", or "regex"
* Include edge cases, such as invalid or malformed inputs, empty values, and optional parts
* Make every task self-contained and unambiguous, and do not repeat the same task

Please generate 12 objects: 4 for each format. At least 1 task per format must target edge cases.
"""
    messages = []
    add_user_message(messages, prompt)
    text = chat(messages, output_schema=DATASET_SCHEMA)
    return json.loads(text)["tasks"]


def main():
    # Keep the eval dataset stable: delete the file on purpose to regenerate it
    if DATASET_PATH.exists():
        raise SystemExit(f"{DATASET_PATH} already exists; delete it to regenerate")

    dataset = generate_dataset()
    print(dataset)

    with DATASET_PATH.open("x", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)


if __name__ == "__main__":
    main()
