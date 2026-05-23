# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

#Step1: Setup API Keys for Groq, OpenAI and Tavily
import os

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY=os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")

#Step2: Setup LLM & Tools
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

openai_llm=ChatOpenAI(model="gpt-4o-mini")
groq_llm=ChatGroq(model="llama-3.3-70b-versatile")

search_tool=TavilySearchResults(max_results=2)

#Step3: Setup AI Agent with Search tool functionality
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage

system_prompt="Act as an AI chatbot who is smart and friendly"

def get_response_from_ai_agent(llm_id, query, allow_search, system_prompt, provider):
    if provider=="Groq":
        llm=ChatGroq(model=llm_id)
    elif provider=="OpenAI":
        llm=ChatOpenAI(model=llm_id)
    tools = [TavilySearchResults(max_results=2)] if allow_search else []

    # Try creating the agent with a state modifier if supported; fall back to no modifier.
    try:
        agent = create_react_agent(model=llm, tools=tools, state_modifier=system_prompt)
        use_state_modifier = True
    except TypeError:
        try:
            agent = create_react_agent(model=llm, tools=tools)
            use_state_modifier = False
        except Exception as e:
            return f"ERROR: failed to create agent: {e}"

    # Build state: if the agent accepted a state modifier, only send the user message;
    # otherwise, prepend the system prompt as a system message in the state.
    try:
        if use_state_modifier:
            state = {"messages": [("user", query)]}
        else:
            state = {"messages": [("system", system_prompt), ("user", query)]}

        response = agent.invoke(state)
        messages = response.get("messages") or []
        ai_messages = [message.content for message in messages if isinstance(message, AIMessage)]
        return ai_messages[-1] if ai_messages else "No response generated."
    except Exception as exc:
        return f"ERROR: agent invocation failed: {exc}"