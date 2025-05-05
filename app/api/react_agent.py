import logging
import os
from logging.handlers import TimedRotatingFileHandler

from copilotkit import CopilotKitState
from copilotkit.langgraph import copilotkit_exit
from dotenv import find_dotenv, load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_community.llms.ollama import Ollama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from typing_extensions import Literal, Optional

import traceback
from .config import DEFAULT_MCP_CONFIG, MCPConfig

load_dotenv(find_dotenv())
    # os.environ[key] = value

"""
This is the main entry point for the agent.
It defines the workflow graph, state, tools, nodes and edges.
"""

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "log")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "agent.log")

logger = logging.getLogger("mcp_agent")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(LOG_FILE, when="W0", interval=1, backupCount=4, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)


def get_llm_model(llm_config: dict):
    """
    LLM 설정 정보를 받아 적절한 LLM 객체를 반환합니다.
    llm_config 예시:
    {
        "provider": "openai" 또는 "ollama",
        "api_key": "...",           # openai
        "model": "...",             # openai, ollama 공통
        "base_url": "...",          # openai, ollama 공통
        "temperature": 0.7,         # 선택
        ...
    }
    """
    provider = llm_config.get("provider")
    if provider == "openai":
        return ChatOpenAI(
            api_key=llm_config.get("api_key"),
            model=llm_config.get("model", "gpt-3.5-turbo"),
            base_url=llm_config.get("base_url"),
            temperature=llm_config.get("temperature", 0.7),
            streaming=True,
        )
    elif provider == "ollama":
        return Ollama(
            base_url=llm_config.get("base_url", "http://localhost:11434"),
            model=llm_config.get("model", "llama2"),
            temperature=llm_config.get("temperature", 0.7),
            streaming=True,
        )
    else:
        raise ValueError(f"지원하지 않는 LLM provider: {provider}")


class AgentState(CopilotKitState):
    """
    Here we define the state of the agent

    In this instance, we're inheriting from CopilotKitState, which will bring in
    the CopilotKitState fields. We're also adding a custom field, `mcp_config`,
    which will be used to configure MCP services for the agent.
    """
    # Define mcp_config as an optional field without skipping validation
    mcp_config: Optional[MCPConfig]
    llm_config: Optional[dict]

# Default MCP configuration to use when no configuration is provided in the state
# Uses relative paths that will work within the project structure


async def chat_node(state: AgentState, config: RunnableConfig) -> Command[Literal["__end__"]]:
    """
    This is a simplified agent that uses the ReAct agent as a subgraph.
    It handles both chat responses and tool execution in one node.
    """
    # Get MCP configuration from state, or use the default config if not provided
    mcp_config = state.get("mcp_config", DEFAULT_MCP_CONFIG)
    llm_config = state.get("llm_config", {})
    logger.info(f"mcp_config: {mcp_config}, default: {DEFAULT_MCP_CONFIG}")
    print(f"mcp_config: {mcp_config}, default: {DEFAULT_MCP_CONFIG}")
    try :
    # Set up the MCP client and tools using the configuration from state
        async with MultiServerMCPClient(mcp_config) as mcp_client:
            # Get the tools
            mcp_tools = mcp_client.get_tools()
            logger.info(f"mcp_tools: {mcp_tools}")

            # Create the react agent
            model = get_llm_model(llm_config)
            react_agent = create_react_agent(model, mcp_tools)

            # Prepare messages for the react agent
            agent_input = {
                "messages": state["messages"]
            }
            logger.info(f"agent_input: {agent_input}")

            # Run the react agent subgraph with our input
            agent_response = await react_agent.ainvoke(agent_input)

            # Update the state with the new messages
            updated_messages = state["messages"] + agent_response.get("messages", []) 
            await copilotkit_exit(config)
            # End the graph with the updated messages
            return Command(
                goto=END,
                update={"messages": updated_messages},
                )
    except Exception as e:
        logger.error(f"Error in chat_node: {e}")
        print(f"Error in chat_node: {e}")
        print(traceback.format_exc())
        raise e

# Define the workflow graph with only a chat node
workflow = StateGraph(AgentState)
workflow.add_node("chat_node", chat_node)
workflow.set_entry_point("chat_node")

# Compile the workflow graph
graph = workflow.compile(MemorySaver())
# graph = workflow.compile()