# Lesson: prompt evaluation - running the eval
import argparse
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from statistics import mean

from academy.client import add_user_message, chat
from anthropic import AnthropicError

from graders import grade

EVALS_DIR = Path(__file__).parent
DATASET_PATH = EVALS_DIR / "datasets" / "aws_tasks.json"
RESULTS_DIR = EVALS_DIR / "results"
MAX_WORKERS = 4

# The prompt under evaluation: edit it and rerun to compare scores
PROMPT_TEMPLATE = """
Solve the following task:

{task}

* Respond only with the {format} solution, without explanations or markdown code fences
"""


def strip_code_fence(text):
    match = re.fullmatch(r"```[\w-]*\n(.*?)\n?```", text.strip(), re.DOTALL)
    return match.group(1) if match else text.strip()


def run_prompt(test_case):
    messages = []
    add_user_message(messages, PROMPT_TEMPLATE.format(**test_case))
    return strip_code_fence(chat(messages))


def run_test_case(test_case):
    result = {"test_case": test_case}
    try:
        result["output"] = run_prompt(test_case)
        result.update(grade(test_case, result["output"]))
    except (AnthropicError, RuntimeError, json.JSONDecodeError) as e:
        # Failed calls are reported separately instead of scored as zero
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def run_eval(dataset):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        return list(executor.map(run_test_case, dataset))


def print_report(results):
    for result in results:
        case = result["test_case"]
        label = f"{case['format']:<6} {case['task'][:60]}"
        if "error" in result:
            print(f"ERROR  {label} ({result['error']})")
        else:
            print(
                f"{result['score']:>5.1f}  {label} "
                f"(syntax {result['syntax_score']}, model {result['model_grade']['score']})"
            )
    scores = [r["score"] for r in results if "error" not in r]
    errors = len(results) - len(scores)
    average = f"{mean(scores):.2f}" if scores else "n/a"
    print(f"\nAverage score: {average} ({len(scores)} graded, {errors} errors)")


def main():
    parser = argparse.ArgumentParser(description="Run the prompt evaluation")
    parser.add_argument("--limit", type=int, help="only run the first N test cases")
    args = parser.parse_args()

    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))[: args.limit]
    results = run_eval(dataset)
    print_report(results)

    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}.json"
    report = {"prompt_template": PROMPT_TEMPLATE, "results": results}
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Results saved to {path}")


if __name__ == "__main__":
    main()
