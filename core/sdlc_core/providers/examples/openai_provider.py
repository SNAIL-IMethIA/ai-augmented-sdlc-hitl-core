"""openai_provider.py: Provider extension for OpenAI and OpenAI-compatible APIs.

Requires:  pip install openai
API key:   set the OPENAI_API_KEY environment variable (or whichever name
           your compatible endpoint uses).

This single provider covers a wide range of endpoints because many services
expose an OpenAI-compatible REST API:
  - OpenAI (api.openai.com)
  - Azure OpenAI
  - Together.ai
  - Groq
  - vLLM self-hosted
  - LM Studio local server
  - Any other OpenAI-compatible endpoint

Usage in models.toml
--------------------
    # Standard OpenAI
    [models.gpt-4o]
    provider    = "openai"
    model_id    = "gpt-4o"
    api_key_env = "OPENAI_API_KEY"

    # Groq (OpenAI-compatible, different base URL)
    [models.llama3-groq]
    provider    = "openai"
    model_id    = "llama-3.1-70b-versatile"
    api_key_env = "GROQ_API_KEY"
    api_base    = "https://api.groq.com/openai/v1"

    # Local vLLM server (no key needed)
    [models.mistral-vllm]
    provider    = "openai"
    model_id    = "mistralai/Mistral-7B-Instruct-v0.3"
    api_key_env = ""
    api_base    = "http://localhost:8000/v1"

Registration
------------
    from sdlc_core.providers import register_provider
    from sdlc_core.providers.examples.openai_provider import OpenAIProvider

    register_provider("openai")(OpenAIProvider)

    # Or decorate when you copy the class into your own module:
    # @register_provider("openai")
    # class OpenAIProvider: ...

Supported models (as of early 2026)
------------------------------------
    gpt-4o, gpt-4o-mini, o1, o3-mini
    (see https://platform.openai.com/docs/models for the latest list)
"""

from __future__ import annotations

import os
from typing import Any


class OpenAIProvider:
    """Provider for OpenAI and OpenAI-compatible API endpoints.

    Args:
        model_id:    The model identifier, e.g. ``"gpt-4o"``.
        api_key_env: Name of the environment variable holding the API key.
                     Pass an empty string for local endpoints that need no key.
        api_base:    Base URL of the API.  Defaults to the official OpenAI URL.
                     Override for Azure, Groq, vLLM, LM Studio, etc.

    """

    def __init__(
        self,
        model_id: str = "gpt-4o",
        api_key_env: str = "OPENAI_API_KEY",
        api_base: str = "",
    ) -> None:
        """Initialise the provider. See class docstring for parameters."""
        self._model_id = model_id
        self._api_key_env = api_key_env
        self._api_base = api_base

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Send *prompt* to the model and return the response text.

        Args:
            prompt: The user message to send.
            system: Optional system prompt prepended as a ``"system"`` message.
            **kwargs: Forwarded to ``client.chat.completions.create``.
                      Useful keys: ``temperature``, ``max_tokens``.

        Returns:
            The model's response as a plain string.

        Raises:
            ImportError: If the ``openai`` package is not installed.
            openai.OpenAIError: On API-level errors.
            EnvironmentError: If the API key env var is set but empty.

        """
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required for OpenAIProvider. "
                "Install it with: pip install openai"
            ) from exc

        api_key = os.environ.get(self._api_key_env, "") if self._api_key_env else "no-key"
        if self._api_key_env and not api_key:
            raise OSError(
                f"Environment variable {self._api_key_env!r} is not set. "
                "Add it to your .env file."
            )

        client_kwargs: dict[str, Any] = {"api_key": api_key}
        if self._api_base:
            client_kwargs["base_url"] = self._api_base

        client = OpenAI(**client_kwargs)

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self._model_id,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content or ""
