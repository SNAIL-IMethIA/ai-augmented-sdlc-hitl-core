"""test_providers.py: Tests for sdlc_core.providers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from sdlc_core.providers.base import ModelProvider

# ---------------------------------------------------------------------------
# ModelProvider Protocol
# ---------------------------------------------------------------------------


def test_model_provider_is_runtime_checkable() -> None:
    class _Impl:
        def complete(
            self, prompt: str, system: str | None = None, **kwargs: Any
        ) -> str:
            return ""

    assert isinstance(_Impl(), ModelProvider)


def test_object_without_complete_fails_protocol() -> None:
    assert not isinstance(object(), ModelProvider)


def test_class_without_correct_signature_can_still_satisfy_protocol() -> None:
    """runtime_checkable only checks attribute presence, not signature."""

    class _Bare:
        def complete(self, *args: Any, **kwargs: Any) -> str:
            return ""

    assert isinstance(_Bare(), ModelProvider)


# ---------------------------------------------------------------------------
# OllamaProvider
# ---------------------------------------------------------------------------


def test_ollama_provider_import_error() -> None:
    from sdlc_core.providers.ollama import OllamaProvider

    provider = OllamaProvider(model_id="llama3")
    with patch.dict(sys.modules, {"ollama": None}):
        with pytest.raises(ImportError, match="ollama"):
            provider.complete("hello")


def test_ollama_provider_complete_basic() -> None:
    from sdlc_core.providers.ollama import OllamaProvider

    mock_ollama = MagicMock()
    mock_client = MagicMock()
    mock_ollama.Client.return_value = mock_client
    mock_client.chat.return_value = {"message": {"content": "Hi there!"}}

    with patch.dict(sys.modules, {"ollama": mock_ollama}):
        provider = OllamaProvider(model_id="llama3")
        result = provider.complete("Hello")

    assert result == "Hi there!"


def test_ollama_provider_passes_system_message() -> None:
    from sdlc_core.providers.ollama import OllamaProvider

    mock_ollama = MagicMock()
    mock_client = MagicMock()
    mock_ollama.Client.return_value = mock_client
    mock_client.chat.return_value = {"message": {"content": "resp"}}

    with patch.dict(sys.modules, {"ollama": mock_ollama}):
        OllamaProvider(model_id="llama3").complete("user msg", system="You are helpful.")

    messages = mock_client.chat.call_args.kwargs["messages"]
    assert any(m["role"] == "system" for m in messages)
    system_msg = next(m for m in messages if m["role"] == "system")
    assert "You are helpful." in system_msg["content"]


def test_ollama_provider_strips_stream_kwarg() -> None:
    from sdlc_core.providers.ollama import OllamaProvider

    mock_ollama = MagicMock()
    mock_client = MagicMock()
    mock_ollama.Client.return_value = mock_client
    mock_client.chat.return_value = {"message": {"content": "resp"}}

    with patch.dict(sys.modules, {"ollama": mock_ollama}):
        OllamaProvider(model_id="llama3").complete(
            "prompt", stream=True, temperature=0.7
        )

    options = mock_client.chat.call_args.kwargs.get("options") or {}
    assert "stream" not in options
    assert options.get("temperature") == 0.7


def test_ollama_provider_no_options_when_no_kwargs() -> None:
    from sdlc_core.providers.ollama import OllamaProvider

    mock_ollama = MagicMock()
    mock_client = MagicMock()
    mock_ollama.Client.return_value = mock_client
    mock_client.chat.return_value = {"message": {"content": "resp"}}

    with patch.dict(sys.modules, {"ollama": mock_ollama}):
        OllamaProvider(model_id="llama3").complete("prompt")

    options = mock_client.chat.call_args.kwargs.get("options")
    assert options is None


def test_ollama_provider_api_base_trailing_slash_stripped() -> None:
    from sdlc_core.providers.ollama import OllamaProvider

    p = OllamaProvider(model_id="llama3", api_base="http://localhost:11434/")
    assert p._api_base == "http://localhost:11434"


def test_ollama_provider_uses_api_base() -> None:
    from sdlc_core.providers.ollama import OllamaProvider

    mock_ollama = MagicMock()
    mock_client = MagicMock()
    mock_ollama.Client.return_value = mock_client
    mock_client.chat.return_value = {"message": {"content": "ok"}}

    with patch.dict(sys.modules, {"ollama": mock_ollama}):
        OllamaProvider(
            model_id="llama3", api_base="http://remote:11434"
        ).complete("p")

    mock_ollama.Client.assert_called_once_with(host="http://remote:11434")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_get_provider_ollama(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text(
        '[models.m]\nprovider = "ollama"\nmodel_id = "llama3"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    from sdlc_core.providers.ollama import OllamaProvider
    from sdlc_core.providers.registry import get_provider

    provider = get_provider("m")
    assert isinstance(provider, OllamaProvider)


def test_get_provider_with_api_base(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text(
        '[models.m]\nprovider = "ollama"\nmodel_id = "mistral"\n'
        'api_base = "http://remote:11434"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    from sdlc_core.providers.ollama import OllamaProvider
    from sdlc_core.providers.registry import get_provider

    p = get_provider("m")
    assert isinstance(p, OllamaProvider)
    assert p._api_base == "http://remote:11434"


def test_get_provider_missing_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text(
        '[models.other]\nprovider = "ollama"\nmodel_id = "llama3"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    from sdlc_core.providers.registry import get_provider

    with pytest.raises(KeyError, match="notexist"):
        get_provider("notexist")


def test_get_provider_missing_models_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SDLC_MODELS_TOML", str(tmp_path / "no.toml"))
    from sdlc_core.providers.registry import get_provider

    with pytest.raises(FileNotFoundError):
        get_provider("m")


def test_get_provider_missing_provider_field(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text('[models.m]\nmodel_id = "llama3"\n', encoding="utf-8")
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    from sdlc_core.providers.registry import get_provider

    with pytest.raises(ValueError, match="missing the 'provider' field"):
        get_provider("m")


def test_get_provider_unknown_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text(
        '[models.m]\nprovider = "nope"\nmodel_id = "llama3"\n', encoding="utf-8"
    )
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    from sdlc_core.providers.registry import get_provider

    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("m")


def test_load_models_toml_custom_env_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custom = tmp_path / "custom.toml"
    custom.write_text('[models.x]\nprovider = "ollama"\n', encoding="utf-8")
    monkeypatch.setenv("SDLC_MODELS_TOML", str(custom))
    from sdlc_core.providers.registry import _load_models_toml

    data = _load_models_toml()
    assert "x" in data["models"]


def test_load_models_toml_default_path_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SDLC_MODELS_TOML", raising=False)
    monkeypatch.chdir(tmp_path)
    from sdlc_core.providers.registry import _load_models_toml

    with pytest.raises(FileNotFoundError):
        _load_models_toml()


def test_registry_custom_provider_class(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Registering a custom class type (not a factory function) works."""
    toml = tmp_path / "models.toml"
    toml.write_text(
        '[models.custom]\nprovider = "custom_key"\n', encoding="utf-8"
    )
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))

    from sdlc_core.providers.registry import PROVIDER_CLASSES, get_provider

    class _CustomProvider:
        def complete(
            self, prompt: str, system: str | None = None, **kwargs: Any
        ) -> str:
            return "custom"

    PROVIDER_CLASSES["custom_key"] = _CustomProvider
    try:
        p = get_provider("custom")
        assert isinstance(p, _CustomProvider)
    finally:
        del PROVIDER_CLASSES["custom_key"]


