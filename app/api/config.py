# from langchain_mcp_adapters.client import MCPConfig
import os
from typing_extensions import TypedDict, List, Literal, Dict, Union

# Define the connection type structures
class StdioConnection(TypedDict):
    command: str
    args: List[str]
    transport: Literal["stdio"]
    envs: List[str]

class SSEConnection(TypedDict):
    url: str
    transport: Literal["sse"]
    envs: List[str]
# Type for MCP configuration
MCPConfig = Dict[str, Union[StdioConnection, SSEConnection]]

DEFAULT_LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "base_url": "https://api.openai.com/v1",
    "temperature": 0.7,
}

DEFAULT_MCP_CONFIG: MCPConfig = {
    "math": {
        "command": "python",
        # Use a relative path that will be resolved based on the current working directory
        "args": [os.path.join(os.path.dirname(__file__), "math_server.py")],
        "transport": "stdio",
    },
}