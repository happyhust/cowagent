"""Tests for cowagent.common.dequeue."""

from queue import Full
from cowagent.common.dequeue import Dequeue


class TestDequeue:
    def test_put_and_get(self):
        q = Dequeue(maxsize=10)
        q.put(1)
        q.put(2)
        assert q.get() == 1
        assert q.get() == 2

    def test_putleft(self):
        q = Dequeue(maxsize=10)
        q.put(1)
        q.putleft(0)
        assert q.get() == 0
        assert q.get() == 1

    def test_putleft_nowait(self):
        q = Dequeue(maxsize=10)
        q.putleft_nowait(1)
        assert q.get() == 1

    def test_putleft_raises_full(self):
        q = Dequeue(maxsize=1)
        q.put(1)
        try:
            q.putleft(2, block=False)
            assert False, "Should have raised Full"
        except Full:
            pass

    def test_putleft_nowait_raises_full(self):
        q = Dequeue(maxsize=1)
        q.put(1)
        try:
            q.putleft_nowait(2)
            assert False, "Should have raised Full"
        except Full:
            pass

    def test_putleft_timeout_negative(self):
        q = Dequeue(maxsize=1)
        q.put(1)
        try:
            q.putleft(2, block=True, timeout=-1)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_qsize(self):
        q = Dequeue(maxsize=10)
        q.put(1)
        q.put(2)
        assert q.qsize() == 2

    def test_empty(self):
        q = Dequeue(maxsize=10)
        assert q.empty()
        q.put(1)
        assert not q.empty()

    def test_full(self):
        q = Dequeue(maxsize=2)
        q.put(1)
        q.put(2)
        assert q.full()

    def test_order_after_mixed_put_putleft(self):
        q = Dequeue(maxsize=10)
        q.put(1)
        q.putleft(0)
        q.put(2)
        q.putleft(-1)
        result = [q.get() for _ in range(4)]
        assert result == [-1, 0, 1, 2]
