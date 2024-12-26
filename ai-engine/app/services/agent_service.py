from typing import Tuple, AsyncGenerator
import logging
from fastapi import HTTPException
from ..ai.llm.factory import LLMFactory
from ..repositories.llm_repository import LLMRepository
from ..utils.llm_cache import LLMCache

logger = logging.getLogger(__name__)

class AgentService:
    @staticmethod
    async def get_index_message() -> str:
        """Return a welcome message for the index route."""
        return "Welcome to Zorat AI Agent Service - Index"
    
    @staticmethod
    async def get_home_message() -> str:
        """Return a welcome message for the home route."""
        return "Welcome to Zorat AI Agent Service - Home"
    
    @staticmethod
    async def process_chat(user_message: str, llm_name: str) -> Tuple[str, str]:
        """
        Process the user's message using the specified LLM.
        Returns a tuple of (response, llm_name).
        """
        try:
            logger.info(f"Processing chat message with LLM: {llm_name}")
            
            # Try to get LLM from cache
            llm_config = LLMCache.get_llm(llm_name)
            
            # If not in cache, get from database and cache it
            if not llm_config:
                logger.debug(f"LLM {llm_name} not found in cache, fetching from database")
                llm_config = await LLMRepository.get_llm_by_name(llm_name)
                if llm_config:
                    LLMCache.set_llm(llm_config)
                    logger.debug(f"Cached LLM configuration for {llm_name}")
            
            if not llm_config:
                logger.warning(f"LLM not found: {llm_name}")
                raise HTTPException(
                    status_code=404,
                    detail=f"LLM not found: {llm_name}"
                )
            
            if not llm_config.is_active:
                logger.warning(f"LLM {llm_name} is not active")
                raise HTTPException(
                    status_code=400,
                    detail=f"LLM {llm_name} is not active"
                )
            
            # Create LLM instance
            try:
                logger.debug(f"Creating LLM instance for {llm_name}")
                llm = await LLMFactory.create(llm_config)
            except Exception as e:
                logger.error(f"Failed to initialize LLM {llm_name}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize LLM: {str(e)}"
                )
            
            # Process message
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ]
            
            try:
                logger.debug(f"Sending chat request to {llm_name}")
                response = await llm.chat(messages)
                logger.info(f"Successfully processed chat with {llm_name}")
                return response, llm_name
            except Exception as e:
                logger.error(f"Failed to process chat with {llm_name}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process chat: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in process_chat: {str(e)}")
            logger.exception("Detailed error:")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    @staticmethod
    async def stream_chat(user_message: str, llm_name: str) -> AsyncGenerator[str, None]:
        """
        Stream the chat responses from the specified LLM.
        Yields chunks of the response as they become available.
        """
        try:
            logger.info(f"Processing streaming chat message with LLM: {llm_name}")
            
            # Try to get LLM from cache
            llm_config = LLMCache.get_llm(llm_name)
            
            # If not in cache, get from database and cache it
            if not llm_config:
                logger.debug(f"LLM {llm_name} not found in cache, fetching from database")
                llm_config = await LLMRepository.get_llm_by_name(llm_name)
                if llm_config:
                    LLMCache.set_llm(llm_config)
                    logger.debug(f"Cached LLM configuration for {llm_name}")
            
            if not llm_config:
                logger.warning(f"LLM not found: {llm_name}")
                raise HTTPException(
                    status_code=404,
                    detail=f"LLM not found: {llm_name}"
                )
            
            if not llm_config.is_active:
                logger.warning(f"LLM {llm_name} is not active")
                raise HTTPException(
                    status_code=400,
                    detail=f"LLM {llm_name} is not active"
                )
            
            # Create LLM instance
            try:
                logger.debug(f"Creating LLM instance for {llm_name}")
                llm = await LLMFactory.create(llm_config)
            except Exception as e:
                logger.error(f"Failed to initialize LLM {llm_name}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize LLM: {str(e)}"
                )
            
            # Process message
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ]
            
            try:
                logger.debug(f"Starting streaming chat with {llm_name}")
                async for chunk in llm.stream_chat(messages):
                    yield chunk
                logger.info(f"Successfully completed streaming chat with {llm_name}")
            except Exception as e:
                logger.error(f"Failed to stream chat with {llm_name}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to stream chat: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in stream_chat: {str(e)}")
            logger.exception("Detailed error:")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            ) 