# ---------------------------------------------------------------------------
# Package __init__ lazy import
# ---------------------------------------------------------------------------


def test_providers_package_exports_model_provider() -> None:
    import sdlc_core.providers as pkg

    assert hasattr(pkg, "ModelProvider")


def test_providers_package_exports_get_provider() -> None:
    import sdlc_core.providers as pkg

    assert hasattr(pkg, "get_provider")


def test_providers_package_ollama_lazy_load() -> None:
    import sdlc_core.providers as pkg

    cls = pkg.OllamaProvider
    from sdlc_core.providers.ollama import OllamaProvider

    assert cls is OllamaProvider


def test_providers_package_unknown_attr_raises() -> None:
    import sdlc_core.providers as pkg

    with pytest.raises(AttributeError):
        _ = pkg.DoesNotExist


def test_providers_package_exports_register_provider() -> None:
    import sdlc_core.providers as pkg

    assert hasattr(pkg, "register_provider")


# ---------------------------------------------------------------------------
# register_provider decorator
# ---------------------------------------------------------------------------


def test_register_provider_class_is_stored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sdlc_core.providers.registry import PROVIDER_CLASSES, register_provider

    @register_provider("_test_class_reg")
    class _P:
        def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:
            return "ok"

    try:
        assert "_test_class_reg" in PROVIDER_CLASSES
        assert PROVIDER_CLASSES["_test_class_reg"] is _P
    finally:
        del PROVIDER_CLASSES["_test_class_reg"]


