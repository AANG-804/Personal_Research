from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
from models.schemas import ChatRequest, ChatResponse, AgentRequest, AgentResponse
from services.llm_service import LLMService
from services.agent_service import AgentService
from langchain.schema import HumanMessage, AIMessage

router = APIRouter()
llm_service = LLMService()
agent_service = AgentService()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await llm_service.get_llm_response(request.prompt, request.model, request.messages)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        llm = llm_service.get_streaming_llm(request.model)

        # Convert messages to LangChain format
        lc_messages = []
        for msg in request.messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
        lc_messages.append(HumanMessage(content=request.prompt))

        async def token_generator():
            async for chunk in llm.astream(lc_messages):
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

        return StreamingResponse(token_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    try:
        agent_executor = agent_service.get_agent_executor()
        result = await agent_executor.ainvoke({
            "input": request.prompt,
            "chat_history": []
        })
        reasoning = "\n\n".join(
            [str(step) for step in result.get("intermediate_steps", [])])
        response = f"Reasoning steps:\n{reasoning}\n\nFinal answer: {result['output']}"
        return AgentResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/stream")
async def agent_stream(request: AgentRequest):
    try:
        agent_executor = agent_service.get_agent_executor()

        async def token_generator():
            # First, run the agent to get the full response
            result = await agent_executor.ainvoke({
                "input": request.prompt,
                "chat_history": []
            })

            # Format the response to include reasoning and final answer
            response_parts = []

            # Add intermediate steps with tool usage information
            for step in result.get("intermediate_steps", []):
                if isinstance(step, tuple) and len(step) == 2:
                    action, observation = step
                    if hasattr(action, 'tool'):
                        response_parts.append(f"Using tool: {action.tool}")
                        if hasattr(action, 'tool_input'):
                            response_parts.append(
                                f"Tool input: {action.tool_input}")
                        response_parts.append(f"Tool output: {observation}")

            # Add the final answer
            response_parts.append(f"\nFinal answer: {result['output']}")

            # Stream the formatted response
            response = "\n".join(response_parts)
            for char in response:
                yield char
                # Small delay to make streaming visible
                await asyncio.sleep(0.01)

        return StreamingResponse(token_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
