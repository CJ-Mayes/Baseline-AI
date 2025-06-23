from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Dict, Any

# Import your existing components
from langsmith import Client
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa
from utilities.prompt import AGENT_SYSTEM_PROMPT
from by_pass import is_bypass_enabled, get_mock_response

# Load environment variables
load_dotenv()

# Add LangSmith tracing
langsmith_client = Client()

config: Dict[str, Any] = {
    "run_name": "Tableau Langchain Web_App.py"
}

# Create FastAPI app
app = FastAPI(title="Tableau AI Chat", description="Simple AI chat interface for Tableau data")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files with proper caching
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Initialize your agent (same as your original code)
def setup_agent():
    """Initialize the Tableau LangChain agent"""
    
    # Initialize the Tableau data source tool
    analyze_datasource = initialize_simple_datasource_qa(
        domain=os.environ['TABLEAU_DOMAIN'],
        site=os.environ['TABLEAU_SITE'],
        jwt_client_id=os.environ['TABLEAU_JWT_CLIENT_ID'],
        jwt_secret_id=os.environ['TABLEAU_JWT_SECRET_ID'],
        jwt_secret=os.environ['TABLEAU_JWT_SECRET'],
        tableau_api_version=os.environ['TABLEAU_API_VERSION'],
        tableau_user=os.environ['TABLEAU_USER'],
        datasource_luid=os.environ['DATASOURCE_LUID'],
        tooling_llm_model="gpt-4.1-nano",
        model_provider="openai"
    )

    # Create the agent
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    tools = [analyze_datasource]

    return create_react_agent(
        model=llm, 
        tools=tools,
        prompt=AGENT_SYSTEM_PROMPT
    )

# Initialize agent once when app starts
agent = setup_agent()

@app.get("/")
async def home():
    """Serve the main HTML page"""
    return FileResponse('static/index.html', headers={"Cache-Control": "no-cache"})

@app.get("/index.html")
async def static_index():
    return FileResponse('static/index.html', headers={"Cache-Control": "no-cache"})

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat messages - this is where the AI magic happens"""
    try:
        # Check if OpenAI bypass is enabled
        if is_bypass_enabled():
            # Return a mock response instead of calling OpenAI
            response_text = get_mock_response()
            return ChatResponse(response=response_text)
        
        # Use your existing agent logic
        messages = {"messages": [("user", request.message)]}
        
        # Get response from agent
        response_text = ""
        for chunk in agent.stream(messages, config=config, stream_mode="values"):
            if 'messages' in chunk and chunk['messages']:
                latest_message = chunk['messages'][-1]
                if hasattr(latest_message, 'content'):
                    response_text = latest_message.content
        
        return ChatResponse(response=response_text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["static", "templates"],
        reload_delay=1
    )