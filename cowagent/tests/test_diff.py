"""Tests for cowagent.agent.tools.utils.diff."""

from cowagent.agent.tools.utils.diff import (
    strip_bom,
    detect_line_ending,
    normalize_to_lf,
    restore_line_endings,
    normalize_for_fuzzy_match,
    fuzzy_find_text,
    generate_diff_string,
)


class TestStripBom:
    def test_with_bom(self):
        bom, text = strip_bom("\ufeffhello")
        assert bom == "\ufeff"
        assert text == "hello"

    def test_without_bom(self):
        bom, text = strip_bom("hello")
        assert bom == ""
        assert text == "hello"


class TestDetectLineEnding:
    def test_crlf(self):
        assert detect_line_ending("a\r\nb") == "\r\n"

    def test_lf(self):
        assert detect_line_ending("a\nb") == "\n"

    def test_empty(self):
        assert detect_line_ending("") == "\n"


class TestNormalizeToLf:
    def test_crlf_to_lf(self):
        assert normalize_to_lf("a\r\nb") == "a\nb"

    def test_already_lf(self):
        assert normalize_to_lf("a\nb") == "a\nb"


class TestRestoreLineEndings:
    def test_restore_crlf(self):
        result = restore_line_endings("a\nb", "\r\n")
        assert result == "a\r\nb"

    def test_keep_lf(self):
        result = restore_line_endings("a\nb", "\n")
        assert result == "a\nb"


class TestNormalizeForFuzzyMatch:
    def test_compress_spaces(self):
        result = normalize_for_fuzzy_match("hello    world")
        assert result == "hello world"

    def test_remove_trailing_spaces(self):
        result = normalize_for_fuzzy_match("hello   \n")
        assert result == "hello\n"


class TestFuzzyFindText:
    def test_exact_match(self):
        result = fuzzy_find_text("hello world", "world")
        assert result.found is True
        assert result.index == 6

    def test_no_match(self):
        result = fuzzy_find_text("hello world", "xyz")
        assert result.found is False

    def test_fuzzy_match(self):
        # Normalize whitespace differences
        result = fuzzy_find_text("  hello  world  ", "hello world")
        assert result.found is True


class TestGenerateDiffString:
    def test_no_diff(self):
        result = generate_diff_string("same", "same")
        assert result["first_changed_line"] is None

    def test_with_diff(self):
        result = generate_diff_string("old", "new")
        assert "--- original" in result["diff"]
        assert "+++ modified" in result["diff"]
        assert result["first_changed_line"] is not None
