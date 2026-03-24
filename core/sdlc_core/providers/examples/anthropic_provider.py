"""anthropic_provider.py: Provider extension for Anthropic Claude models.

Requires:  pip install anthropic
API key:   set the ANTHROPIC_API_KEY environment variable.

Usage in models.toml
--------------------
    [models.claude-sonnet]
    provider    = "anthropic"
    model_id    = "claude-sonnet-4-5"
    api_key_env = "ANTHROPIC_API_KEY"

    [models.claude-haiku]
    provider    = "anthropic"
    model_id    = "claude-haiku-3-5"
    api_key_env = "ANTHROPIC_API_KEY"

Registration (add to your setup script or template entry point)
---------------------------------------------------------------
    from sdlc_core.providers import register_provider
    from sdlc_core.providers.examples.anthropic_provider import AnthropicProvider

    register_provider("anthropic")(AnthropicProvider)

    # Or decorate the class when you copy it into your own module:
    # @register_provider("anthropic")
    # class AnthropicProvider: ...

Supported models (as of early 2026)
------------------------------------
    claude-opus-4-5
    claude-sonnet-4-5
    claude-haiku-3-5
    (see https://docs.anthropic.com/en/docs/about-claude/models for the latest list)
"""

from __future__ import annotations

import os
from typing import Any


class AnthropicProvider:
    """Provider for Anthropic Claude models.

    Args:
        model_id:    The Anthropic model identifier, e.g. ``"claude-sonnet-4-5"``.
        api_key_env: Name of the environment variable holding the API key.
                     Defaults to ``"ANTHROPIC_API_KEY"``.

    """

    def __init__(
        self,
        model_id: str = "claude-sonnet-4-5",
        api_key_env: str = "ANTHROPIC_API_KEY",
    ) -> None:
        """Initialise the provider. See class docstring for parameters."""
        self._model_id = model_id
        self._api_key_env = api_key_env

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Send *prompt* to the Claude model and return the response text.

        Args:
            prompt: The user message to send.
            system: Optional system prompt passed as the ``system`` field.
            **kwargs: Forwarded to the Anthropic ``messages.create`` call.
                      Useful keys: ``max_tokens`` (default 4096),
                      ``temperature``.

        Returns:
            The model's response as a plain string.

        Raises:
            ImportError: If the ``anthropic`` package is not installed.
            anthropic.APIError: On API-level errors.
            EnvironmentError: If the API key env var is not set.

        """
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "The 'anthropic' package is required for AnthropicProvider. "
                "Install it with: pip install anthropic"
            ) from exc

        api_key = os.environ.get(self._api_key_env, "")
        if not api_key:
            raise OSError(
                f"Environment variable {self._api_key_env!r} is not set. "
                "Add it to your .env file."
            )

        client = anthropic.Anthropic(api_key=api_key)

        create_kwargs: dict[str, Any] = {
            "model": self._model_id,
            "max_tokens": kwargs.pop("max_tokens", 4096),
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            create_kwargs["system"] = system
        create_kwargs.update(kwargs)

        message = client.messages.create(**create_kwargs)
        return str(message.content[0].text)
