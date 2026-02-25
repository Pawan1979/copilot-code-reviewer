"""
Unit tests for CodeReview Agent
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_agent():
    """Return a CodeReviewAgent with a mocked OpenAI client."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}):
        with patch("src.agent.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client

            # Mock chat completion response
            mock_response = MagicMock()
            mock_response.choices[0].message.content = (
                "📋 **Summary**: Needs Work\n"
                "🐛 **Issues Found**: 1. [HIGH] Missing input validation\n"
                "💡 **Suggestions**: Add try/except around file I/O"
            )
            mock_client.chat.completions.create.return_value = mock_response

            from src.agent import CodeReviewAgent
            agent = CodeReviewAgent()
            agent.client = mock_client
            return agent


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCodeReviewAgent:

    def test_review_code_returns_string(self, mock_agent):
        result = mock_agent.review_code("def foo(): pass")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_review_code_stores_last_code(self, mock_agent):
        code = "x = 1/0"
        mock_agent.review_code(code)
        assert mock_agent.last_code == code

    def test_history_updated_after_review(self, mock_agent):
        initial_len = len(mock_agent.history)
        mock_agent.review_code("print('hello')")
        assert len(mock_agent.history) == initial_len + 2  # user + assistant

    def test_explain_last_no_code(self, mock_agent):
        result = mock_agent.explain_last()
        assert "No code" in result

    def test_explain_last_with_code(self, mock_agent):
        mock_agent.last_code = "def add(a,b): return a+b"
        result = mock_agent.explain_last()
        assert isinstance(result, str)

    def test_clear_session_resets_history(self, mock_agent):
        mock_agent.review_code("x = 1")
        mock_agent.clear_session()
        assert len(mock_agent.history) == 1  # only system prompt
        assert mock_agent.last_code is None

    def test_review_file_not_found(self, mock_agent):
        result = mock_agent.review_file("/nonexistent/path/file.py")
        assert "not found" in result.lower() or "❌" in result

    def test_review_file_success(self, mock_agent, tmp_path):
        sample = tmp_path / "sample.py"
        sample.write_text("def greet(name):\n    print(f'Hello {name}')\n")
        result = mock_agent.review_file(str(sample))
        assert isinstance(result, str)

    def test_chat_appends_to_history(self, mock_agent):
        before = len(mock_agent.history)
        mock_agent.chat("What is a race condition?")
        assert len(mock_agent.history) == before + 2

    def test_review_code_with_language(self, mock_agent):
        result = mock_agent.review_code("console.log('hi')", language="JavaScript")
        assert isinstance(result, str)


class TestClientFactory:

    def test_exits_without_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove any credential env vars
            for key in ["GITHUB_TOKEN", "AZURE_OPENAI_ENDPOINT", "OPENAI_API_KEY"]:
                os.environ.pop(key, None)
            with pytest.raises(SystemExit):
                from src.agent import build_client
                build_client()
