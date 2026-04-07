import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from app.agents import app_graph  # This imports your LangGraph 'brain'
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AgentLog(Base):
    __tablename__ = "agent_logs"
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String)
    action_taken = Column(String)
    reasoning_process = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class QueryRequest(BaseModel):
    message: str
    farm_id: str = "default_farm"

app = FastAPI(title="Agri-Smart API")

@app.post("/orchestrate")
async def orchestrate_request(request: QueryRequest):
    try:
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "farm_id": request.farm_id
        }
        
        result = await app_graph.ainvoke(initial_state)
        
        final_answer = ""
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.content.strip() and not msg.tool_calls:
                final_answer = msg.content
                break

        return {
            "status": "success",
            "agent_response": final_answer,
            "session_id": request.farm_id
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/")
def read_root():
    return {"message": "Agri-Smart Multi-Agent API is LIVE"}