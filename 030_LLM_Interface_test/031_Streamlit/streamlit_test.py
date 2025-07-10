import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sidebar for model options
st.sidebar.header("Model Options")

# Model type selection
model_type = st.sidebar.radio(
    "Select Model Type",
    ["test1", "test2", "test3"],
    index=0
)

# Temperature slider
temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.05
)

# Top-k slider (for demonstration, not used by OpenAI API directly)
top_k = st.sidebar.slider(
    "Top-k (for sampling, if supported)",
    min_value=1,
    max_value=100,
    value=40,
    step=1
)

# Basemodel selection (OPENAI_MODEL_NAME)
default_model = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o")
model_choices = ["gpt-4o", "gpt-4o-mini", "o3-mini"]
basemodel = st.sidebar.selectbox(
    "Base Model (OPENAI_MODEL_NAME)",
    model_choices,
    index=model_choices.index(
        default_model) if default_model in model_choices else 0
)

# Update environment variable for OPENAI_MODEL_NAME
os.environ["OPENAI_MODEL_NAME"] = basemodel

# Streamlit UI


def create_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant that provides detailed and accurate responses."),
        ("human", "{input}")
    ])
    model = ChatOpenAI(
        temperature=temperature,
        model=basemodel,
        streaming=True
        # top_k is not supported by OpenAI, but you could pass it to other models
    )
    chain = (
        {"input": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return chain


chain = create_chain()

st.title("LLM Interface Test")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response (currently same for all model types)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        chain = create_chain()  # Re-create chain with current sidebar options
        for chunk in chain.stream(prompt):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
