"""Tests for cowagent.agent.skills.frontmatter."""

from cowagent.agent.skills.frontmatter import (
    parse_frontmatter,
    parse_metadata,
    parse_boolean_value,
    get_frontmatter_value,
    _normalize_string_list,
    _unwrap_metadata_namespace,
)


class TestParseFrontmatter:
    def test_no_frontmatter(self):
        assert parse_frontmatter("just text") == {}

    def test_simple_key_value(self):
        result = parse_frontmatter("---\nname: test\ndesc: hello\n---\ncontent")
        assert result.get("name") == "test"
        assert result.get("desc") == "hello"

    def test_boolean_parsing(self):
        result = parse_frontmatter("---\nenabled: true\ndisabled: false\n---\ncontent")
        assert result.get("enabled") is True
        assert result.get("disabled") is False

    def test_number_parsing(self):
        result = parse_frontmatter("---\ncount: 42\n---\ncontent")
        assert result.get("count") == 42

    def test_json_parsing(self):
        result = parse_frontmatter('---\ndata: {"key": "val"}\n---\ncontent')
        assert result.get("data") == {"key": "val"}


class TestParseBooleanValue:
    def test_none(self):
        assert parse_boolean_value(None) is False

    def test_bool(self):
        assert parse_boolean_value(True) is True
        assert parse_boolean_value(False) is False

    def test_string(self):
        assert parse_boolean_value("true") is True
        assert parse_boolean_value("false") is False
        assert parse_boolean_value("1") is True
        assert parse_boolean_value("0") is False
        assert parse_boolean_value("yes") is True
        assert parse_boolean_value("no") is False

    def test_default(self):
        assert parse_boolean_value(None, default=True) is True


class TestGetFrontmatterValue:
    def test_existing_key(self):
        fm = {"name": "test"}
        assert get_frontmatter_value(fm, "name") == "test"

    def test_missing_key(self):
        fm = {"name": "test"}
        assert get_frontmatter_value(fm, "missing") is None

    def test_none_value(self):
        fm = {"key": None}
        assert get_frontmatter_value(fm, "key") is None


class TestNormalizeStringList:
    def test_string(self):
        assert _normalize_string_list("a, b, c") == ["a", "b", "c"]

    def test_list(self):
        assert _normalize_string_list(["a", "b"]) == ["a", "b"]

    def test_empty(self):
        assert _normalize_string_list("") == []
        assert _normalize_string_list(None) == []
        assert _normalize_string_list([]) == []


class TestUnwrapMetadataNamespace:
    def test_known_namespace(self):
        result = _unwrap_metadata_namespace({"cowagent": {"key": "val"}})
        assert result == {"key": "val"}

    def test_unknown_namespace(self):
        result = _unwrap_metadata_namespace({"cowagent": {"key": "val"}, "extra": 1})
        # Has extra key, so not unwrapped
        assert result == {"cowagent": {"key": "val"}, "extra": 1}

    def test_not_namespace_wrapped(self):
        result = _unwrap_metadata_namespace({"key": "val"})
        assert result == {"key": "val"}


class TestParseMetadata:
    def test_no_metadata(self):
        assert parse_metadata({}) is None

    def test_valid_metadata(self):
        fm = {"metadata": {"default_enabled": True, "always": False}}
        result = parse_metadata(fm)
        assert result is not None
        assert result.default_enabled is True
        assert result.always is False
