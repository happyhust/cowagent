"""Tests for cowagent.agent.protocol.models."""

from cowagent.agent.protocol.models import LLMRequest, LLMModel, ModelFactory
import pytest


class TestLLMRequest:
    def test_defaults(self):
        req = LLMRequest()
        assert req.messages == []
        assert req.model is None
        assert req.temperature == 0.7
        assert req.max_tokens is None
        assert req.stream is False
        assert req.tools is None

    def test_custom(self):
        req = LLMRequest(
            messages=[{"role": "user", "content": "hi"}],
            model="gpt-4",
            temperature=0.5,
            max_tokens=100,
            stream=True,
        )
        assert len(req.messages) == 1
        assert req.model == "gpt-4"
        assert req.temperature == 0.5
        assert req.max_tokens == 100
        assert req.stream is True

    def test_extra_kwargs(self):
        req = LLMRequest(custom_field="value")
        assert req.custom_field == "value"


class TestLLMModel:
    def test_init(self):
        model = LLMModel(model="test-model", api_key="secret")
        assert model.model == "test-model"
        assert model.config == {"api_key": "secret"}

    def test_call_not_implemented(self):
        model = LLMModel()
        with pytest.raises(NotImplementedError):
            model.call(LLMRequest())

    def test_call_stream_not_implemented(self):
        model = LLMModel()
        with pytest.raises(NotImplementedError):
            model.call_stream(LLMRequest())


class TestModelFactory:
    def test_create_model_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ModelFactory.create_model("unknown")
