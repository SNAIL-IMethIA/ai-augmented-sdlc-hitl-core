"""gemini_provider.py: Provider extension for Google Gemini models.

Requires:  pip install google-genai
API key:   set the GOOGLE_API_KEY environment variable.

Usage in models.toml
--------------------
    [models.gemini-flash]
    provider    = "gemini"
    model_id    = "gemini-2.0-flash"
    api_key_env = "GOOGLE_API_KEY"

    [models.gemini-pro]
    provider    = "gemini"
    model_id    = "gemini-2.5-pro"
    api_key_env = "GOOGLE_API_KEY"

Registration
------------
    from sdlc_core.providers import register_provider
    from sdlc_core.providers.examples.gemini_provider import GeminiProvider

    register_provider("gemini")(GeminiProvider)

    # Or decorate when you copy the class into your own module:
    # @register_provider("gemini")
    # class GeminiProvider: ...

Note on the system prompt
--------------------------
Gemini supports a dedicated ``system_instruction`` field.  This provider
passes the ``system`` argument there when provided.

Supported models (as of early 2026)
------------------------------------
    gemini-2.5-pro, gemini-2.0-flash, gemini-2.0-flash-lite
    (see https://ai.google.dev/gemini-api/docs/models for the latest list)
"""

from __future__ import annotations

import os
from typing import Any


class GeminiProvider:
    """Provider for Google Gemini models via the google-genai SDK.

    Args:
        model_id:    The Gemini model identifier, e.g. ``"gemini-2.0-flash"``.
        api_key_env: Name of the environment variable holding the API key.
                     Defaults to ``"GOOGLE_API_KEY"``.

    """

    def __init__(
        self,
        model_id: str = "gemini-2.0-flash",
        api_key_env: str = "GOOGLE_API_KEY",
    ) -> None:
        """Initialise the provider. See class docstring for parameters."""
        self._model_id = model_id
        self._api_key_env = api_key_env

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Send *prompt* to the Gemini model and return the response text.

        Args:
            prompt: The user message to send.
            system: Optional system instruction passed via
                    ``system_instruction``.
            **kwargs: Forwarded to ``client.models.generate_content``.
                      Useful keys: ``temperature``, ``max_output_tokens``.

        Returns:
            The model's response as a plain string.

        Raises:
            ImportError: If the ``google-genai`` package is not installed.
            google.genai.errors.APIError: On API-level errors.
            EnvironmentError: If the API key env var is not set.

        """
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ImportError(
                "The 'google-genai' package is required for GeminiProvider. "
                "Install it with: pip install google-genai"
            ) from exc

        api_key = os.environ.get(self._api_key_env, "")
        if not api_key:
            raise OSError(
                f"Environment variable {self._api_key_env!r} is not set. "
                "Add it to your .env file."
            )

        client = genai.Client(api_key=api_key)

        config_kwargs: dict[str, Any] = {}
        if system:
            config_kwargs["system_instruction"] = system
        config_kwargs.update(kwargs)

        generate_config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

        response = client.models.generate_content(
            model=self._model_id,
            contents=prompt,
            config=generate_config,
        )
        return response.text or ""
