# app/agent/graph.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import TypedDict, Annotated
from datetime import date
import operator

from app.agent.agent import tools, get_llm
from app.agent.prompts import SYSTEM_PROMPT


# ── State ────────────────────────────────────────────────────────────────────
# This is what gets passed between every node in the graph
# "messages" holds the full conversation history
# Annotated[list, operator.add] means: each step ADDS to the list, not replaces it


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]


# ── Nodes ────────────────────────────────────────────────────────────────────
# A "node" is just a function that:
# - receives the current state
# - does something
# - returns an update to the state


def agent_node(state: AgentState) -> dict:
    """
    The main thinking node.
    The LLM reads all messages and either:
    - Calls a tool (if it needs data)
    - Replies directly (if it can answer without tools)
    """
    today = date.today()

    # Build the system prompt with today's date filled in
    system_prompt = SYSTEM_PROMPT.format(
        today=today.strftime("%Y-%m-%d"),
        current_month=today.strftime("%B"),
        year=today.year,
        month_num=f"{today.month:02d}",
    )

    llm = get_llm()

    # Bind tools to the LLM so it knows what it can call
    llm_with_tools = llm.bind_tools(tools)

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """
    Router function — decides what happens next.

    After the LLM responds, check:
    - Did the LLM want to call a tool? → go to "tools" node
    - Did the LLM just reply normally? → we're done, go to END
    """
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"  # LLM wants to call a tool

    return END  # LLM gave a final answer


# ── Build the Graph ──────────────────────────────────────────────────────────


def build_graph():
    # ToolNode automatically runs whatever tool the LLM asked for
    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Set entry point — always start at agent
    graph.set_entry_point("agent")

    # Add edges (connections between nodes)
    # After agent runs → check should_continue to decide where to go
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # if tools needed → go to tools node
            END: END,  # if done → end
        },
    )

    # After tools run → always go back to agent
    # So the LLM can read the tool result and form a reply
    graph.add_edge("tools", "agent")

    return graph.compile()


# The compiled graph — import this everywhere you need it
budget_graph = build_graph()
