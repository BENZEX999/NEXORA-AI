#!/usr/bin/env python3
"""NEXORA-AI: local-first cybersecurity learning assistant."""

import json
import os
import sys
from datetime import datetime, timezone

import requests

SYSTEM_PROMPT = """You are NEXORA-AI, a cybersecurity learning assistant.

Your purpose is authorized education, defensive security, secure architecture,
hardening, threat modeling, malware analysis at a conceptual level, and
incident response.

You must not provide instructions for unauthorized access, credential theft,
malware delivery, persistence, privilege escalation, evasion, exploitation,
or actions against real-world targets. Do not execute commands, claim you
performed a test, or present uncertain facts as confirmed observations.

For potentially dangerous requests:
1. Explain the safety or authorization concern.
2. Offer a safe local lab, simulation, documentation, checklist, or defensive
   alternative.
3. Encourage written permission before testing systems.

Be precise, distinguish explanation from verification, and state assumptions.
"""

DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
ENDPOINT = os.getenv("NEXORA_ENDPOINT", DEFAULT_ENDPOINT)
MODEL = os.getenv("NEXORA_MODEL", "local-model")
API_KEY = os.getenv("NEXORA_API_KEY")
MAX_TURNS = max(1, int(os.getenv("NEXORA_MAX_TURNS", "8")))
SAVE_HISTORY = os.getenv("NEXORA_SAVE_HISTORY", "0") == "1"
HISTORY_FILE = os.path.expanduser(
    os.getenv("NEXORA_HISTORY_FILE", "$HOME/nexora-history.jsonl")
)


def chat(messages):
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    response = requests.post(
        ENDPOINT,
        headers=headers,
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": 0.3,
        },
        timeout=180,
    )

    if not response.ok:
        raise RuntimeError(
            f"Provider returned HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    try:
        return response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("The provider returned an unexpected response.") from exc


def append_history(role, content):
    if not SAVE_HISTORY:
        return

    parent = os.path.dirname(HISTORY_FILE)
    if parent:
        os.makedirs(parent, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "role": role,
        "content": content,
    }
    with open(HISTORY_FILE, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def print_help():
    print("""
Commands:
  /help   Show this help
  /reset  Clear the current conversation
  /quit   Exit

Example topics:
  Explain MFA and where it can fail
  Create an incident-response checklist
  Review security principles for a small web application
  Explain DNS, TLS, or Linux permissions
  Suggest an authorized local cybersecurity lab
""")


def main():
    print("NEXORA-AI — Cybersecurity Learning Assistant")
    print(f"Endpoint: {ENDPOINT}")

    if ENDPOINT.startswith(("http://127.0.0.1", "http://localhost")):
        print("Mode: offline/local")
    else:
        print("Mode: online — prompts leave this device")

    print("Type /help for help or /quit to exit.")

    history = []

    while True:
        try:
            user_text = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_text:
            continue

        command = user_text.lower()
        if command in {"/quit", "/exit"}:
            break
        if command == "/reset":
            history.clear()
            print("Conversation cleared.")
            continue
        if command == "/help":
            print_help()
            continue

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history[-(MAX_TURNS * 2):])
        messages.append({"role": "user", "content": user_text})

        try:
            answer = chat(messages)
        except (requests.RequestException, RuntimeError) as exc:
            print(f"\nError: {exc}", file=sys.stderr)
            continue

        print(f"\nNEXORA> {answer}")

        history.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": answer},
        ])
        append_history("user", user_text)
        append_history("assistant", answer)


if __name__ == "__main__":
    main()
