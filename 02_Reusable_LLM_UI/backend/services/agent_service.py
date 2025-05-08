from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_API_KEY, TAVILY_API_KEY


class AgentService:
    def __init__(self):
        self.search_tool = TavilySearchResults(api_key=TAVILY_API_KEY)
        self.tools = [self.search_tool]
        self.agent_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful research assistant. You have access to a search tool that can find real-time information. Always use the search tool when you need current information or facts. Show your reasoning and the search results you used."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])

    def get_agent_executor(self):
        if not OPENAI_API_KEY:
            raise Exception("Missing OpenAI API key.")
        llm = ChatOpenAI(model="gpt-4", api_key=OPENAI_API_KEY, temperature=0)
        agent = create_openai_tools_agent(llm, self.tools, self.agent_prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
