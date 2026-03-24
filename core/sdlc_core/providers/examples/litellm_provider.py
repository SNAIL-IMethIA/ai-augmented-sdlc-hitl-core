"""litellm_provider.py: Provider extension for LiteLLM unified model routing.

Requires:  pip install litellm

This provider keeps the ``ModelProvider`` contract while delegating completion
calls to LiteLLM's single ``completion`` API. It is useful for research runs
where model backends must be swapped without changing orchestration code.

Usage in models.toml
--------------------
    [models.llama3-litellm]
    provider    = "litellm"
    model_id    = "ollama/llama3"
    api_key_env = ""
    api_base    = "http://localhost:11434"

    [models.gpt4o-litellm]
    provider    = "litellm"
    model_id    = "openai/gpt-4o"
    api_key_env = "OPENAI_API_KEY"

Registration
------------
    from sdlc_core.providers import register_provider
    from sdlc_core.providers.examples.litellm_provider import LiteLLMProvider

    register_provider("litellm")(LiteLLMProvider)
"""

from __future__ import annotations

import importlib
import os
from typing import Any


class LiteLLMProvider:
    """Provider backed by LiteLLM's ``completion`` API.

    Args:
        model_id:    LiteLLM model string, e.g. ``"ollama/llama3"`` or
                     ``"openai/gpt-4o"``.
        api_key_env: Environment variable name for API key. Leave empty for
                     local backends that do not require credentials.
        api_base:    Optional provider base URL for compatible endpoints.

    """

    def __init__(
        self,
        model_id: str = "ollama/llama3",
        api_key_env: str = "",
        api_base: str = "",
    ) -> None:
        """Initialise the provider. See class docstring for parameters."""
        self._model_id = model_id
        self._api_key_env = api_key_env
        self._api_base = api_base
        self._last_token_usage: dict[str, int] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    @property
    def last_token_usage(self) -> dict[str, int]:
        """Token usage from the most recent call.

        Returns:
            A defensive copy of the token usage dict.

        """
        return dict(self._last_token_usage)

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Send *prompt* through LiteLLM and return response text.

        Args:
            prompt: The user message to send.
            system: Optional system prompt prepended as a system message.
            **kwargs: Forwarded to ``litellm.completion``.

        Returns:
            The model response text.

        Raises:
            ImportError: If ``litellm`` is not installed.
            OSError: If ``api_key_env`` is configured but not set.

        """
        try:
            litellm_mod = importlib.import_module("litellm")
            completion_fn = litellm_mod.completion
        except (ImportError, AttributeError) as exc:
            raise ImportError(
                "The 'litellm' package is required for LiteLLMProvider. "
                "Install it with: pip install litellm"
            ) from exc

        api_key = ""
        if self._api_key_env:
            api_key = os.environ.get(self._api_key_env, "")
            if not api_key:
                raise OSError(
                    f"Environment variable {self._api_key_env!r} is not set. "
                    "Add it to your .env file."
                )

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        call_kwargs: dict[str, Any] = {
            "model": self._model_id,
            "messages": messages,
        }
        if api_key:
            call_kwargs["api_key"] = api_key
        if self._api_base:
            call_kwargs["api_base"] = self._api_base
        call_kwargs.update(kwargs)

        response = completion_fn(**call_kwargs)

        usage = getattr(response, "usage", None)
        if usage is None and isinstance(response, dict):
            usage = response.get("usage")

        if isinstance(usage, dict):
            self._last_token_usage = {
                "prompt_tokens": int(usage.get("prompt_tokens", 0)),
                "completion_tokens": int(usage.get("completion_tokens", 0)),
                "total_tokens": int(usage.get("total_tokens", 0)),
            }
        else:
            self._last_token_usage = {
                "prompt_tokens": int(getattr(usage, "prompt_tokens", 0)),
                "completion_tokens": int(getattr(usage, "completion_tokens", 0)),
                "total_tokens": int(getattr(usage, "total_tokens", 0)),
            }

        content = ""
        if isinstance(response, dict):
            choices = response.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = str(message.get("content", ""))
        else:
            choices = getattr(response, "choices", [])
            if choices:
                message = getattr(choices[0], "message", None)
                content = str(getattr(message, "content", ""))

        return content
