from typing import Dict, Any
from app.core.tools.base import BaseTool, ToolResult
from app.tools.base_interpreter import BaseCodeInterpreter

class CodeExecutionTool(BaseTool):
    def __init__(self, interpreter: BaseCodeInterpreter = None):
        self.name = "execute_code"
        self.description = (
            "This function allows you to execute Python code and retrieve the terminal output. "
            "If the code generates image output, the function will return the text '[image]'. "
            "The code is sent to a Jupyter kernel for execution. The kernel will remain active "
            "after execution, retaining all variables in memory."
        )
        self.parameters = {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The code text"}
            },
            "required": ["code"],
            "additionalProperties": False,
        }
        self.interpreter = interpreter

    async def execute(self, code: str) -> ToolResult:
        if not self.interpreter:
            return ToolResult(content="Code interpreter not initialized", is_error=True)

        text_to_gpt, error_occurred, error_message = await self.interpreter.execute_code(code)
        
        if error_occurred:
            return ToolResult(content=error_message, is_error=True)
        
        return ToolResult(content=text_to_gpt, is_error=False)
