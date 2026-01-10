from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.mcp_manager import mcp_manager
from app.utils.log_util import logger

router = APIRouter(prefix="/mcp", tags=["mcp"])

class MCPServerConfig(BaseModel):
    name: str
    type: str # "stdio" or "sse"
    command: Optional[str] = None
    args: Optional[List[str]] = []
    url: Optional[str] = None
    env: Optional[Dict[str, str]] = {}
    enabled: bool = True

class MCPServerStatus(BaseModel):
    name: str
    config: MCPServerConfig
    status: str # "connected", "disconnected", "error"
    tools: int

@router.get("/servers", response_model=List[MCPServerStatus])
async def list_servers():
    result = []
    config = mcp_manager.config.get("servers", {})
    
    for name, cfg in config.items():
        is_connected = name in mcp_manager.sessions
        status = "connected" if is_connected else "disconnected"
        
        # Count tools if connected (this is a bit inefficient, but okay for now)
        # Ideally mcp_manager should cache tool counts
        tool_count = 0
        # TODO: Get actual tool count from registry or manager cache
        
        result.append(MCPServerStatus(
            name=name,
            config=MCPServerConfig(name=name, **cfg),
            status=status,
            tools=tool_count
        ))
    return result

@router.post("/servers")
async def add_server(server: MCPServerConfig):
    config_dict = server.model_dump(exclude={"name"})
    
    # Update config
    if "servers" not in mcp_manager.config:
        mcp_manager.config["servers"] = {}
    
    mcp_manager.config["servers"][server.name] = config_dict
    mcp_manager.save_config()
    
    # Try to connect
    if server.enabled:
        try:
            await mcp_manager.connect_server(server.name, config_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Server added but failed to connect: {str(e)}")
            
    return {"message": "Server added successfully"}

@router.delete("/servers/{name}")
async def remove_server(name: str):
    if name not in mcp_manager.config.get("servers", {}):
        raise HTTPException(status_code=404, detail="Server not found")
        
    # Remove from config
    del mcp_manager.config["servers"][name]
    mcp_manager.save_config()
    
    # TODO: Disconnect session if active
    # Currently MCPManager doesn't support individual disconnect nicely without full cleanup
    # For now, we just leave it until restart or implement disconnect in manager
    
    return {"message": "Server removed"}

@router.post("/sync")
async def sync_tools():
    await mcp_manager.sync_tools()
    return {"message": "Tools synced"}