def test_register_provider_class_returns_original() -> None:
    from sdlc_core.providers.registry import PROVIDER_CLASSES, register_provider

    class _P:
        def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:
            return "ok"

    result = register_provider("_test_ret")(_P)
    try:
        assert result is _P
    finally:
        del PROVIDER_CLASSES["_test_ret"]


def test_register_provider_callable_wraps_in_adapter() -> None:
    from sdlc_core.providers.registry import PROVIDER_CLASSES, register_provider

    @register_provider("_test_fn_reg")
    def _fn(prompt: str, system: str | None = None, **kwargs: Any) -> str:
        return f"fn:{prompt}"

    try:
        adapter_cls = PROVIDER_CLASSES["_test_fn_reg"]
        assert isinstance(adapter_cls, type)
        instance = adapter_cls()
        assert instance.complete("hello") == "fn:hello"
    finally:
        del PROVIDER_CLASSES["_test_fn_reg"]


def test_register_provider_callable_returns_original_function() -> None:
    from sdlc_core.providers.registry import PROVIDER_CLASSES, register_provider

    def _fn(prompt: str, system: str | None = None, **kwargs: Any) -> str:
        return prompt

    result = register_provider("_test_fn_ret")(_fn)
    try:
        assert result is _fn
    finally:
        del PROVIDER_CLASSES["_test_fn_ret"]


def test_register_provider_callable_passes_system_kwarg() -> None:
    from sdlc_core.providers.registry import PROVIDER_CLASSES, register_provider

    received: dict[str, Any] = {}

    @register_provider("_test_fn_sys")
    def _fn(prompt: str, system: str | None = None, **kwargs: Any) -> str:
        received["system"] = system
        return "ok"

    try:
        adapter_cls = PROVIDER_CLASSES["_test_fn_sys"]
        adapter_cls().complete("p", system="Be concise.")
        assert received["system"] == "Be concise."
    finally:
        del PROVIDER_CLASSES["_test_fn_sys"]


def test_register_provider_callable_forwards_kwargs() -> None:
    from sdlc_core.providers.registry import PROVIDER_CLASSES, register_provider

    received: dict[str, Any] = {}

    @register_provider("_test_fn_kw")
    def _fn(prompt: str, system: str | None = None, **kwargs: Any) -> str:
        received.update(kwargs)
        return "ok"

    try:
        adapter_cls = PROVIDER_CLASSES["_test_fn_kw"]
        adapter_cls().complete("p", temperature=0.7, max_tokens=50)
        assert received["temperature"] == 0.7
        assert received["max_tokens"] == 50
    finally:
        del PROVIDER_CLASSES["_test_fn_kw"]


