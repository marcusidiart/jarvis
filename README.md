# JARVIS

A voice AI assistant that finds local businesses with no website, builds them one, and helps you pitch it.

## Milestone 1: the brain (typing only)

JARVIS can chat and search Google Maps for businesses without a website.

### Files

- `jarvis.py` is the brain. It sends your message to Claude. If Claude asks to use a tool, it runs the tool, sends back the result, and repeats until Claude has a final answer. That loop is the "agent".
- `tools.py` holds the tools. Each one is a normal Python function plus a short description that tells Claude what it's for.
- `.env` holds your secret keys (copy `.env.example`). It is git-ignored so keys never get uploaded.

### Setup (one time)

1. Install Python 3.11 or newer from python.org.
2. Get your keys:
   - **Anthropic:** console.anthropic.com → API Keys → Create key. Add a few dollars of credit.
   - **Google:** console.cloud.google.com → create a project → "APIs & Services" → enable **Places API (New)** → Credentials → Create API key.
3. In this folder, run:

   ```
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env             # Windows: copy .env.example .env
   ```

4. Open `.env` and paste in both keys.

### Run it

```
python jarvis.py
```

Try: `Find a restaurant in Miami that doesn't have a website.`

You'll see `[running search_places: ...]` when JARVIS uses Google Maps, then its answer.

## Coming next

- Milestone 2: `build_site` and `publish_site` tools, so JARVIS writes and publishes the website.
- Milestone 3: the voice and glowing-orb screen.
- Milestone 4: emailing the owner, follow-ups and payment links, always asking you before sending.
