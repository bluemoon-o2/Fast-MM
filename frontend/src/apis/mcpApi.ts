import request from "@/utils/request";

export interface MCPServerConfig {
  name: str;
  type: "stdio" | "sse";
  command?: str;
  args?: string[];
  url?: str;
  env?: Record<string, string>;
  enabled: boolean;
}

export interface MCPServerStatus {
  name: str;
  config: MCPServerConfig;
  status: "connected" | "disconnected" | "error";
  tools: number;
}

export const getMCPServers = () => {
  return request.get<MCPServerStatus[]>("/mcp/servers");
};

export const addMCPServer = (data: MCPServerConfig) => {
  return request.post("/mcp/servers", data);
};

export const removeMCPServer = (name: str) => {
  return request.delete(`/mcp/servers/${name}`);
};

export const syncMCPTools = () => {
  return request.post("/mcp/sync");
};
