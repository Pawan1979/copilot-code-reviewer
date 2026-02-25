# 🤖 CodeReview Agent
### Microsoft Agents League 2026 – Creative Apps Track (GitHub Copilot Chat)

[![CI](https://github.com/pawan1979/codereview-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/codereview-agent/actions)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Powered by GitHub Copilot](https://img.shields.io/badge/Powered%20by-GitHub%20Copilot-6f42c1)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## 📌 What is CodeReview Agent?

**CodeReview Agent** is an AI-powered chatbot assistant that reviews your code in real time using **GitHub Copilot Chat**. It detects bugs, security vulnerabilities, and code smells — and suggests clean, refactored alternatives along with ready-to-use unit test stubs.

Designed for **developers who want instant, actionable code feedback** without waiting for a PR review.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🐛 Bug Detection | Identifies logic errors, null pointer risks, edge cases |
| 🔒 Security Scanning | Flags SQL injection, hardcoded secrets, unsafe I/O |
| 💡 Refactoring Tips | Suggests cleaner, more idiomatic rewrites |
| 🧪 Test Stubs | Generates pytest/unittest stubs automatically |
| 📂 File Review | Review any local file directly from the CLI |
| 💬 Chat Mode | Conversational REPL — ask follow-up questions |
| 🔁 CI Integration | Single-shot mode for use in GitHub Actions pipelines |

---

## 🏗️ Architecture

```
copilot-code-reviewer/
├── src/
│   └── agent.py              # Core agent: CodeReviewAgent class + CLI
├── tests/
│   └── test_agent.py         # pytest test suite (10+ tests)
├── .github/
│   ├── copilot-instructions/ # GitHub Copilot repo instructions
│   └── workflows/ci.yml      # CI pipeline (Python 3.10/3.11/3.12)
├── .env.example              # Credential template
├── requirements.txt
└── README.md
```

### How it uses GitHub Copilot

The agent connects to **GitHub's Models Inference endpoint** (`https://models.inference.ai.azure.com`) using your `GITHUB_TOKEN`. This is the production GitHub Copilot Chat API — the same one powering Copilot in VS Code and the CLI.

```
User Input
    │
    ▼
CodeReviewAgent (Python)
    │  Builds structured prompt with SYSTEM_PROMPT + conversation history
    ▼
GitHub Copilot Chat API  ──►  gpt-4o (or gpt-4o-mini)
    │
    ▼
Structured Review Output
  📋 Summary  |  🐛 Issues  |  💡 Suggestions  |  ✅ Refactor  |  🧪 Tests
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/pawan1979/codereview-agent.git
cd codereview-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your GitHub token
```bash
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN
```

> **Getting a GitHub Token**: Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token. No special scopes needed for Copilot Models access.

### 4. Run the agent
```bash
# Interactive chat mode
python src/agent.py

# Review a specific file
python src/agent.py --file path/to/your/code.py

# Review an inline snippet
python src/agent.py --code "def divide(a,b): return a/b"

# Save review to JSON (great for CI pipelines)
python src/agent.py --file app.py --output review.json
```

---

## 💬 Interactive Mode Demo

```
╔══════════════════════════════════════════════════════════╗
║        🤖  CodeReview Agent  |  Powered by GitHub Copilot       ║
║          Microsoft Agents League 2026 Submission           ║
╚══════════════════════════════════════════════════════════╝

You > review def get_user(id): return db.execute(f"SELECT * FROM users WHERE id={id}")

Agent >
📋 Summary: Critical Issues

🐛 Issues Found:
1. [CRITICAL] SQL Injection – f-string interpolation in SQL query allows arbitrary SQL execution
2. [MEDIUM]   No error handling – db.execute may throw if connection is lost

💡 Suggestions:
- Use parameterised queries: db.execute("SELECT * FROM users WHERE id=?", (id,))
- Wrap in try/except and return None on failure

✅ Refactored Snippet:
def get_user(user_id: int):
    try:
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    except Exception as e:
        logging.error(f"DB error: {e}")
        return None

🧪 Test Stubs:
def test_get_user_returns_none_on_invalid_id():
    assert get_user(-1) is None

You > explain

Agent > This function fetches a user record from the database by ID. The original
version is dangerous because it builds the SQL query by directly embedding
user input into the string — a classic SQL injection vulnerability...
```

---

## 🧪 Running Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=src
```

---

## 🔧 CI / CD Integration

Use CodeReview Agent in your GitHub Actions pipeline:

```yaml
- name: AI Code Review
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python src/agent.py --file src/my_module.py --output review.json
    cat review.json
```

---

## 🌐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GITHUB_TOKEN` | ✅ Recommended | GitHub PAT for Copilot Models API |
| `COPILOT_MODEL` | Optional | Model to use (default: `gpt-4o`) |

---

## 📋 Submission Details

| Field | Value |
|---|---|
| **Challenge** | Microsoft Agents League 2026 |
| **Track** | Creative Apps – GitHub Copilot (Chat) |
| **Dates** | Feb 16 – Feb 27, 2026 |
| **Tech Stack** | Python 3.10+, OpenAI SDK, GitHub Copilot Models API |
| **License** | MIT |

---

## 📄 License

MIT © 2026 – Built for Microsoft Agents League
