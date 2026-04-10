"""Tests for cowagent.agent.protocol.task."""

import time
from cowagent.agent.protocol.task import Task, TaskType, TaskStatus


class TestTaskType:
    def test_values(self):
        assert TaskType.TEXT.value == "text"
        assert TaskType.IMAGE.value == "image"
        assert TaskType.VIDEO.value == "video"


class TestTaskStatus:
    def test_values(self):
        assert TaskStatus.INIT.value == "init"
        assert TaskStatus.PROCESSING.value == "processing"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"


class TestTask:
    def test_defaults(self):
        t = Task()
        assert t.content == ""
        assert t.type == TaskType.TEXT
        assert t.status == TaskStatus.INIT
        assert t.id is not None
        assert t.metadata == {}
        assert t.images == []

    def test_with_content(self):
        t = Task(content="hello world")
        assert t.content == "hello world"

    def test_custom_type(self):
        t = Task(content="img", type=TaskType.IMAGE)
        assert t.type == TaskType.IMAGE

    def test_custom_id(self):
        t = Task(content="test", id="my-id")
        assert t.id == "my-id"

    def test_get_text(self):
        t = Task(content="some text")
        assert t.get_text() == "some text"

    def test_update_status(self):
        t = Task(content="test")
        old_time = t.updated_at
        time.sleep(0.01)
        t.update_status(TaskStatus.COMPLETED)
        assert t.status == TaskStatus.COMPLETED
        assert t.updated_at > old_time

    def test_metadata(self):
        t = Task(content="test", metadata={"key": "value"})
        assert t.metadata["key"] == "value"

    def test_media_fields(self):
        t = Task(
            content="media",
            images=["img1.png"],
            videos=["vid1.mp4"],
            audios=["aud1.mp3"],
            files=["doc.pdf"],
        )
        assert t.images == ["img1.png"]
        assert t.videos == ["vid1.mp4"]
        assert t.audios == ["aud1.mp3"]
        assert t.files == ["doc.pdf"]

    def test_unique_ids(self):
        t1 = Task()
        t2 = Task()
        assert t1.id != t2.id
