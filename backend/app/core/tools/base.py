from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    content: str
    is_error: bool = False
    metadata: Optional[Dict[str, Any]] = None

class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema for parameters

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with the given arguments."""
        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert tool definition to OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "strict": True
            }
        }