def test_register_provider_decorator_used_with_get_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: decorate a function, then resolve it via get_provider."""
    from sdlc_core.providers.registry import PROVIDER_CLASSES, get_provider, register_provider

    @register_provider("_test_e2e")
    def _fn(prompt: str, system: str | None = None, **kwargs: Any) -> str:
        return "e2e-response"

    toml = tmp_path / "models.toml"
    toml.write_text('[models.mymodel]\nprovider = "_test_e2e"\n', encoding="utf-8")
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))

    try:
        provider = get_provider("mymodel")
        assert provider.complete("test") == "e2e-response"
    finally:
        del PROVIDER_CLASSES["_test_e2e"]


# ---------------------------------------------------------------------------
# LangChainProvider
# ---------------------------------------------------------------------------


def _make_fake_langchain_modules(
    response_content: str = "lc response",
) -> tuple[MagicMock, MagicMock]:
    """Build minimal fakes for langchain_core.messages."""
    fake_lc_core = MagicMock()
    fake_lc_core.messages.HumanMessage = MagicMock(
        side_effect=lambda content: {"role": "user", "content": content}
    )
    fake_lc_core.messages.SystemMessage = MagicMock(
        side_effect=lambda content: {"role": "system", "content": content}
    )

    fake_response = MagicMock()
    fake_response.content = response_content
    fake_response.usage_metadata = {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}

    fake_model = MagicMock()
    fake_model.invoke.return_value = fake_response
    fake_model.model = "llama3"

    return fake_lc_core, fake_model


def test_langchain_provider_returns_response_content() -> None:
    from sdlc_core.providers.langchain_provider import LangChainProvider

    fake_lc_core, fake_model = _make_fake_langchain_modules("the answer")
    with patch.dict(
        sys.modules,
        {"langchain_core": fake_lc_core, "langchain_core.messages": fake_lc_core.messages},
    ):
        provider = LangChainProvider(fake_model)
        result = provider.complete("What is 2+2?")

    assert result == "the answer"


def test_langchain_provider_model_id_from_model_attribute() -> None:
    from sdlc_core.providers.langchain_provider import LangChainProvider

    fake_lc_core, fake_model = _make_fake_langchain_modules()
    provider = LangChainProvider(fake_model)
    assert provider._model_id == "llama3"


def test_langchain_provider_model_id_fallback_to_class_name() -> None:
    from sdlc_core.providers.langchain_provider import LangChainProvider

    class _FakeModel:
        def invoke(self, messages: Any, **kw: Any) -> Any:
            r = MagicMock()
            r.content = "ok"
            r.usage_metadata = {}
            return r

    provider = LangChainProvider(_FakeModel())
    assert provider._model_id == "_FakeModel"


def test_langchain_provider_captures_token_usage() -> None:
    from sdlc_core.providers.langchain_provider import LangChainProvider

    fake_lc_core, fake_model = _make_fake_langchain_modules()
    with patch.dict(
        sys.modules,
        {"langchain_core": fake_lc_core, "langchain_core.messages": fake_lc_core.messages},
    ):
        provider = LangChainProvider(fake_model)
        provider.complete("prompt")

    usage = provider.last_token_usage
    assert usage["prompt_tokens"] == 10
    assert usage["completion_tokens"] == 20
    assert usage["total_tokens"] == 30


def test_langchain_provider_zero_tokens_when_usage_absent() -> None:
    from sdlc_core.providers.langchain_provider import LangChainProvider

    fake_lc_core, fake_model = _make_fake_langchain_modules()
    fake_model.invoke.return_value.usage_metadata = None
    with patch.dict(
        sys.modules,
        {"langchain_core": fake_lc_core, "langchain_core.messages": fake_lc_core.messages},
    ):
        provider = LangChainProvider(fake_model)
        provider.complete("prompt")

    assert provider.last_token_usage["prompt_tokens"] == 0


def test_langchain_provider_raises_import_error_without_langchain_core() -> None:
    from sdlc_core.providers.langchain_provider import LangChainProvider

    fake_model = MagicMock()
    provider = LangChainProvider(fake_model)
    with patch.dict(sys.modules, {"langchain_core": None, "langchain_core.messages": None}):
        with pytest.raises(ImportError, match="langchain-core"):
            provider.complete("prompt")


def test_langchain_provider_satisfies_model_provider_protocol() -> None:
    from sdlc_core.providers.base import ModelProvider
    from sdlc_core.providers.langchain_provider import LangChainProvider

    assert isinstance(LangChainProvider(MagicMock()), ModelProvider)


def test_langchain_provider_last_token_usage_returns_copy() -> None:
    from sdlc_core.providers.langchain_provider import LangChainProvider

    provider = LangChainProvider(MagicMock())
    usage = provider.last_token_usage
    usage["prompt_tokens"] = 9999
    assert provider.last_token_usage["prompt_tokens"] == 0
