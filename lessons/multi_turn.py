# Lesson: multi-turn conversation
from academy.client import add_assistant_message, add_user_message, chat

messages = []
add_user_message(messages, "Define quantum computing in one sentence.")
answer = chat(messages)
add_assistant_message(messages, answer)
add_user_message(messages, "Write another sentence.")
print(chat(messages))
