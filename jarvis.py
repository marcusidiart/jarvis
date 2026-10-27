"""JARVIS, milestone 1: a typing-only assistant that can search Google Maps.

Run it with:  python jarvis.py
"""

import json

import anthropic
from dotenv import load_dotenv

load_dotenv()  # reads your keys from the .env file

from tools import TOOLS, run_tool  # noqa: E402  (needs the keys loaded first)

client = anthropic.Anthropic()

MODEL = "claude-opus-5-5"

SYSTEM = (
    "You are JARVIS, a calm, witty British AI assistant, in the style of Tony "
    "Stark's butler AI. Address the user as 'sir'. Keep replies short, because "
    "they will be spoken out loud later. Use your tools to get real work done "
    "instead of guessing. Never send anything to a real person without asking "
    "the user first."
)


def ask_claude(messages):
    """Send the conversation to Claude and get its next reply."""
    return client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        tools=TOOLS,
        messages=messages,
        output_config={"effort": "medium"},
        # If Claude declines a request, retry it on a backup model automatically.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )


def main():
    print("JARVIS online. Type 'quit' to exit.\n")
    messages = []

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in {"quit", "exit"}:
            print("JARVIS: Very good, sir.")
            break
        if not user_text:
            continue
        messages.append({"role": "user", "content": user_text})

        # The agent loop: keep going while Claude wants to use tools.
        while True:
            reply = ask_claude(messages)
            # Save Claude's full reply (text + tool requests) to the history.
            messages.append({"role": "assistant", "content": reply.content})

            if reply.stop_reason == "refusal":
                print("JARVIS: I'm afraid I can't help with that one, sir.\n")
                break

            if reply.stop_reason != "tool_use":
                text = "".join(b.text for b in reply.content if b.type == "text")
                print(f"JARVIS: {text}\n")
                break

            # Claude asked for one or more tools. Run each and collect results.
            results = []
            for block in reply.content:
                if block.type != "tool_use":
                    continue
                print(f"  [running {block.name}: {json.dumps(block.input)}]")
                try:
                    output = run_tool(block.name, block.input)
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(output),
                    })
                except Exception as error:  # tell Claude what went wrong
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: {error}",
                        "is_error": True,
                    })
            # All results go back together in one message.
            messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    main()
