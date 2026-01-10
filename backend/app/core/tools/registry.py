from typing import Dict, List, Optional, Type
from app.core.tools.base import BaseTool
from app.utils.log_util import logger

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """Register a tool instance."""
        if tool.name in self._tools:
            logger.warning(f"Tool {tool.name} already registered. Overwriting.")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_openai_tools(self) -> List[Dict]:
        """Get all registered tools in OpenAI format."""
        return [tool.to_openai_schema() for tool in self._tools.values()]

    async def execute_tool(self, name: str, arguments: Dict) -> Dict:
        """Execute a tool by name and arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        
        result = await tool.execute(**arguments)
        return {
            "content": result.content,
            "is_error": result.is_error,
            "metadata": result.metadata
        }

# Global registry instance
tool_registry = ToolRegistry()
