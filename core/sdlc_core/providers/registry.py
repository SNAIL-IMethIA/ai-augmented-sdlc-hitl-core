"""registry.py: Resolve a model name from models.toml to a provider instance.

``get_provider`` is the single entry point used by all command modules.

Provider resolution
-------------------
1. Load ``models.toml`` from the working directory (or the path in the
   ``SDLC_MODELS_TOML`` environment variable).
2. Look up the model name in the ``[models.*]`` table.
3. Instantiate the class registered under the ``provider`` key.
4. Return the instance, ready to call ``.complete()``.

Built-in provider keys
----------------------
``"ollama"``  → :class:`sdlc_core.providers.ollama.OllamaProvider`
``"manual"``  → :class:`sdlc_core.providers.manual.ManualProvider`

Registering a custom provider (decorator style)
------------------------------------------------
The preferred way to register a provider is the ``@register_provider``
decorator.  It accepts a class with a ``complete`` method, or a plain
callable function:

    from sdlc_core.providers.registry import register_provider

    @register_provider("anthropic")
    class AnthropicProvider:
        def complete(self, prompt, system=None, **kwargs):
            ...

    # Or as a plain function (wrapped in a thin adapter class automatically):

    @register_provider("my_api")
    def my_api_complete(prompt, system=None, **kwargs):
        return call_api(prompt)

The decorator returns the class or function unchanged, so it can still be
imported, tested, and used directly.

Registering via dict (imperative style)
---------------------------------------
You can also mutate ``PROVIDER_CLASSES`` directly before calling
``get_provider``.  The decorator is just a cleaner spelling of the same
operation:

    from sdlc_core.providers.registry import PROVIDER_CLASSES
    PROVIDER_CLASSES["my_provider"] = MyProvider
"""

from __future__ import annotations

import os
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from sdlc_core.providers.base import ModelProvider

_C = TypeVar("_C", bound=Callable[..., Any])

# ---------------------------------------------------------------------------
# Built-in provider registry
# Keys must match the ``provider`` value in models.toml entries
# ---------------------------------------------------------------------------

def _ollama_class() -> type:
    from sdlc_core.providers.ollama import OllamaProvider
    return OllamaProvider


def _manual_class() -> type:
    from sdlc_core.providers.manual import ManualProvider
    return ManualProvider


PROVIDER_CLASSES: dict[str, Any] = {
    "ollama": _ollama_class,
    "manual": _manual_class,
}


# ---------------------------------------------------------------------------
# Registration decorator
# ---------------------------------------------------------------------------

def register_provider(name: str) -> Callable[[_C], _C]:
    """Register a class or callable as a named provider.

    Args:
        name: The ``provider`` key used in ``models.toml`` entries.

    Returns:
        A decorator that registers the target and returns it unchanged.

    The decorated object may be:

    * **A class** with a ``complete(prompt, system, **kwargs) -> str``
      method.  Registered as-is.
    * **A plain function** with signature
      ``(prompt, system=None, **kwargs) -> str``.  Wrapped in a thin
      adapter class automatically so ``get_provider`` can call
      ``.complete()`` on it.

    Examples::

        @register_provider("anthropic")
        class AnthropicProvider:
            def complete(self, prompt, system=None, **kwargs):
                ...

        @register_provider("my_api")
        def my_api_complete(prompt, system=None, **kwargs):
            return call_api(prompt)

    """
    def decorator(cls_or_fn: _C) -> _C:
        if isinstance(cls_or_fn, type):
            PROVIDER_CLASSES[name] = cls_or_fn
        else:
            # Wrap a plain callable in a thin adapter so the registry can
            # Call .complete() on it uniformly
            _fn = cls_or_fn

            class _FuncAdapter:
                def complete(
                    self,
                    prompt: str,
                    system: str | None = None,
                    **kwargs: Any,  # noqa: ANN401
                ) -> str:
                    return _fn(prompt, system=system, **kwargs)  # type: ignore[no-any-return]

            _FuncAdapter.__name__ = getattr(cls_or_fn, "__name__", "FuncAdapter")
            PROVIDER_CLASSES[name] = _FuncAdapter
        return cls_or_fn

    return decorator


# ---------------------------------------------------------------------------
# TOML loading
# ---------------------------------------------------------------------------

def _load_models_toml() -> dict[str, Any]:
    """Load and return the parsed contents of models.toml.

    Raises:
        FileNotFoundError: If models.toml cannot be found.

    """
    env_path = os.environ.get("SDLC_MODELS_TOML")
    path = Path(env_path) if env_path else Path("models.toml")

    if not path.exists():
        raise FileNotFoundError(
            f"models.toml not found at {path.resolve()}.\n"
            "Copy models.example.toml to models.toml and fill in your models."
        )

    with path.open("rb") as fh:
        return tomllib.load(fh)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_provider(model_name: str) -> ModelProvider:
    """Return a ready-to-call provider instance for *model_name*.

    Args:
        model_name: Key under ``[models]`` in ``models.toml``,
                    e.g. ``"llama3"`` or ``"manual"``.

    Returns:
        An object satisfying :class:`~sdlc_core.providers.base.ModelProvider`.

    Raises:
        FileNotFoundError: If ``models.toml`` is missing.
        KeyError: If *model_name* has no entry in ``models.toml``.
        ValueError: If the ``provider`` field names an unregistered class.

    """
    data = _load_models_toml()
    models_section: dict[str, Any] = data.get("models", {})

    if model_name not in models_section:
        available = ", ".join(models_section.keys()) or "(none)"
        raise KeyError(
            f"Model {model_name!r} not found in models.toml.\n"
            f"Available models: {available}"
        )

    entry: dict[str, Any] = models_section[model_name]
    provider_key: str = entry.get("provider", "")

    if not provider_key:
        raise ValueError(
            f"models.toml entry {model_name!r} is missing the 'provider' field."
        )

    if provider_key not in PROVIDER_CLASSES:
        raise ValueError(
            f"Unknown provider {provider_key!r} for model {model_name!r}.\n"
            f"Registered providers: {', '.join(PROVIDER_CLASSES)}\n"
            "To add a custom provider, see sdlc_core/providers/examples/."
        )

    cls_factory = PROVIDER_CLASSES[provider_key]
    is_factory_fn = callable(cls_factory) and not isinstance(cls_factory, type)
    cls = cls_factory() if is_factory_fn else cls_factory

    # Build keyword arguments from the TOML entry
    # Standard keys are consumed here and others are forwarded to the constructor
    init_kwargs: dict[str, Any] = {}

    model_id = entry.get("model_id", "")
    if model_id:
        init_kwargs["model_id"] = model_id

    api_base = entry.get("api_base", "")
    if api_base:
        init_kwargs["api_base"] = api_base

    # Constructors that don't accept these kwargs (e.g. ManualProvider)
    # will receive nothing and the kwargs dict will be empty for them
    if not init_kwargs:
        return cls()  # type: ignore[no-any-return]

    return cls(**init_kwargs)  # type: ignore[no-any-return]
