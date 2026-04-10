"""Tests for bridge frontend assets (chat.html)."""

import os


class TestBridgeFrontend:
    def test_chat_html_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", "web", "chat.html")
        assert os.path.exists(path), "bridge/web/chat.html should exist"

    def test_chat_html_not_empty(self):
        path = os.path.join(os.path.dirname(__file__), "..", "web", "chat.html")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 100, "chat.html should have meaningful content"

    def test_chat_html_has_doctype(self):
        path = os.path.join(os.path.dirname(__file__), "..", "web", "chat.html")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content or "<!doctype html>" in content
