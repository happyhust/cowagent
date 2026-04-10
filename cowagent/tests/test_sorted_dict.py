"""Tests for cowagent.common.sorted_dict."""

from cowagent.common.sorted_dict import SortedDict


class TestSortedDict:
    def test_basic_set_get(self):
        d = SortedDict()
        d["b"] = 2
        d["a"] = 1
        assert d["a"] == 1
        assert d["b"] == 2

    def test_keys_sorted_default(self):
        d = SortedDict(sort_func=lambda k, v: k)
        d["c"] = 3
        d["a"] = 1
        d["b"] = 2
        assert d.keys() == ["a", "b", "c"]

    def test_keys_sorted_reverse(self):
        d = SortedDict(sort_func=lambda k, v: k, reverse=True)
        d["a"] = 1
        d["b"] = 2
        d["c"] = 3
        assert d.keys() == ["c", "b", "a"]

    def test_custom_sort(self):
        d = SortedDict(sort_func=lambda k, v: v)
        d["c"] = 30
        d["a"] = 10
        d["b"] = 20
        assert d.keys() == ["a", "b", "c"]

    def test_delitem(self):
        d = SortedDict(sort_func=lambda k, v: k)
        d["a"] = 1
        d["b"] = 2
        del d["a"]
        assert d.keys() == ["b"]

    def test_update_value(self):
        d = SortedDict(sort_func=lambda k, v: v)
        d["a"] = 10
        d["a"] = 5  # update with smaller value
        assert d["a"] == 5

    def test_items(self):
        d = SortedDict(sort_func=lambda k, v: k)
        d["b"] = 2
        d["a"] = 1
        items = d.items()
        assert items == [("a", 1), ("b", 2)]

    def test_init_from_dict(self):
        d = SortedDict(sort_func=lambda k, v: k, init_dict={"b": 2, "a": 1})
        assert d.keys() == ["a", "b"]

    def test_iter(self):
        d = SortedDict(sort_func=lambda k, v: k)
        d["c"] = 3
        d["a"] = 1
        keys = list(d)
        assert keys == ["a", "c"]

    def test_repr(self):
        d = SortedDict(sort_func=lambda k, v: k)
        d["a"] = 1
        assert "SortedDict" in repr(d)
