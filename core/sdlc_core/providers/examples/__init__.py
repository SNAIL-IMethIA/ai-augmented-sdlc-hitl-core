"""examples: Ready-to-use provider extensions for commercial LLM APIs.

Each file in this package shows the exact pattern for extending the provider
system with a new API.

Available examples
------------------
- ``anthropic_provider.py``: Anthropic Claude (claude-3-*, claude-sonnet-*, ...)
- ``openai_provider.py``: OpenAI GPT models; also works for any OpenAI-compatible
  endpoint (Azure OpenAI, Together.ai, ...)
- ``gemini_provider.py``: Google Gemini (gemini-2.0-flash, gemini-pro, ...)
- ``litellm_provider.py``: Unified provider routing via LiteLLM

How to use (@register_provider decorator)
-----------------------------------------
1. Copy the file you need into your template repo (or any importable location).
2. Decorate your class (or function) with ``@register_provider``:

       from sdlc_core.providers import register_provider

       @register_provider("anthropic")
       class AnthropicProvider:
           ...

   That is all.  No separate registration step needed.
3. Add the matching entry to your ``models.toml``.

Alternative (imperative style)
-------------------------------
If you prefer not to use the decorator, mutate ``PROVIDER_CLASSES`` directly::

       from sdlc_core.providers.registry import PROVIDER_CLASSES
       from my_template.providers import AnthropicProvider
       PROVIDER_CLASSES["anthropic"] = AnthropicProvider

These files are intentionally self-contained so they can be copied without
bringing any sdlc_core internals with them.
"""
