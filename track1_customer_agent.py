"""
Orbit Support — AI Customer-Facing Agent (Track 1 Codelab)
Run: streamlit run app.py
Requires: ANTHROPIC_API_KEY environment variable
"""

import os
import streamlit as st
from anthropic import Anthropic

st.set_page_config(page_title="Orbit Support — AI Agent", page_icon="🛰️", layout="centered")

# ---------- Setup ----------
api_key = os.environ.get("ANTHROPIC_API_KEY")

with st.sidebar:
    st.markdown("### ⚙️ Setup")
    if not api_key:
        api_key = st.text_input("Anthropic API Key", type="password",
                                 help="Set ANTHROPIC_API_KEY env var, or paste it here for this session.")
    st.markdown("---")
    st.markdown("**Simulated store policies**")
    st.caption("Delivery: 4–6 days standard, 1–2 express\n\nReturns: 15 days, unused, original packaging\n\nDamaged item: free replacement/refund, pickup in 48h\n\nAddress change: only before shipping")
    if st.button("Reset conversation"):
        st.session_state.messages = []
        st.rerun()

SYSTEM_PROMPT = """
You are "Orbit Support", the customer support AI agent for an online electronics store called Orbit.
Store policies you must follow strictly:
- Standard delivery: 4-6 business days. Express: 1-2 business days.
- Returns accepted within 15 days of delivery, item must be unused and in original packaging. Refund issued in 5-7 business days after pickup.
- Damaged or wrong item: customer gets free replacement or full refund, no return shipping cost, pickup arranged within 48 hours.
- Order tracking: if no order ID given, ask for one. You don't have a real database — for status, generate a plausible but clearly fictional status and mention it's simulated for this demo.
- Address changes only possible before the order ships. Once shipped, cannot be changed.
- Be warm, concise (3-5 sentences max), and end with a helpful next step or question if relevant.
- Never invent policies outside what's given above.
"""

st.title("🛰️ Orbit Support")
st.caption("AI customer-facing agent · Track 1 Codelab")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm the Orbit Support agent. I can help with order tracking, returns, damaged items, or address changes. What's going on?"}
    ]

# ---------- Quick prompts ----------
cols = st.columns(4)
quick_prompts = [
    "Where is my order #4821?",
    "What is your return policy?",
    "My item arrived damaged",
    "Can I change my delivery address?",
]
clicked_prompt = None
for c, qp in zip(cols, quick_prompts):
    if c.button(qp, use_container_width=True):
        clicked_prompt = qp

# ---------- Render history ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------- Handle input ----------
user_input = st.chat_input("Ask about your order, returns, or anything else...")
final_input = clicked_prompt or user_input

if final_input:
    if not api_key:
        st.error("Please provide your Anthropic API key in the sidebar first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.write(final_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            )
            reply = "".join(block.text for block in response.content if block.type == "text")
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
