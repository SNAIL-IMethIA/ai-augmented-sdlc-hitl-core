"""test_providers_examples.py: Tests for the example provider extensions.

All three providers lazy-import their SDK inside ``complete()``.  Tests
mock the SDK at the ``sys.modules`` level so no real packages are required.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from sdlc_core.providers.examples.anthropic_provider import AnthropicProvider
    from sdlc_core.providers.examples.gemini_provider import GeminiProvider
    from sdlc_core.providers.examples.litellm_provider import LiteLLMProvider
    from sdlc_core.providers.examples.openai_provider import OpenAIProvider

# ---------------------------------------------------------------------------
# AnthropicProvider
# ---------------------------------------------------------------------------


class TestAnthropicProvider:
    def _provider(self, **kwargs: Any) -> AnthropicProvider:
        from sdlc_core.providers.examples.anthropic_provider import AnthropicProvider

        return AnthropicProvider(**kwargs)

    def _mock_anthropic(self, text: str = "Claude response") -> MagicMock:
        mock = MagicMock()
        message = MagicMock()
        message.content = [MagicMock(text=text)]
        mock.Anthropic.return_value.messages.create.return_value = message
        return mock

    # -- happy path ----------------------------------------------------------

    def test_returns_response_text(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock = self._mock_anthropic("Hello from Claude")
        with patch.dict(sys.modules, {"anthropic": mock}):
            result = self._provider().complete("Say hi")
        assert result == "Hello from Claude"

    def test_default_max_tokens_is_4096(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock = self._mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock}):
            self._provider().complete("prompt")
        call_kwargs = mock.Anthropic.return_value.messages.create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 4096

    def test_max_tokens_kwarg_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock = self._mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock}):
            self._provider().complete("prompt", max_tokens=256)
        call_kwargs = mock.Anthropic.return_value.messages.create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 256

    def test_system_prompt_added_when_provided(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock = self._mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock}):
            self._provider().complete("prompt", system="Be concise.")
        call_kwargs = mock.Anthropic.return_value.messages.create.call_args.kwargs
        assert call_kwargs.get("system") == "Be concise."

    def test_no_system_key_when_system_is_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock = self._mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock}):
            self._provider().complete("prompt")
        call_kwargs = mock.Anthropic.return_value.messages.create.call_args.kwargs
        assert "system" not in call_kwargs

    def test_extra_kwargs_forwarded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock = self._mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock}):
            self._provider().complete("prompt", temperature=0.5)
        call_kwargs = mock.Anthropic.return_value.messages.create.call_args.kwargs
        assert call_kwargs.get("temperature") == 0.5

    def test_uses_custom_model_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock = self._mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock}):
            self._provider(model_id="claude-haiku-3-5").complete("prompt")
        call_kwargs = mock.Anthropic.return_value.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-3-5"

    def test_api_key_read_from_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_CLAUDE_KEY", "real-key")
        mock = self._mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock}):
            self._provider(api_key_env="MY_CLAUDE_KEY").complete("prompt")
        mock.Anthropic.assert_called_once_with(api_key="real-key")

    # -- error paths ---------------------------------------------------------

    def test_import_error_when_package_missing(self) -> None:
        with patch.dict(sys.modules, {"anthropic": None}):
            with pytest.raises(ImportError, match="anthropic"):
                self._provider().complete("prompt")

    def test_os_error_when_api_key_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        mock = self._mock_anthropic()
        with patch.dict(sys.modules, {"anthropic": mock}):
            with pytest.raises(OSError, match="ANTHROPIC_API_KEY"):
                self._provider().complete("prompt")


# ---------------------------------------------------------------------------
# OpenAIProvider
# ---------------------------------------------------------------------------


class TestOpenAIProvider:
    def _provider(self, **kwargs: Any) -> OpenAIProvider:
        from sdlc_core.providers.examples.openai_provider import OpenAIProvider

        return OpenAIProvider(**kwargs)

    def _mock_openai(self, content: str | None = "GPT response") -> MagicMock:
        mock = MagicMock()
        choice = MagicMock()
        choice.message.content = content
        mock.OpenAI.return_value.chat.completions.create.return_value = MagicMock(
            choices=[choice]
        )
        return mock

    # -- happy path ----------------------------------------------------------

    def test_returns_response_text(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        mock = self._mock_openai("Hello from GPT")
        with patch.dict(sys.modules, {"openai": mock}):
            result = self._provider().complete("Say hi")
        assert result == "Hello from GPT"

    def test_empty_content_returns_empty_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        mock = self._mock_openai(content=None)
        with patch.dict(sys.modules, {"openai": mock}):
            result = self._provider().complete("prompt")
        assert result == ""

    def test_system_message_prepended(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        mock = self._mock_openai()
        with patch.dict(sys.modules, {"openai": mock}):
            self._provider().complete("user msg", system="You are helpful.")
        messages = mock.OpenAI.return_value.chat.completions.create.call_args.kwargs[
            "messages"
        ]
        assert messages[0] == {"role": "system", "content": "You are helpful."}
        assert messages[1]["role"] == "user"

    def test_no_system_message_when_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        mock = self._mock_openai()
        with patch.dict(sys.modules, {"openai": mock}):
            self._provider().complete("user msg")
        messages = mock.OpenAI.return_value.chat.completions.create.call_args.kwargs[
            "messages"
        ]
        assert all(m["role"] != "system" for m in messages)

    def test_api_base_adds_base_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GROQ_KEY", "gk-test")
        mock = self._mock_openai()
        with patch.dict(sys.modules, {"openai": mock}):
            self._provider(
                api_key_env="GROQ_KEY",
                api_base="https://api.groq.com/openai/v1",
            ).complete("prompt")
        mock.OpenAI.assert_called_once_with(
            api_key="gk-test",
            base_url="https://api.groq.com/openai/v1",
        )

    def test_no_api_key_env_uses_no_key_sentinel(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock = self._mock_openai()
        with patch.dict(sys.modules, {"openai": mock}):
            self._provider(
                api_key_env="",
                api_base="http://localhost:8000/v1",
            ).complete("prompt")
        mock.OpenAI.assert_called_once_with(
            api_key="no-key",
            base_url="http://localhost:8000/v1",
        )

    def test_extra_kwargs_forwarded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        mock = self._mock_openai()
        with patch.dict(sys.modules, {"openai": mock}):
            self._provider().complete("prompt", temperature=0.3)
        call_kwargs = mock.OpenAI.return_value.chat.completions.create.call_args.kwargs
        assert call_kwargs.get("temperature") == 0.3

    # -- error paths ---------------------------------------------------------

    def test_import_error_when_package_missing(self) -> None:
        with patch.dict(sys.modules, {"openai": None}):
            with pytest.raises(ImportError, match="openai"):
                self._provider().complete("prompt")

    def test_os_error_when_api_key_env_set_but_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        mock = self._mock_openai()
        with patch.dict(sys.modules, {"openai": mock}):
            with pytest.raises(OSError, match="OPENAI_API_KEY"):
                self._provider().complete("prompt")


# ---------------------------------------------------------------------------
# GeminiProvider
# ---------------------------------------------------------------------------


class TestGeminiProvider:
    def _provider(self, **kwargs: Any) -> GeminiProvider:
        from sdlc_core.providers.examples.gemini_provider import GeminiProvider

        return GeminiProvider(**kwargs)

    def _mock_google(self, text: str | None = "Gemini response") -> tuple[MagicMock, MagicMock]:
        mock_genai = MagicMock()
        mock_types = MagicMock()
        # Wire types as an attribute so `from google.genai import types` resolves
        # to mock_types (Python's import does getattr on the module object).
        mock_genai.types = mock_types
        response = MagicMock()
        response.text = text
        mock_genai.Client.return_value.models.generate_content.return_value = response
        # Make types.GenerateContentConfig(...) return a sentinel we can check.
        mock_types.GenerateContentConfig.side_effect = lambda **kw: ("config", kw)
        return mock_genai, mock_types

    def _sys_patch(
        self, mock_genai: MagicMock, mock_types: MagicMock
    ) -> dict[str, MagicMock]:
        mock_google = MagicMock()
        mock_google.genai = mock_genai
        return {
            "google": mock_google,
            "google.genai": mock_genai,
            "google.genai.types": mock_types,
        }

    # -- happy path ----------------------------------------------------------

    def test_returns_response_text(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "gk-test")
        mock_genai, mock_types = self._mock_google("Hello from Gemini")
        with patch.dict(sys.modules, self._sys_patch(mock_genai, mock_types)):
            result = self._provider().complete("Say hi")
        assert result == "Hello from Gemini"

    def test_empty_text_returns_empty_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "gk-test")
        mock_genai, mock_types = self._mock_google(text=None)
        with patch.dict(sys.modules, self._sys_patch(mock_genai, mock_types)):
            result = self._provider().complete("prompt")
        assert result == ""

    def test_system_instruction_added_when_provided(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "gk-test")
        mock_genai, mock_types = self._mock_google()
        with patch.dict(sys.modules, self._sys_patch(mock_genai, mock_types)):
            self._provider().complete("prompt", system="You are an expert.")
        mock_types.GenerateContentConfig.assert_called_once()
        call_kwargs = mock_types.GenerateContentConfig.call_args.kwargs
        assert call_kwargs["system_instruction"] == "You are an expert."

    def test_no_config_when_no_system_and_no_kwargs(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "gk-test")
        mock_genai, mock_types = self._mock_google()
        # Use real (not side_effect) types so generate_content gets None config.
        mock_types.GenerateContentConfig.side_effect = None
        with patch.dict(sys.modules, self._sys_patch(mock_genai, mock_types)):
            self._provider().complete("prompt")
        call_kwargs = mock_genai.Client.return_value.models.generate_content.call_args.kwargs
        assert call_kwargs.get("config") is None

    def test_extra_kwargs_forwarded_to_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "gk-test")
        mock_genai, mock_types = self._mock_google()
        with patch.dict(sys.modules, self._sys_patch(mock_genai, mock_types)):
            self._provider().complete("prompt", temperature=0.8)
        call_kwargs = mock_types.GenerateContentConfig.call_args.kwargs
        assert call_kwargs.get("temperature") == 0.8

    def test_uses_custom_model_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "gk-test")
        mock_genai, mock_types = self._mock_google()
        with patch.dict(sys.modules, self._sys_patch(mock_genai, mock_types)):
            self._provider(model_id="gemini-2.5-pro").complete("prompt")
        call_kwargs = mock_genai.Client.return_value.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-2.5-pro"

    # -- error paths ---------------------------------------------------------

    def test_import_error_when_package_missing(self) -> None:
        with patch.dict(
            sys.modules, {"google": None, "google.genai": None, "google.genai.types": None}
        ):
            with pytest.raises(ImportError, match="google-genai"):
                self._provider().complete("prompt")

    def test_os_error_when_api_key_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        mock_genai, mock_types = self._mock_google()
        with patch.dict(sys.modules, self._sys_patch(mock_genai, mock_types)):
            with pytest.raises(OSError, match="GOOGLE_API_KEY"):
                self._provider().complete("prompt")

    def test_custom_api_key_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_GEMINI_KEY", "secret")
        mock_genai, mock_types = self._mock_google()
        with patch.dict(sys.modules, self._sys_patch(mock_genai, mock_types)):
            self._provider(api_key_env="MY_GEMINI_KEY").complete("prompt")
        mock_genai.Client.assert_called_once_with(api_key="secret")


# ---------------------------------------------------------------------------
# LiteLLMProvider
# ---------------------------------------------------------------------------


class TestLiteLLMProvider:
    def _provider(self, **kwargs: Any) -> LiteLLMProvider:
        from sdlc_core.providers.examples.litellm_provider import LiteLLMProvider

        return LiteLLMProvider(**kwargs)

    def _mock_litellm(self, content: str = "LiteLLM response") -> MagicMock:
        mock = MagicMock()
        response = {
            "choices": [{"message": {"content": content}}],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 8,
                "total_tokens": 20,
            },
        }
        mock.completion.return_value = response
        return mock

    def test_returns_response_text(self) -> None:
        mock = self._mock_litellm("hello")
        with patch.dict(sys.modules, {"litellm": mock}):
            result = self._provider().complete("Say hi")
        assert result == "hello"

    def test_includes_system_message_when_provided(self) -> None:
        mock = self._mock_litellm()
        with patch.dict(sys.modules, {"litellm": mock}):
            self._provider().complete("p", system="You are strict.")
        call_kwargs = mock.completion.call_args.kwargs
        assert call_kwargs["messages"][0]["role"] == "system"

    def test_uses_api_key_env_when_configured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "secret")
        mock = self._mock_litellm()
        with patch.dict(sys.modules, {"litellm": mock}):
            self._provider(
                model_id="openai/gpt-4o",
                api_key_env="OPENAI_API_KEY",
            ).complete("prompt")
        call_kwargs = mock.completion.call_args.kwargs
        assert call_kwargs["api_key"] == "secret"

    def test_uses_api_base_for_self_hosted_ollama(self) -> None:
        mock = self._mock_litellm()
        with patch.dict(sys.modules, {"litellm": mock}):
            self._provider(
                model_id="ollama/llama3",
                api_base="http://localhost:11434",
            ).complete("prompt")
        call_kwargs = mock.completion.call_args.kwargs
        assert call_kwargs["api_base"] == "http://localhost:11434"

    def test_captures_token_usage(self) -> None:
        mock = self._mock_litellm()
        with patch.dict(sys.modules, {"litellm": mock}):
            provider = self._provider()
            provider.complete("prompt")
        usage = provider.last_token_usage
        assert usage["prompt_tokens"] == 12
        assert usage["completion_tokens"] == 8
        assert usage["total_tokens"] == 20

    def test_raises_import_error_when_package_missing(self) -> None:
        with patch.dict(sys.modules, {"litellm": None}):
            with pytest.raises(ImportError, match="litellm"):
                self._provider().complete("prompt")

    def test_raises_when_api_key_env_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        mock = self._mock_litellm()
        with patch.dict(sys.modules, {"litellm": mock}):
            with pytest.raises(OSError, match="OPENAI_API_KEY"):
                self._provider(
                    model_id="openai/gpt-4o",
                    api_key_env="OPENAI_API_KEY",
                ).complete("prompt")
