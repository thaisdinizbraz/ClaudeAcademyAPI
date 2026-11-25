# Lesson: system prompts
from academy.client import add_user_message, chat

system = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""
messages = []
add_user_message(messages, "How do I solve 5x + 2 = 3 for x?")
print(chat(messages, system=system))
