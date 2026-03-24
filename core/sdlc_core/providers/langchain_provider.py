"""langchain_provider.py: LangChainProvider bridge.

Bridges any LangChain BaseChatModel to the ModelProvider protocol.

Ollama (via ``ChatOllama``) is the default concrete model for this project,
but any ``BaseChatModel`` works without changes to the wrapper: ``ChatOpenAI``,
``ChatAnthropic``, ``ChatGoogleGenerativeAI``, etc.

Usage (Ollama default)
----------------------
    from langchain_ollama import ChatOllama
    from sdlc_core.providers.langchain_provider import LangChainProvider

    provider = LangChainProvider(ChatOllama(model="llama3"))

Usage (researcher extending to another model)
---------------------------------------------
    from langchain_openai import ChatOpenAI
    from sdlc_core.providers.langchain_provider import LangChainProvider

    provider = LangChainProvider(ChatOpenAI(model="gpt-4o"))

Then wrap with ``LoggedProvider`` as usual. Token counts are forwarded
automatically to the DB.

Token usage
-----------
After each call, token counts are available via ``provider.last_token_usage``
and are automatically read by ``LoggedProvider`` to populate the
``prompt_tokens`` and ``completion_tokens`` columns in ``interactions``.

Registration
------------
To expose this provider through the ``models.toml`` registry, register it
under a key in your template repo's entry point::

    from sdlc_core.providers import register_provider
    from langchain_ollama import ChatOllama
    from sdlc_core.providers.langchain_provider import LangChainProvider

    @register_provider("ollama-lc")
    class OllamaLangChain:
        def complete(self, prompt, system=None, **kwargs):
            return LangChainProvider(ChatOllama(model=kwargs.pop("model", "llama3"))).complete(
                prompt, system=system, **kwargs
            )

See ``sdlc_core/providers/examples/langchain_ollama_provider.py`` for a
complete, ready-to-register implementation.
"""

from __future__ import annotations

import importlib
from typing import Any


class LangChainProvider:
    """Wraps any LangChain ``BaseChatModel`` as a ``ModelProvider``.

    Pass an instantiated LangChain chat model (for example,
    ``ChatOllama(model="llama3:70b")``).

    The ``model_id`` is derived from the model's ``model`` or ``model_name``
    attribute; it falls back to the class name when neither is present.
    This string is stored in the ``interactions.model`` column.

    Token counts are read from ``AIMessage.usage_metadata`` (added in
    LangChain 0.3) and stored in ``interactions.prompt_tokens`` and
    ``interactions.completion_tokens`` when the model reports them.
    """

    def __init__(self, model: Any) -> None:  # noqa: ANN401
        """Initialise with an instantiated LangChain chat model."""
        self._model = model
        self._model_id: str = (
            getattr(model, "model", None)
            or getattr(model, "model_name", None)
            or type(model).__name__
        )
        self._last_token_usage: dict[str, int] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    @property
    def last_token_usage(self) -> dict[str, int]:
        """Token counts from the most recent call.

        Keys: ``prompt_tokens``, ``completion_tokens``, ``total_tokens``.
        All values are 0 when the model does not report usage metadata.

        Returns:
            A copy of the usage dict so callers cannot mutate internal state.

        """
        return dict(self._last_token_usage)

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Send *prompt* to the wrapped model and return the response text.

        Args:
            prompt: The user-turn text to send.
            system: Optional system / instruction prompt passed as a
                    ``SystemMessage``.
            **kwargs: Forwarded to the model's ``invoke`` call (e.g.
                      ``temperature``, ``max_tokens``).

        Returns:
            The model's response as a plain string.

        Raises:
            ImportError: If ``langchain-core`` is not installed.

        """
        try:
            messages_mod = importlib.import_module("langchain_core.messages")
            human_message_cls = messages_mod.HumanMessage
            system_message_cls = messages_mod.SystemMessage
        except (ImportError, AttributeError) as exc:
            raise ImportError(
                "langchain-core is required for LangChainProvider. "
                "Install it with: pip install langchain-core"
            ) from exc

        messages: list[Any] = []
        if system:
            messages.append(system_message_cls(content=system))
        messages.append(human_message_cls(content=prompt))

        response = self._model.invoke(messages, **kwargs)

        # Read usage_metadata (LangChain 0.3+). Default to zeros when omitted.
        usage = getattr(response, "usage_metadata", None) or {}
        self._last_token_usage = {
            "prompt_tokens": int(usage.get("input_tokens", 0)),
            "completion_tokens": int(usage.get("output_tokens", 0)),
            "total_tokens": int(usage.get("total_tokens", 0)),
        }

        return str(response.content)
