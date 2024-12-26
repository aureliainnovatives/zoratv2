from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..controllers.agent_controller import AgentController
from ..schemas.agent_schema import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
    responses={404: {"description": "Not found"}},
)

agent_controller = AgentController()

@router.get("/")
async def index():
    """
    Index route for agent service.
    Returns a welcome message.
    """
    return await agent_controller.get_index()

@router.get("/home")
async def home():
    """
    Home route for agent service.
    Returns a home welcome message.
    """
    return await agent_controller.get_home()

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """
    Chat with the AI agent.
    
    Parameters:
    - user: The user's message
    
    Returns:
    - user: The original user message
    - assistant: The AI assistant's response
    """
    return await agent_controller.chat(chat_request)

@router.post("/chat/stream")
async def chat_stream(chat_request: ChatRequest):
    """
    Stream chat responses from the AI agent.
    
    Parameters:
    - user: The user's message
    
    Returns:
    - StreamingResponse: A stream of AI assistant's responses
    """
    return StreamingResponse(
        agent_controller.stream_chat(chat_request),
        media_type="text/event-stream"
    ) 