"""
CodeReview Agent - OpenAI-powered Code Review Assistant
Microsoft Agents League 2026 - Creative Apps Track
"""

import os
import sys
import json
import argparse
from typing import Optional
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
SYSTEM_PROMPT = """
You are **CodeReview Agent**, an expert AI assistant specialised in reviewing code.

Your capabilities:
- Detect bugs, logic errors, and security vulnerabilities
- Suggest performance optimisations and best practices
- Enforce coding standards (PEP8, SOLID, DRY, etc.)
- Explain complex code in plain English
- Generate unit-test stubs for reviewed functions
- Provide refactored alternatives where relevant

Response format:
1. 📋 **Summary** – one-line verdict (Pass / Needs Work / Critical Issues)
2. 🐛 **Issues Found** – numbered list with severity [LOW / MEDIUM / HIGH / CRITICAL]
3. 💡 **Suggestions** – actionable improvements
4. ✅ **Refactored Snippet** – improved code (if applicable)
5. 🧪 **Test Stubs** – basic unit tests (if applicable)

Always be concise, constructive, and beginner-friendly.
"""

WELCOME_BANNER = """
╔══════════════════════════════════════════════════════════╗
║        🤖  CodeReview Agent  |  Powered by Github Copilot       ║
║          Microsoft Agents League 2026 Submission           ║
╚══════════════════════════════════════════════════════════╝
Commands:
  review <code>   – paste code inline
  file <path>     – review a local file
  explain         – explain the last reviewed code
  clear           – start a new session
  exit / quit     – exit the agent

Type your message or a command to get started.
"""


# ─────────────────────────────────────────────
# Client Factory
# ─────────────────────────────────────────────
def build_client():
    """
    Build the OpenAI client.
    Priority:
      1. OpenAI (via OpenAI API key)

    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        # OpenAI chat completions endpoint
        client = OpenAI(
            api_key=openai_api_key,
        )
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        print(f"✅ Connected via OpenAI (model: {model})\n")
        return client, model

 

    print("❌ No API credentials found.")
    print("   Set OPENAI_API_KEY environment variable.")
    sys.exit(1)


# ─────────────────────────────────────────────
# CodeReview Agent
# ─────────────────────────────────────────────
class CodeReviewAgent:
    def __init__(self):
        self.client, self.model = build_client()
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.last_code: Optional[str] = None

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=0.3,
            max_tokens=2048,
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def review_code(self, code: str, language: str = "auto-detect") -> str:
        self.last_code = code
        prompt = f"Please review the following {language} code:\n\n```\n{code}\n```"
        return self.chat(prompt)

    def review_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            ext = os.path.splitext(file_path)[1].lstrip(".")
            lang_map = {"py": "Python", "js": "JavaScript", "ts": "TypeScript",
                        "java": "Java", "cs": "C#", "go": "Go", "rs": "Rust",
                        "cpp": "C++", "c": "C", "rb": "Ruby", "php": "PHP"}
            language = lang_map.get(ext, ext or "unknown")
            print(f"📂 Reviewing file: {file_path} ({language})\n")
            return self.review_code(code, language)
        except FileNotFoundError:
            return f"❌ File not found: {file_path}"
        except Exception as e:
            return f"❌ Error reading file: {e}"

    def explain_last(self) -> str:
        if not self.last_code:
            return "No code has been reviewed yet. Please review some code first."
        return self.chat("Can you explain what the last reviewed code does in simple terms?")

    def clear_session(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.last_code = None
        print("🔄 Session cleared. Starting fresh!\n")

    # ── Interactive REPL ──────────────────────
    def run_interactive(self):
        print(WELCOME_BANNER)
        while True:
            try:
                user_input = input("You > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            lower = user_input.lower()

            if lower in ("exit", "quit"):
                print("👋 Goodbye!")
                break

            elif lower == "clear":
                self.clear_session()

            elif lower == "explain":
                print("\nAgent >\n" + self.explain_last() + "\n")

            elif lower.startswith("file "):
                path = user_input[5:].strip()
                print("\nAgent >\n" + self.review_file(path) + "\n")

            elif lower.startswith("review "):
                code = user_input[7:].strip()
                print("\nAgent >\n" + self.review_code(code) + "\n")

            else:
                # Free-form chat
                print("\nAgent >\n" + self.chat(user_input) + "\n")

    # ── Single-shot review (CI / scripting) ──
    def run_single(self, file_path: Optional[str] = None, code: Optional[str] = None):
        if file_path:
            result = self.review_file(file_path)
        elif code:
            result = self.review_code(code)
        else:
            print("❌ Provide --file or --code for single-shot mode.")
            sys.exit(1)
        print(result)


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="CodeReview Agent – OpenAI-powered code reviewer"
    )
    parser.add_argument("--file", "-f", help="Path to a file to review (single-shot)")
    parser.add_argument("--code", "-c", help="Code snippet to review (single-shot)")
    parser.add_argument("--output", "-o", help="Save review result to a JSON file")
    args = parser.parse_args()

    agent = CodeReviewAgent()

    if args.file or args.code:
        agent.run_single(file_path=args.file, code=args.code)
        if args.output:
            data = {"file": args.file, "code": args.code, "history": agent.history[1:]}
            with open(args.output, "w") as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Review saved to {args.output}")
    else:
        agent.run_interactive()


if __name__ == "__main__":
    main()
