# Lesson: structured data
from academy.client import add_user_message, chat

messages = []
add_user_message(
    messages,
    "Generate three different sample AWS CLI commands. Each should be very short. "
    "Output only the commands, one per line, no explanations.",
)
print(chat(messages))
