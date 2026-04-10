"""Tests for cowagent.bridge.reply."""

from cowagent.bridge.reply import Reply, ReplyType


class TestReplyType:
    def test_str(self):
        assert str(ReplyType.TEXT) == "TEXT"
        assert str(ReplyType.ERROR) == "ERROR"

    def test_values(self):
        assert ReplyType.TEXT.value == 1
        assert ReplyType.VOICE.value == 2
        assert ReplyType.IMAGE.value == 3


class TestReply:
    def test_default(self):
        r = Reply()
        assert r.type is None
        assert r.content is None

    def test_with_values(self):
        r = Reply(type=ReplyType.TEXT, content="hello")
        assert r.type == ReplyType.TEXT
        assert r.content == "hello"

    def test_str(self):
        r = Reply(type=ReplyType.TEXT, content="hi")
        assert "TEXT" in str(r)
        assert "hi" in str(r)
