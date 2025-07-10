# app.py
import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from typing import cast

# 채팅 세션 시작 시 한 번만 실행


@cl.on_chat_start
async def on_chat_start():
    # 스트리밍 가능한 LLM 설정
    model = ChatOpenAI(streaming=True)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{question}"),
    ])
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

# 사용자가 메시지를 보낼 때마다 실행


@cl.on_message
async def on_message(message: cl.Message):
    # 저장해둔 Runnable 꺼내기
    runnable = cast(Runnable, cl.user_session.get("runnable"))

    # 빈 메시지 객체로 스트리밍 준비
    msg = cl.Message(content="")

    # stream_final_answer=False인 경우 최종 답변도 콜백으로 처리됨
    async for token in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()])
    ):
        await msg.stream_token(token)  # UI에 토큰 단위로 전송

    await msg.send()  # 최종 메시지 전송
