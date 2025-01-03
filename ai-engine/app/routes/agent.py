from fastapi import APIRouter, Query
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
async def chat(
    chat_request: ChatRequest,
    session_id: str = Query(default="default_session", description="Session ID for the chat")
):
    """
    Chat with an AI agent.
    
    Parameters:
    - chat_request: The chat request containing the user's message, agent_id and optional llm_name
    - session_id: Session ID for the chat (defaults to 'default_session' if not provided)
    
    Returns:
    - user: The original user message
    - assistant: The AI assistant's response
    - llm_used: The LLM used for the response
    """
    return await agent_controller.chat(chat_request.agent_id, session_id, chat_request)

@router.post("/chat/stream")
async def chat_stream(
    chat_request: ChatRequest,
    session_id: str = Query(default="default_session", description="Session ID for the chat")
):
    """
    Stream chat responses from an AI agent.
    
    Parameters:
    - chat_request: The chat request containing the user's message, agent_id and optional llm_name
    - session_id: Session ID for the chat (defaults to 'default_session' if not provided)
    
    Returns:
    - StreamingResponse: A stream of AI assistant's responses
    """
    return StreamingResponse(
        agent_controller.stream_chat(chat_request.agent_id, session_id, chat_request),
        media_type="text/event-stream"
    ) 