# test_agent.py

from app.agent.graph import budget_graph
from langchain_core.messages import HumanMessage


def chat(message: str):
    result = budget_graph.invoke({"messages": [HumanMessage(content=message)]})
    # The last message is always the AI's final reply
    return result["messages"][-1].content


# Test it
print(chat("lunch 80 baht"))
print("---")
print(chat("set my budget for this month to 15000"))
print("---")
print(chat("how much have I spent this month?"))
