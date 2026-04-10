"""Tests for cowagent.common.singleton."""

from cowagent.common.singleton import singleton


class TestSingleton:
    def test_same_instance(self):
        @singleton
        class Service:
            def __init__(self):
                self.value = 42

        a = Service()
        b = Service()
        assert a is b

    def test_args_ignored_after_first(self):
        @singleton
        class Configurable:
            def __init__(self, name="default"):
                self.name = name

        a = Configurable(name="first")
        b = Configurable(name="second")
        assert a.name == "first"
        assert b.name == "first"
        assert a is b

    def test_different_classes_different_instances(self):
        @singleton
        class A:
            pass

        @singleton
        class B:
            pass

        assert A() is not B()
