import logging
import json
from ..services.agent_service import AgentService
from ..schemas.agent_schema import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

class AgentController:
    def __init__(self):
        self.agent_service = AgentService()
    
    async def get_index(self) -> str:
        """Get index message"""
        return await self.agent_service.get_index_message()
    
    async def get_home(self) -> str:
        """Get home message"""
        return await self.agent_service.get_home_message()
    
    async def chat(self, agent_id: str, session_id: str, chat_request: ChatRequest) -> ChatResponse:
        """Process chat request"""
        response, llm_used = await self.agent_service.process_chat(
            agent_id=agent_id,
            session_id=session_id,
            user_message=chat_request.user
        )
        
        return ChatResponse(
            user=chat_request.user,
            assistant=response,
            llm_used=llm_used
        )
    
    async def stream_chat(self, agent_id: str, session_id: str, chat_request: ChatRequest):
        """Stream chat responses"""
        # TODO: Implement streaming with new agent-based approach
        # For now, just use regular chat and stream the response
        response, llm_used = await self.agent_service.process_chat(
            agent_id=agent_id,
            session_id=session_id,
            user_message=chat_request.user
        )
        
        # Format as Server-Sent Event
        data = json.dumps({
            "content": response,
            "user": chat_request.user,
            "llm_used": llm_used
        })
        yield f"data: {data}\n\n" 