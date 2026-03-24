"""ollama.py: OllamaProvider, the default provider for locally-hosted models.

Requires the ``ollama`` Python package (``pip install ollama``).
The Ollama daemon must be running locally (``ollama serve``).

Usage in models.toml
--------------------
    [models.llama3]
    provider  = "ollama"
    model_id  = "llama3"
    api_base  = "http://localhost:11434"   # optional (this is the default)

    [models.codellama]
    provider  = "ollama"
    model_id  = "codellama:13b"

    [models.mistral-local]
    provider  = "ollama"
    model_id  = "mistral"

Any model pulled via ``ollama pull <name>`` works.  No API key needed.
"""

from __future__ import annotations

from typing import Any


class OllamaProvider:
    """Provider for locally-hosted models served by Ollama.

    Args:
        model_id: The Ollama model name, e.g. ``"llama3"`` or
                  ``"codellama:13b"``.
        api_base: Base URL of the Ollama daemon.  Defaults to
                  ``http://localhost:11434``.

    """

    def __init__(
        self,
        model_id: str,
        api_base: str = "http://localhost:11434",
    ) -> None:
        """Initialise the provider. See class docstring for parameters."""
        self._model_id = model_id
        self._api_base = api_base.rstrip("/")

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Send *prompt* to the Ollama model and return the response text.

        Args:
            prompt: The user message to send.
            system: Optional system prompt. Passed as the ``system`` field in
                    the Ollama chat request.
            **kwargs: Forwarded to ``ollama.chat`` (e.g. ``temperature``,
                      ``num_predict``).  Unknown keys are ignored by Ollama.

        Returns:
            The model's response as a plain string.

        Raises:
            ImportError: If the ``ollama`` package is not installed.
            ollama.ResponseError: If the Ollama daemon returns an error.

        """
        try:
            import ollama
        except ImportError as exc:
            raise ImportError(
                "The 'ollama' package is required for OllamaProvider. "
                "Install it with: pip install ollama"
            ) from exc

        client = ollama.Client(host=self._api_base)

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Strip kwargs not accepted by ollama.chat to avoid TypeErrors
        # Ollama accepts options as a nested dict so forward them there
        options = {k: v for k, v in kwargs.items() if k not in ("stream",)}

        response = client.chat(
            model=self._model_id,
            messages=messages,
            options=options if options else None,
        )
        return str(response["message"]["content"])
