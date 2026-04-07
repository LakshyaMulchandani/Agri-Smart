import os
from typing import TypedDict, Annotated, Sequence, List
import operator
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    farm_id: str
    weather_data: dict = {}
    market_data: dict = {}
    next_node: str = ""

ACTUAL_PROJECT_ID = "agri-smart-492412"
llm = ChatVertexAI(model_name="gemini-2.5-flash", project=ACTUAL_PROJECT_ID, location="us-central1")

def field_agent(state: AgentState):
    """Expert in weather, soil, and crop health."""
    system_prompt = SystemMessage(content=(
        "You are the Agri-Smart Field Agent. Your ONLY job is to check weather. "
        "When a user asks about rain or weather, IMMEDIATELY call the fetch_weather tool. "
        "Assume the date is TODAY. Do not ask the user for dates or permission. "
        "Just call the tool and report the forecast."
    ))
    
    response = llm_with_tools.invoke([system_prompt] + state['messages'])
    return {"messages": [response]}

def market_agent(state: AgentState):
    """Expert in commodity pricing and market demand."""
    system_prompt = SystemMessage(content=(
        "You are the Agri-Smart Market Agent. Your job is to monitor crop prices "
        "and demand. If the Field Agent reports bad weather, calculate if selling "
        "crops immediately at current prices is better than waiting."
    ))
    
    messages = [system_prompt] + state['messages']
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response], "market_data": {"status": "price_checked"}}

def orchestrator(state: AgentState):
    """The Primary Agent that coordinates the workflow."""
    system_prompt = SystemMessage(content=(
        "You are the Orchestrator. If a user asks a question, delegate it to the "
        "Field Agent (weather) or Market Agent (prices). "
        "Once a sub-agent provides data from a tool, your job is to give the "
        "FINAL RECOMMENDATION to the farmer. Keep it professional and concise."
    ))
    
    response = llm.invoke([system_prompt] + state['messages'])
    return {"messages": [response]}

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

@tool
def fetch_weather(location: str):
    """Fetches real-time weather and soil moisture for a farm location."""
    return {
        "temp": 32,
        "humidity": 85,
        "forecast": "Heavy Rain & Potential Flooding",
        "soil_moisture": "High"
    }

@tool
def fetch_market_prices(crop_name: str):
    """Checks the current market price and demand trend for a specific crop."""
    return {
        "crop": crop_name,
        "current_price_per_kg": 28.50,
        "trend": "Dropping",
        "demand": "Low"
    }

tools = [fetch_weather, fetch_market_prices]
llm_with_tools = llm.bind_tools(tools)

def router(state: AgentState):
    """The traffic police that directs the workflow."""
    messages = state['messages']
    last_message = messages[-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    content = last_message.content.lower()
    
    if "forecast" in content or "weather" in content:
        return "orchestrator"

    if any(word in content for word in ["rain", "weather", "wheat"]):
        if "field agent:" not in content:
            return "field_agent"  
  
    return END

workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", orchestrator)
workflow.add_node("field_agent", field_agent)
workflow.add_node("market_agent", market_agent)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("orchestrator")

workflow.add_conditional_edges(
    "orchestrator",
    router,
    {"field_agent": "field_agent", "market_agent": "market_agent", "tools": "tools", "orchestrator": "orchestrator", END: END}
)

workflow.add_edge("field_agent", "orchestrator")
workflow.add_edge("market_agent", "orchestrator")
workflow.add_edge("tools", "orchestrator")

app_graph = workflow.compile()