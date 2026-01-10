from typing import Dict, Any
from app.core.tools.base import BaseTool, ToolResult
from app.tools.openalex_scholar import OpenAlexScholar
from app.utils.log_util import logger

class ScholarSearchTool(BaseTool):
    def __init__(self, scholar: OpenAlexScholar = None):
        self.name = "search_papers"
        self.description = "Search for papers using a query string."
        self.parameters = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The query string"}
            },
            "required": ["query"],
            "additionalProperties": False,
        }
        self.scholar = scholar

    async def execute(self, query: str) -> ToolResult:
        if not self.scholar:
            return ToolResult(content="Scholar client not initialized", is_error=True)

        try:
            papers = await self.scholar.search_papers(query)
            papers_str = self.scholar.papers_to_str(papers)
            logger.info(f"搜索文献结果\n{papers_str}")
            return ToolResult(content=papers_str, is_error=False)
        except Exception as e:
            error_msg = f"搜索文献失败: {str(e)}"
            logger.error(error_msg)
            return ToolResult(content=error_msg, is_error=True)
