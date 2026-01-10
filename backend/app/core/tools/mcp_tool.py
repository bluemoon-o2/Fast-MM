from typing import Any, Dict
from mcp import ClientSession
from app.core.tools.base import BaseTool, ToolResult
from app.utils.log_util import logger

class MCPToolAdapter(BaseTool):
    def __init__(
        self, 
        name: str, 
        description: str, 
        input_schema: Dict[str, Any],
        session: ClientSession
    ):
        self.name = name
        self.description = description
        self.parameters = input_schema
        self.session = session

    async def execute(self, **kwargs) -> ToolResult:
        try:
            # MCP SDK expects arguments as a dictionary
            result = await self.session.call_tool(self.name, arguments=kwargs)
            
            # MCP result content is a list of TextContent or ImageContent
            # We need to serialize it back to string for the LLM
            content_str = ""
            for content in result.content:
                if content.type == "text":
                    content_str += content.text
                elif content.type == "image":
                    content_str += f"[Image: {content.mimeType}]"
                elif content.type == "resource":
                    content_str += f"[Resource: {content.uri}]"
            
            return ToolResult(content=content_str, is_error=result.isError)
        except Exception as e:
            logger.error(f"MCP Tool execution failed: {str(e)}")
            return ToolResult(content=str(e), is_error=True)
