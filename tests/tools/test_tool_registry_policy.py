import asyncio

import pytest

from tools.base_tool import BaseTool
from tools.tool_registry import ToolOutputTooLargeError, ToolRegistry, ToolTimeoutError


class EchoTool(BaseTool):
    @property
    def name(self) -> str:
        return "Echo"

    @property
    def description(self) -> str:
        return "Echoes text"

    async def execute(self, assistant, **kwargs):
        return kwargs.get("text", "ok")


class SlowTool(EchoTool):
    @property
    def name(self) -> str:
        return "Slow"

    async def execute(self, assistant, **kwargs):
        await asyncio.sleep(0.05)
        return "late"


def test_tool_registry_blocks_tools_outside_allowlist():
    registry = ToolRegistry(assistant=object(), allowed_tools={"Echo"})
    registry.register_tool(EchoTool())

    with pytest.raises(PermissionError):
        registry.get_tool_policy().validate_allowed("Quiz_Generator")


@pytest.mark.asyncio
async def test_tool_registry_enforces_timeout():
    registry = ToolRegistry(assistant=object(), tool_timeout_seconds=0.001)
    registry.register_tool(SlowTool())

    with pytest.raises(ToolTimeoutError):
        await registry.execute_tool("Slow")


@pytest.mark.asyncio
async def test_tool_registry_rejects_oversized_output():
    registry = ToolRegistry(assistant=object(), tool_output_max_chars=4)
    registry.register_tool(EchoTool())

    with pytest.raises(ToolOutputTooLargeError):
        await registry.execute_tool("Echo", text="too large")
