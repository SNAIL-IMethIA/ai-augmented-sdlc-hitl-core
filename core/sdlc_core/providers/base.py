"""base.py: ModelProvider Protocol. The contract every provider must satisfy.

A provider is any object with a ``complete`` method matching the signature
below.  The Protocol is structural (``runtime_checkable``), so duck-typing
works: no base-class inheritance required.

Example custom provider
-----------------------
>>> class MyProvider:
...     def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:
...         return call_my_api(prompt)

Register it in ``registry.py`` under a ``provider`` name and add a matching
entry to ``models.toml``.  No other changes are needed.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ModelProvider(Protocol):
    """Contract that every model provider implementation must satisfy.

    Parameters passed to ``complete`` are intentionally loose. Providers
    forward unrecognised ``**kwargs`` to the underlying API, allowing
    temperature, max_tokens, top_p, and any future parameters to pass
    through without changes to this interface.
    """

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Send *prompt* to the model and return the full response text.

        Args:
            prompt: The user-turn text to send.
            system: Optional system / instruction prompt.  Providers that do
                    not support a dedicated system role may prepend it to
                    *prompt* or ignore it. Both are acceptable.
            **kwargs: Provider-specific parameters (e.g. ``temperature``,
                      ``max_tokens``).  Unknown kwargs must be silently
                      ignored or forwarded, never raise.

        Returns:
            The model's response as a plain string.

        """
        ...
