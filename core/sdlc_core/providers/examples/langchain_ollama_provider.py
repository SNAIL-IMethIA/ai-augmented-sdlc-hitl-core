"""langchain_ollama_provider.py: Ready-to-register LangChain + Ollama provider.

Wraps ``ChatOllama`` from ``langchain-ollama`` via :class:`LangChainProvider`.
This is the recommended default provider for researchers using local models
through Ollama.  Because ``LangChainProvider`` accepts any ``BaseChatModel``,
switching to a different backend later is a one-line change.

Requirements
------------
    pip install langchain-ollama   # already in pyproject.toml pinned deps

Ollama daemon must be running::

    ollama serve
    ollama pull llama3       # or whichever model_id you configure

Usage in models.toml
--------------------
    [models.llama3-lc]
    provider    = "ollama-lc"
    model_id    = "llama3"
    api_base    = ""           # defaults to http://localhost:11434

    [models.llama3-70b-lc]
    provider    = "ollama-lc"
    model_id    = "llama3:70b"

Registration (add to your template repo's entry point)
-------------------------------------------------------
    from sdlc_core.providers import register_provider
    from sdlc_core.providers.examples.langchain_ollama_provider import (
        LangChainOllamaProvider,
    )

    register_provider("ollama-lc")(LangChainOllamaProvider)

Swapping to another provider later
-----------------------------------
Replace the inner model without touching any logging or DB code::

    # from langchain_openai import ChatOpenAI
    from sdlc_core.providers.langchain_provider import LangChainProvider

    provider = LangChainProvider(ChatOpenAI(model="gpt-4o"))
"""

from __future__ import annotations

import importlib
from typing import Any

from sdlc_core.providers.langchain_provider import LangChainProvider


class LangChainOllamaProvider:
    """``ModelProvider`` backed by ``ChatOllama`` via ``LangChainProvider``.

    Args:
        model_id: The Ollama model name, e.g. ``"llama3"`` or
                  ``"llama3:70b"``.
        api_base: Base URL of the Ollama daemon.  Defaults to
                  ``http://localhost:11434``.

    This class satisfies both the ``ModelProvider`` protocol (for use with
    ``LoggedProvider``) and the ``last_token_usage`` convention (for automatic
    token tracking in the interactions table).

    Example::

        from sdlc_core.providers.examples.langchain_ollama_provider import (
            LangChainOllamaProvider,
        )
        from sdlc_core.providers import LoggedProvider
        from sdlc_core.session import Session

        session = Session(run_id="run-001", approach=1, active_phase=3)
        provider = LoggedProvider(
            LangChainOllamaProvider("llama3"),
            session=session,
        )
        response = provider.complete(
            prompt="...",
            agent_role="requirements_analyst",
            artifact_id="REQ-01",
        )

    """

    def __init__(
        self,
        model_id: str = "llama3",
        api_base: str = "http://localhost:11434",
    ) -> None:
        """Initialise the provider. See class docstring for parameters."""
        self._model_id = model_id
        self._api_base = api_base
        self._inner: LangChainProvider | None = None

    def _get_inner(self) -> LangChainProvider:
        if self._inner is None:
            try:
                ollama_mod = importlib.import_module("langchain_ollama")
                chat_ollama_cls = ollama_mod.ChatOllama
            except (ImportError, AttributeError) as exc:
                raise ImportError(
                    "langchain-ollama is required for LangChainOllamaProvider. "
                    "Install it with: pip install langchain-ollama"
                ) from exc
            model = chat_ollama_cls(
                model=self._model_id,
                base_url=self._api_base,
            )
            self._inner = LangChainProvider(model)
        return self._inner

    @property
    def last_token_usage(self) -> dict[str, int]:
        """Token counts from the most recent call, forwarded from the inner provider."""
        if self._inner is None:
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        return self._inner.last_token_usage

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Send *prompt* to the Ollama model via LangChain and return the response.

        Args:
            prompt: The user-turn text to send.
            system: Optional system prompt.
            **kwargs: Forwarded to ``ChatOllama.invoke``.

        Returns:
            The model's response as a plain string.

        """
        return self._get_inner().complete(prompt, system=system, **kwargs)
