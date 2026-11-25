from anthropic import Anthropic

# Credentials come from the `ant auth login` profile (or ANTHROPIC_API_KEY)
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
