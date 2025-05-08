from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_cohere import ChatCohere
from langchain_core.messages import AIMessage, HumanMessage
from typing import List, Dict, Optional
from config.settings import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    COHERE_API_KEY,
    MODEL_PROVIDER_MAP
)


class LLMService:
    @staticmethod
    async def get_llm_response(prompt: str, model: str, messages: List[Dict] = None) -> str:
        provider = MODEL_PROVIDER_MAP.get(model)
        if not provider:
            raise Exception(f"Model '{model}' is not supported.")

        try:
            if provider == "openai":
                if not OPENAI_API_KEY:
                    raise Exception("Missing OpenAI API key.")
                llm = ChatOpenAI(model=model, api_key=OPENAI_API_KEY)
            elif provider == "anthropic":
                if not ANTHROPIC_API_KEY:
                    raise Exception("Missing Anthropic API key.")
                llm = ChatAnthropic(model=model, api_key=ANTHROPIC_API_KEY)
            elif provider == "cohere":
                if not COHERE_API_KEY:
                    raise Exception("Missing Cohere API key.")
                llm = ChatCohere(model=model, api_key=COHERE_API_KEY)

            # Convert messages to LangChain format
            lc_messages = []
            if messages:
                for msg in messages:
                    if msg["role"] == "user":
                        lc_messages.append(
                            HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        lc_messages.append(AIMessage(content=msg["content"]))
            lc_messages.append(HumanMessage(content=prompt))

            result = await llm.ainvoke(lc_messages)
            return result.content if hasattr(result, "content") else str(result)
        except Exception as e:
            raise Exception(f"Error in {provider} model: {str(e)}")

    @staticmethod
    def get_streaming_llm(model: str, streaming: bool = True):
        provider = MODEL_PROVIDER_MAP.get(model)
        if not provider:
            raise Exception(f"Model '{model}' is not supported.")

        if provider == "openai":
            if not OPENAI_API_KEY:
                raise Exception("Missing OpenAI API key.")
            return ChatOpenAI(model=model, api_key=OPENAI_API_KEY, streaming=streaming)
        elif provider == "anthropic":
            if not ANTHROPIC_API_KEY:
                raise Exception("Missing Anthropic API key.")
            return ChatAnthropic(model=model, api_key=ANTHROPIC_API_KEY, streaming=streaming)
        elif provider == "cohere":
            if not COHERE_API_KEY:
                raise Exception("Missing Cohere API key.")
            return ChatCohere(model=model, api_key=COHERE_API_KEY, streaming=streaming)
