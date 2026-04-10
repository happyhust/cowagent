"""Tests for cowagent.common.utils."""

from cowagent.common.utils import (
    fsize,
    split_string_by_utf8_length,
    get_path_suffix,
    remove_markdown_symbol,
    expand_path,
)
import io
import os


class TestFsize:
    def test_bytesio(self):
        buf = io.BytesIO(b"hello")
        assert fsize(buf) == 5

    def test_string_path(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("hi")
        assert fsize(str(p)) == 2

    def test_file_object(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("abcde")
        with open(p, "rb") as f:
            assert fsize(f) == 5

    def test_unsupported(self):
        try:
            fsize(123)
            assert False
        except TypeError:
            pass


class TestSplitStringByUtf8Length:
    def test_short_string(self):
        result = split_string_by_utf8_length("hello", 100)
        assert result == ["hello"]

    def test_exact_split(self):
        result = split_string_by_utf8_length("abcdefghij", 5)
        assert result == ["abcde", "fghij"]

    def test_max_split(self):
        # max_split=2 means first 2 chunks are split, rest goes in last element
        result = split_string_by_utf8_length("abcdefghij", 3, max_split=2)
        assert len(result) == 3
        assert result[0] == "abc"
        assert result[1] == "def"
        assert result[2] == "ghij"

    def test_multibyte_utf8(self):
        result = split_string_by_utf8_length("你好世界", 6)  # 每个汉字3字节
        assert len(result) >= 2


class TestGetPathSuffix:
    def test_url_with_extension(self):
        assert get_path_suffix("https://example.com/file.txt") == "txt"

    def test_url_no_extension(self):
        assert get_path_suffix("https://example.com/path") == ""

    def test_deep_path(self):
        assert get_path_suffix("/a/b/c/report.pdf") == "pdf"


class TestRemoveMarkdownSymbol:
    def test_remove_bold(self):
        assert remove_markdown_symbol("**hello**") == "hello"

    def test_multiple_bold(self):
        result = remove_markdown_symbol("**a** and **b**")
        assert "**" not in result

    def test_empty(self):
        assert remove_markdown_symbol("") == ""

    def test_none(self):
        assert remove_markdown_symbol(None) is None

    def test_no_markdown(self):
        assert remove_markdown_symbol("plain text") == "plain text"


class TestExpandPath:
    def test_normal_path(self):
        result = expand_path("/some/path")
        assert result == "/some/path"

    def test_tilde(self):
        result = expand_path("~")
        assert not result.startswith("~")
        assert result == os.path.expanduser("~")

    def test_tilde_subdir(self):
        result = expand_path("~/subdir")
        assert result.startswith(os.path.expanduser("~"))
        assert result.endswith("subdir")

    def test_empty(self):
        assert expand_path("") == ""

    def test_none(self):
        assert expand_path(None) is None
