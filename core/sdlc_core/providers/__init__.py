"""providers: Model provider abstractions for the AI-Augmented SDLC experiment.

Public surface
--------------
- ``ModelProvider``: Protocol every provider must satisfy.
- ``ManualProvider``: HITL provider that routes through the researcher's terminal (Approach 1).
- ``OllamaProvider``: Default provider for locally-hosted models via Ollama.
- ``LangChainProvider``: Bridge wrapping any LangChain ``BaseChatModel`` (recommended for
  LangGraph integration; ``ChatOllama`` is the default, swap to any other chat model).
- ``LoggedProvider``: Wrapper that adds automatic timing and DB logging around any provider.
- ``InterventionLogger``: Guided terminal UI for logging human interventions outside AI calls.
- ``get_provider``: Registry that resolves a model name from ``models.toml`` to a provider instance.
- ``register_provider``: Decorator that registers a class or callable as a named provider.

Built-in providers
------------------
Ollama is the default because it requires no API key and works with any
open-source model.  See ``sdlc_core/providers/examples/`` for ready-to-use
extensions for Anthropic, OpenAI, Google Gemini, and LangChain + Ollama.

Adding a custom provider
------------------------
The preferred approach is the ``@register_provider`` decorator::

    from sdlc_core.providers import register_provider

    @register_provider("my_api")
    class MyProvider:
        def complete(self, prompt, system=None, **kwargs):
            return call_my_api(prompt)

    # Or as a plain function:

    @register_provider("my_api")
    def my_api_complete(prompt, system=None, **kwargs):
        return call_my_api(prompt)

Then add a matching entry to ``models.toml`` in your template repo with
``provider = "my_api"``.
"""

from __future__ import annotations

from sdlc_core.providers.base import ModelProvider
from sdlc_core.providers.intervention import InterventionLogger
from sdlc_core.providers.logged import LoggedProvider
from sdlc_core.providers.manual import ManualProvider
from sdlc_core.providers.registry import get_provider, register_provider

__all__ = [
    "InterventionLogger",
    "LangChainProvider",
    "LoggedProvider",
    "ManualProvider",
    "ModelProvider",
    "OllamaProvider",
    "get_provider",
    "register_provider",
]

# Lazy imports so optional packages are only required when actually used
def __getattr__(name: str) -> object:
    if name == "OllamaProvider":
        from sdlc_core.providers.ollama import OllamaProvider
        return OllamaProvider
    if name == "LangChainProvider":
        from sdlc_core.providers.langchain_provider import LangChainProvider
        return LangChainProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
