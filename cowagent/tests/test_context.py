"""Tests for cowagent.bridge.context."""

from cowagent.bridge.context import Context, ContextType


class TestContextType:
    def test_str(self):
        assert str(ContextType.TEXT) == "TEXT"
        assert str(ContextType.VOICE) == "VOICE"

    def test_values(self):
        assert ContextType.TEXT.value == 1
        assert ContextType.IMAGE.value == 3
        assert ContextType.FUNCTION.value == 22


class TestContext:
    def test_default(self):
        c = Context()
        assert c.type is None
        assert c.content is None
        assert c.kwargs == {}

    def test_with_values(self):
        c = Context(type=ContextType.TEXT, content="hello")
        assert c.type == ContextType.TEXT
        assert c.content == "hello"

    def test_contains_type(self):
        c = Context(type=ContextType.TEXT, content="hello")
        assert "type" in c

    def test_contains_content(self):
        c = Context(type=ContextType.TEXT, content="hello")
        assert "content" in c

    def test_contains_kwarg(self):
        c = Context(type=ContextType.TEXT, content="hi", kwargs={"session_id": "123"})
        assert "session_id" in c

    def test_contains_missing(self):
        c = Context(type=ContextType.TEXT, content="hi")
        assert "missing" not in c

    def test_getitem(self):
        c = Context(
            type=ContextType.TEXT,
            content="hello",
            kwargs={"extra": "value"},
        )
        assert c["type"] == ContextType.TEXT
        assert c["content"] == "hello"
        assert c["extra"] == "value"

    def test_get_with_default(self):
        c = Context(type=ContextType.TEXT, content="hi")
        assert c.get("missing", "default") == "default"

    def test_setitem(self):
        c = Context(type=ContextType.TEXT, content="hi")
        c["new_key"] = "new_value"
        assert c.kwargs["new_key"] == "new_value"

    def test_setitem_type(self):
        c = Context()
        c["type"] = ContextType.IMAGE
        assert c.type == ContextType.IMAGE

    def test_setitem_content(self):
        c = Context()
        c["content"] = "updated"
        assert c.content == "updated"

    def test_delitem(self):
        c = Context(
            type=ContextType.TEXT, content="hi", kwargs={"extra": "val"}
        )
        del c["extra"]
        assert "extra" not in c.kwargs

    def test_delitem_type(self):
        c = Context(type=ContextType.TEXT, content="hi")
        del c["type"]
        assert c.type is None

    def test_delitem_content(self):
        c = Context(type=ContextType.TEXT, content="hi")
        del c["content"]
        assert c.content is None

    def test_str(self):
        c = Context(type=ContextType.TEXT, content="hi")
        s = str(c)
        assert "TEXT" in s
        assert "hi" in s
