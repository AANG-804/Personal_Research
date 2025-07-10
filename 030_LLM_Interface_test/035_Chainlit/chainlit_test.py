
import os
import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEFAULT_MODEL = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o")
DEFAULT_TEMPERATURE = 0.7


def create_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant that provides detailed and accurate responses. always say sir on the end of your response."),
        ("human", "{input}")
    ])
    model = ChatOpenAI(
        temperature=DEFAULT_TEMPERATURE,
        model=DEFAULT_MODEL,
        streaming=True
    )
    chain = (
        {"input": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return chain


@cl.on_chat_start
async def main():
    cl.user_session.set("chain", create_chain())
    cl.user_session.set("message_history", [])


@cl.on_message
async def handle_message(message: cl.Message):
    chain = cl.user_session.get("chain")
    message_history = cl.user_session.get("message_history")

    if message_history is None:
        message_history = []

    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")

    # LangChain의 astream을 사용하여 토큰 단위로 스트리밍
    full_response = ""
    async for chunk in chain.astream(message_history):
        full_response += chunk
        await msg.stream_token(chunk)

    # 최종 답변 저장 및 마무리
    message_history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("message_history", message_history)
    await msg.update()
