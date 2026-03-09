# app/ui/streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from langchain_core.messages import HumanMessage

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.agent.graph import budget_graph
from app.tools.expense_tools import (
    get_monthly_spending,
    get_spending_by_category,
    get_recent_expenses,
)
from app.tools.budget_tools import get_remaining_budget

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Budget Assistant", page_icon="💰", layout="wide")

# ── Session state ─────────────────────────────────────────────────────────────
# Session state persists data across reruns within the same browser session
# Every time user sends a message, Streamlit reruns the whole script
# Without session_state, chat history would be lost on every rerun

if "messages" not in st.session_state:
    st.session_state.messages = []  # chat history for display

if "graph_messages" not in st.session_state:
    st.session_state.graph_messages = []  # messages passed to LangGraph


# ── Helper ───────────────────────────────────────────────────────────────────
def chat(user_input: str) -> str:
    """Send a message to the agent and get a response."""
    st.session_state.graph_messages.append(HumanMessage(content=user_input))

    result = budget_graph.invoke({"messages": st.session_state.graph_messages})

    # Update graph messages with full result (includes tool calls etc.)
    st.session_state.graph_messages = result["messages"]

    # Return just the final text reply
    return result["messages"][-1].content


# ── Layout ───────────────────────────────────────────────────────────────────
st.title("💰 AI Budget Assistant")

# Two columns: chat on left, dashboard on right
chat_col, dashboard_col = st.columns([1.2, 1])


# ── LEFT: Chat ───────────────────────────────────────────────────────────────
with chat_col:
    st.subheader("Chat")

    # Display all past messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input at the bottom
    user_input = st.chat_input("Type an expense or ask a question...")

    if user_input:
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat(user_input)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to refresh dashboard with new data
        st.rerun()


# ── RIGHT: Dashboard ─────────────────────────────────────────────────────────
with dashboard_col:
    st.subheader("Dashboard")

    today = date.today()
    year = today.year
    month = today.month
    month_name = today.strftime("%B %Y")

    # ── Budget summary cards ──────────────────────────────────────────────
    remaining = get_remaining_budget(year, month)

    if remaining["success"]:
        budget = remaining["budget"]
        spent = remaining["total_spent"]
        left = remaining["remaining"]
        percent_used = (spent / budget * 100) if budget > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Budget", f"฿{budget:,.0f}")
        col2.metric("Spent", f"฿{spent:,.0f}")

        # Show remaining — red if over budget, green if under
        col3.metric(
            "Remaining",
            f"฿{left:,.0f}",
            delta=f"{left:,.0f}",
            delta_color="normal" if left >= 0 else "inverse",
        )

        # Progress bar
        st.caption(f"{month_name} — {percent_used:.1f}% of budget used")
        st.progress(min(percent_used / 100, 1.0))

    else:
        st.info("💡 No budget set yet. Tell me: 'My budget this month is ฿15,000'")

    st.divider()

    # ── Spending by category chart ────────────────────────────────────────
    category_data = get_spending_by_category(year, month)
    breakdown = category_data.get("breakdown", {})

    if breakdown:
        st.caption(f"Spending by Category — {month_name}")
        df = pd.DataFrame(
            list(breakdown.items()), columns=["Category", "Amount"]
        ).sort_values("Amount", ascending=False)

        fig = px.pie(
            df,
            values="Amount",
            names="Category",
            hole=0.4,  # donut style
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=280,
            showlegend=True,
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No expenses recorded this month yet.")

    st.divider()

    # ── Recent expenses table ─────────────────────────────────────────────
    st.caption("Recent Expenses")
    recent = get_recent_expenses(limit=8)
    expenses = recent.get("expenses", [])

    if expenses:
        df_recent = pd.DataFrame(expenses)[
            ["date", "category", "description", "amount"]
        ]
        df_recent["amount"] = df_recent["amount"].apply(lambda x: f"฿{x:,.0f}")
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.caption("No expenses yet.")
