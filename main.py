# pip install -r requirements.txt
import json

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
model = "claude-opus-5-5"


# ---------------------------------------------------------------------------
# Helpers (multi-turn conversations / system prompts)
# ---------------------------------------------------------------------------
def add_user_message(messages, content):
    messages.append({"role": "user", "content": content})


def add_assistant_message(messages, content):
    messages.append({"role": "assistant", "content": content})


def chat(messages, system=None, stop_sequences=None, output_schema=None):
    params = {
        "model": model,
        "max_tokens": 16000,
        "messages": messages,
        # Server-side fallback in case the model declines the request
        "betas": ["server-side-fallback-2026-07-01"],
        "fallbacks": "default",
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    if output_schema:
        # Structured outputs replace the old "prefill + stop sequence" trick
        params["output_config"] = {
            "format": {"type": "json_schema", "schema": output_schema}
        }

    response = client.beta.messages.create(**params)

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Request refused: {response.stop_details}")

    return next((b.text for b in response.content if b.type == "text"), "")


# ---------------------------------------------------------------------------
# Lesson: multi-turn conversation
# ---------------------------------------------------------------------------
messages = []
add_user_message(messages, "Define quantum computing in one sentence.")
answer = chat(messages)
add_assistant_message(messages, answer)
add_user_message(messages, "Write another sentence.")
print(chat(messages))


# ---------------------------------------------------------------------------
# Lesson: system prompts
# ---------------------------------------------------------------------------
system = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""
messages = []
add_user_message(messages, "How do I solve 5x + 2 = 3 for x?")
print(chat(messages, system=system))


# ---------------------------------------------------------------------------
# Lesson: response streaming
# ---------------------------------------------------------------------------
messages = []
add_user_message(messages, "Write a 1 sentence description of a fake database")

with client.messages.stream(
    model=model,
    max_tokens=16000,
    messages=messages,
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final_message = stream.get_final_message()
print()


# ---------------------------------------------------------------------------
# Lesson: structured data
# ---------------------------------------------------------------------------
messages = []
add_user_message(
    messages,
    "Generate three different sample AWS CLI commands. Each should be very short. "
    "Output only the commands, one per line, no explanations.",
)
print(chat(messages))


# ---------------------------------------------------------------------------
# Lesson: prompt evaluation - generating test datasets
# ---------------------------------------------------------------------------
DATASET_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"task": {"type": "string"}},
                "required": ["task"],
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

Please generate 3 objects.
"""
    messages = []
    add_user_message(messages, prompt)
    text = chat(messages, output_schema=DATASET_SCHEMA)
    return json.loads(text)["tasks"]


dataset = generate_dataset()
print(dataset)

with open("dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)
