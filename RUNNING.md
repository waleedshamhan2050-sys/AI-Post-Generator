# AI-Post-Generator — Open-Model Mode (Hacktoberfest 2026, Week 2: Side Hustle)

This repo runs on a **local open-weight model** (Gemma 3 by default)
through **Ollama** — no hosted API, no per-post cost, and your content
never leaves your machine.

The original OpenAI mode is still there (`--provider openai`).

## What changed vs. the original `main.py`

- New `--provider` flag: `ollama` (default) or `openai`.
- New `--model` flag (default: `OLLAMA_MODEL` from `.env`, or `gemma3`).
- New `get_client()` — for Ollama it points the same OpenAI-compatible
  client at the local Ollama server (`http://localhost:11434/v1`).
- The prompt, templates, and saving logic are unchanged.
- `requirements.txt` is unchanged (no new dependencies).

## Status

This mode is already merged into the repo (`main.py` on the default
branch). No manual step needed.

## How to run it

```bash
# 1. Install Ollama from https://ollama.com, then pull the model:
ollama pull gemma3

# 2. Install dependencies:
pip install -r requirements.txt

# 3. Run with the local open-weight model (default):
python main.py

# Or explicitly:
python main.py --provider ollama --model gemma3

# Old behaviour still works:
python main.py --provider openai
```

## Notes for the Hacktoberfest submission

- The DEV submission article is published (Hacktoberfest 2026,
  Week 2: Side Hustle; enters the **Best Use of Gemma** featured
  category, because the default model is Gemma 3, an open-weight model).
- Verified: the tool was run with Ollama locally and generated a real
  post — see `examples/gemma3_local_sample.txt`.
