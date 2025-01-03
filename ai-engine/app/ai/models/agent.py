import logging
from typing import List, Dict, Any
from langchain.agents import AgentType, initialize_agent
from ..core.base_tool import BaseTool
from ...repositories.agent_repository import AgentRepository
from ...repositories.capability_repository import CapabilityRepository
from ...repositories.llm_repository import LLMRepository
from ..llm.factory import LLMFactory
import importlib

logger = logging.getLogger(__name__)

class Agent:
    """LangChain-based agent implementation"""
    
    def __init__(self, config: Dict[str, Any], session_id: str):
        """Initialize agent with configuration"""
        self.config = config
        self.session_id = session_id
        self.tools: List[BaseTool] = []
        self.llm = None
        self.agent_executor = None
        logger.debug(f"Agent initialized for session {session_id}")
    
    @classmethod
    async def create(cls, agent_id: str, session_id: str) -> 'Agent':
        """Create a new agent instance"""
        try:
            # Load agent configuration
            agent_repo = AgentRepository()
            agent_config = await agent_repo.get_by_id(agent_id)
            if not agent_config:
                raise ValueError(f"Agent not found: {agent_id}")
            
            logger.debug(f"Loaded agent config: {agent_config}")
            
            # Create agent instance
            agent = cls(agent_config, session_id)
            await agent.initialize()
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise
    
    async def initialize(self) -> None:
        """Initialize agent with LLM and tools"""
        try:
            # Get LLM configuration
            llm_repo = LLMRepository()
            llm_config = await llm_repo.get_by_id(self.config.get("llm"))
            if not llm_config:
                raise ValueError("No LLM configuration found")
            
            logger.debug(f"Using LLM config: {llm_config}")
            
            # Initialize LLM
            self.llm = await LLMFactory.create(llm_config)
            
            # Load capabilities as tools
            await self._load_tools()
            
            if not self.tools:
                raise ValueError("No tools loaded. Agent requires at least one tool.")
            
            # Get LangChain tool instances
            langchain_tools = [tool.langchain_tool for tool in self.tools]
            logger.debug(f"Loaded {len(langchain_tools)} tools")
            
            # Initialize LangChain agent
            self.agent_executor = initialize_agent(
                tools=langchain_tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
            
            logger.info(f"Agent initialized with {len(self.tools)} tools")
            
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise
    
    async def _load_tools(self) -> None:
        """Load capabilities and convert them to tools"""
        try:
            capability_repo = CapabilityRepository()
            capability_ids = self.config.get("capabilities", [])
            
            logger.debug(f"Loading {len(capability_ids)} capabilities: {capability_ids}")
            
            for cap_id in capability_ids:
                try:
                    # Load capability config
                    cap_config = await capability_repo.get_by_id(cap_id)
                    if not cap_config:
                        logger.warning(f"Capability not found: {cap_id}")
                        continue
                    
                    logger.debug(f"Loaded capability config: {cap_config}")
                    
                    # Import and instantiate tool class
                    tool_class = self._import_tool_class(cap_config.get("file"))
                    if tool_class:
                        tool = tool_class(cap_config)
                        self.tools.append(tool)
                        logger.debug(f"Loaded tool: {tool.name}")
                    else:
                        logger.warning(f"Failed to load tool class for capability: {cap_id}")
                        
                except Exception as e:
                    logger.error(f"Error loading capability {cap_id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error loading tools: {str(e)}")
            raise
    
    def _import_tool_class(self, file_name: str) -> type:
        """Import tool class from file"""
        try:
            if not file_name:
                logger.error("No file name provided for tool class")
                return None
                
            logger.debug(f"Importing tool class from file: {file_name}")
            
            # Remove .py extension if present
            if file_name.endswith('.py'):
                file_name = file_name[:-3]
            
            module_path = f"app.ai.capabilities.implementations.{file_name}"
            logger.debug(f"Full module path: {module_path}")
            
            module = importlib.import_module(module_path)
            logger.debug(f"Successfully imported module: {module}")
            
            # Get the first class that inherits from BaseTool
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseTool) and attr != BaseTool:
                    logger.debug(f"Found tool class: {attr_name}")
                    return attr
                    
            logger.error(f"No tool class found in {file_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error importing tool class from {file_name}: {str(e)}")
            return None
    
    async def process_message(self, message: str) -> str:
        """Process user message using LangChain agent"""
        try:
            if not self.agent_executor:
                raise ValueError("Agent not initialized")
                
            response = await self.agent_executor.arun(message)
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise 