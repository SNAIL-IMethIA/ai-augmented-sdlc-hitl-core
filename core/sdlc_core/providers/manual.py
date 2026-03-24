"""manual.py: ManualProvider, the HITL terminal provider for Approach 1.

The researcher sees the prompt printed to stdout, writes or pastes the model
response, and confirms with a blank line followed by the sentinel ``END``.
The captured text is returned as the provider response and logged to the DB
exactly like any automated provider response.

This is a first-class provider, not a special case.  Approach 1 simply
assigns ``manual`` as the model for every phase in ``run_config.toml``.
"""

from __future__ import annotations

import textwrap
from typing import Any


class ManualProvider:
    """Provider that routes prompts through the researcher's terminal.

    No API key, no network call.  The researcher copies the prompt into
    whatever interface they are using (browser, local app, IDE plugin),
    pastes the response back, and presses Enter twice then types END.
    """

    def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:  # noqa: ANN401
        """Print *prompt* to stdout and read the researcher's response from stdin.

        Args:
            prompt: The prompt text to display to the researcher.
            system: Optional system instruction, printed before the prompt.
            **kwargs: Ignored. Present only to satisfy the ``ModelProvider``
                      Protocol.

        Returns:
            The researcher's typed or pasted response, stripped of leading
            and trailing whitespace.

        """
        separator = "-" * 72

        print()
        print(separator)
        print("MANUAL PROVIDER: copy the prompt below into your model interface")
        print(separator)

        if system:
            print()
            print("[ SYSTEM / INSTRUCTION ]")
            print()
            print(textwrap.fill(system, width=80))

        print()
        print("[ PROMPT ]")
        print()
        print(prompt)
        print()
        print(separator)
        print("Paste the model response below.")
        print("When done, enter a blank line followed by:  END")
        print(separator)

        lines: list[str] = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)

        response = "\n".join(lines).strip()

        if not response:
            # Researcher confirmed but entered nothing
            # Record the absence explicitly so the DB row is never empty
            response = "[no response recorded]"

        return response
