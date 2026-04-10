"""Tests for cowagent.agent.protocol.result."""

from cowagent.agent.protocol.result import AgentResult, AgentActionType, ToolResult


class TestAgentResult:
    def test_success(self):
        r = AgentResult.success(final_answer="done", step_count=3)
        assert r.final_answer == "done"
        assert r.step_count == 3
        assert r.status == "success"
        assert not r.is_error
        assert r.error_message is None

    def test_error(self):
        r = AgentResult.error(error_message="failed", step_count=2)
        assert r.step_count == 2
        assert r.status == "error"
        assert r.is_error
        assert "failed" in r.final_answer
        assert r.error_message == "failed"

    def test_error_defaults_step_count(self):
        r = AgentResult.error(error_message="oops")
        assert r.step_count == 0

    def test_direct_init(self):
        r = AgentResult(
            final_answer="answer",
            step_count=1,
            status="error",
            error_message="test",
        )
        assert r.is_error


class TestToolResult:
    def test_basic(self):
        r = ToolResult(
            tool_name="read",
            input_params={"file": "test.txt"},
            output="content",
            status="success",
        )
        assert r.tool_name == "read"
        assert r.input_params == {"file": "test.txt"}
        assert r.output == "content"
        assert r.status == "success"
        assert r.error_message is None
        assert r.execution_time == 0.0

    def test_error_result(self):
        r = ToolResult(
            tool_name="bash",
            input_params={"cmd": "ls"},
            output=None,
            status="error",
            error_message="command failed",
            execution_time=1.5,
        )
        assert r.status == "error"
        assert r.execution_time == 1.5
