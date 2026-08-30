import json
import re

import requests
from django.utils import timezone

from menu.models import Category

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma2:2b"


def _clean_reply(raw_reply):
    text = raw_reply.strip()
    text = re.sub(r"^```(text)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())
    return text.strip()


def _ask_ollama(prompt):
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    headers = {"Accept": "*/*", "Content-Type": "application/json"}
    response = requests.post(OLLAMA_URL, headers=headers, data=json.dumps(payload), timeout=60)
    response.raise_for_status()
    return response.json()["response"]


def build_cafe_context():
    """Grounds the model in real, current data so it never invents menu items or prices."""
    lines = [
        "You are the friendly front-desk assistant for CafeFlow, a cafe in Butwal, Lumbini Province, Nepal.",
        "Opening hours: 7:00 AM to 9:00 PM, open daily.",
        "We offer dine-in, pickup, and online ordering. Customers can browse the menu and order at /menu/.",
        "",
        "Here is our current menu:",
    ]

    categories = Category.objects.prefetch_related("items").all()
    for category in categories:
        available_items = [item for item in category.items.all() if item.is_available]
        if not available_items:
            continue
        lines.append(f"\n{category.name}:")
        for item in available_items:
            lines.append(f"- {item.name}: Rs.{item.price}")

    lines.append(
        "\nAnswer customer questions warmly and briefly, using only the information above. "
        "If you don't know something, say you'll have staff confirm it — never invent menu items, prices, or policies."
    )
    return "\n".join(lines)


def get_chatbot_reply(message, history):
    """
    history: list of {"role": "user"/"assistant", "text": "..."} dicts, most recent last.
    Returns plain text reply.
    """
    context = build_cafe_context()

    convo = ""
    for turn in history[-6:]:  # keep only the last few turns so the prompt doesn't grow unbounded
        speaker = "Customer" if turn["role"] == "user" else "You"
        convo += f"{speaker}: {turn['text']}\n"

    prompt = f"""{context}

Conversation so far:
{convo}Customer: {message}
You:"""

    try:
        raw_reply = _ask_ollama(prompt)
        return _clean_reply(raw_reply)
    except requests.RequestException:
        return "Sorry, I'm having trouble connecting right now — please ask a staff member directly."