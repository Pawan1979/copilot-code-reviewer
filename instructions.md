# GitHub Copilot Instructions – CodeReview Agent

## Project Overview
This is **CodeReview Agent**, a Python chatbot that uses GitHub Copilot / OpenAI-compatible APIs
to review code, detect bugs, and suggest improvements. Submitted to **Microsoft Agents League 2026**.

## Coding Standards
- Python 3.10+, type hints on all public functions
- Follow PEP8; max line length 100
- Docstrings on every class and public method
- All new features must include unit tests in `tests/`

## Architecture
- `src/agent.py` – core agent logic (CodeReviewAgent class + CLI)
- `tests/test_agent.py` – pytest test suite
- `.env.example` – credential template (never commit real keys)

## When suggesting code:
- Prefer the `OpenAI` client with `base_url` for GitHub Copilot compatibility
- Always handle API errors gracefully with try/except
- Keep system prompts in a named constant (SYSTEM_PROMPT)
- New commands in the REPL should follow the existing `elif lower.startswith(...)` pattern

## Security rules (Copilot must follow):
- Never hardcode tokens or API keys
- Never log full user code to stdout in production mode
- Validate all file paths before reading
