import asyncio
import json
import os
from typing import Dict, Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from app.core.tools.registry import tool_registry
from app.core.tools.mcp_tool import MCPToolAdapter
from app.utils.log_util import logger
from app.config.setting import settings

MCP_CONFIG_FILE = os.path.join(settings.WORK_DIR, "mcp_config.json")

class MCPManager:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(MCP_CONFIG_FILE):
            try:
                with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load MCP config: {e}")
                return {"servers": {}}
        return {"servers": {}}

    def save_config(self):
        os.makedirs(os.path.dirname(MCP_CONFIG_FILE), exist_ok=True)
        with open(MCP_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    async def connect_server(self, name: str, config: Dict[str, Any]):
        if name in self.sessions:
            logger.info(f"MCP Server {name} already connected.")
            return

        server_type = config.get("type")
        
        try:
            if server_type == "stdio":
                command = config.get("command")
                args = config.get("args", [])
                env = config.get("env", None)
                
                params = StdioServerParameters(
                    command=command,
                    args=args,
                    env=env
                )
                
                # We need to maintain the connection context
                read, write = await self.exit_stack.enter_async_context(stdio_client(params))
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                self.sessions[name] = session
                logger.info(f"Connected to Stdio MCP Server: {name}")

            elif server_type == "sse":
                url = config.get("url")
                # TODO: Implement SSE support
                # transport = await self.exit_stack.enter_async_context(sse_client(url))
                # session = await self.exit_stack.enter_async_context(ClientSession(transport.read, transport.write))
                # await session.initialize()
                # self.sessions[name] = session
                logger.warning(f"SSE MCP Server type not yet fully implemented: {name}")
                
            else:
                logger.error(f"Unknown MCP server type: {server_type}")
                return

            # Sync tools immediately after connection
            await self.sync_tools(name)

        except Exception as e:
            logger.error(f"Failed to connect to MCP server {name}: {e}")
            raise e

    async def sync_tools(self, server_name: str = None):
        """Sync tools from one or all servers to the registry."""
        servers_to_sync = [server_name] if server_name else self.sessions.keys()
        
        for name in servers_to_sync:
            session = self.sessions.get(name)
            if not session:
                continue
            
            try:
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    # Create adapter
                    # Note: MCP tool names might collide, maybe prefix them? 
                    # For now, we use raw names as per opencode behavior
                    adapter = MCPToolAdapter(
                        name=tool.name,
                        description=tool.description,
                        input_schema=tool.inputSchema,
                        session=session
                    )
                    tool_registry.register(adapter)
                    logger.info(f"Registered MCP tool: {tool.name} from server {name}")
            except Exception as e:
                logger.error(f"Failed to list tools from {name}: {e}")

    async def initialize(self):
        """Connect to all configured servers on startup."""
        for name, config in self.config.get("servers", {}).items():
            if config.get("enabled", True):
                try:
                    await self.connect_server(name, config)
                except Exception as e:
                    logger.error(f"Startup connection failed for {name}: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()

# Global instance
mcp_manager = MCPManager()
