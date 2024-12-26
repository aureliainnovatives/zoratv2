from ..services.agent_service import AgentService
from ..schemas.agent_schema import ChatRequest, ChatResponse
import json

class AgentController:
    def __init__(self):
        pass
    
    async def get_index(self) -> str:
        """Get index message"""
        return await AgentService.get_index_message()
    
    async def get_home(self) -> str:
        """Get home message"""
        return await AgentService.get_home_message()
    
    async def chat(self, chat_request: ChatRequest) -> ChatResponse:
        """Process chat request"""
        response, llm_used = await AgentService.process_chat(
            user_message=chat_request.user,
            llm_name=chat_request.llm_name
        )
        
        return ChatResponse(
            user=chat_request.user,
            assistant=response,
            llm_used=llm_used
        )
    
    async def stream_chat(self, chat_request: ChatRequest):
        """Stream chat responses"""
        async for chunk in AgentService.stream_chat(
            user_message=chat_request.user,
            llm_name=chat_request.llm_name
        ):
            # Format the chunk as a Server-Sent Event
            data = json.dumps({
                "content": chunk,
                "user": chat_request.user,
                "llm_used": chat_request.llm_name
            })
            yield f"data: {data}\n\n" 