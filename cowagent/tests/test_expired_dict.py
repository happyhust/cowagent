"""Tests for cowagent.common.expired_dict."""

import time
from cowagent.common.expired_dict import ExpiredDict


class TestExpiredDict:
    def test_set_and_get(self):
        d = ExpiredDict(expires_in_seconds=60)
        d["a"] = 1
        assert d["a"] == 1

    def test_get_with_default(self):
        d = ExpiredDict(expires_in_seconds=60)
        assert d.get("missing", "default") == "default"

    def test_get_existing(self):
        d = ExpiredDict(expires_in_seconds=60)
        d["key"] = "val"
        assert d.get("key") == "val"

    def test_contains(self):
        d = ExpiredDict(expires_in_seconds=60)
        d["a"] = 1
        assert "a" in d
        assert "b" not in d

    def test_keys(self):
        d = ExpiredDict(expires_in_seconds=60)
        d["a"] = 1
        d["b"] = 2
        assert set(d.keys()) == {"a", "b"}

    def test_items(self):
        d = ExpiredDict(expires_in_seconds=60)
        d["a"] = 1
        items = d.items()
        assert len(items) == 1
        assert items[0] == ("a", 1)

    def test_iter(self):
        d = ExpiredDict(expires_in_seconds=60)
        d["x"] = 10
        d["y"] = 20
        assert set(list(d)) == {"x", "y"}

    def test_expiration(self):
        d = ExpiredDict(expires_in_seconds=0)
        d["a"] = 1
        time.sleep(0.01)
        assert "a" not in d
        assert d.get("a", "expired") == "expired"

    def test_not_expired_yet(self):
        d = ExpiredDict(expires_in_seconds=10)
        d["a"] = 1
        assert d["a"] == 1

    def test_delete_expired_doesnt_affect_valid(self):
        d = ExpiredDict(expires_in_seconds=60)
        d["a"] = 1
        d["b"] = 2
        assert len(d.keys()) == 2

    def test_len(self):
        d = ExpiredDict(expires_in_seconds=60)
        d["a"] = 1
        d["b"] = 2
        assert len(d) == 2
