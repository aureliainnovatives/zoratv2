import logging
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
from ..capabilities.tool import CapabilityTool
from ..capabilities.base import BaseCapability
from ..llm.base import BaseLLM

logger = logging.getLogger(__name__)

class Agent:
    """Agent that uses LangChain for capability execution."""
    
    def __init__(self, 
                 config: Dict[str, Any],
                 llm: BaseLLM,
                 capabilities: List[BaseCapability]):
        """
        Initialize the agent.
        
        Args:
            config: Agent configuration from MongoDB
            llm: LLM instance to use
            capabilities: List of capabilities available to the agent
        """
        logger.info("***************** Initializing Agent *****************")
        self.config = config
        self.llm = llm
        self.input_format = config.get('inputFormat', 'text')
        self.output_format = config.get('outputFormat', 'text')
        
        # Create tools from capabilities
        logger.info(f"Creating tools for {len(capabilities)} capabilities")
        self.tools = []
        for cap in capabilities:
            try:
                tool = CapabilityTool(cap)
                self.tools.append(tool)
                logger.info(f"Created tool for capability: {cap.name}")
            except Exception as e:
                logger.error(f"Error creating tool for capability {cap.name}: {str(e)}")
                logger.exception("Detailed error:")
        
        if not self.tools:
            logger.error("No tools created from capabilities")
            raise ValueError("No tools available for agent")
            
        # Create conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant with access to various capabilities. 
                      Use the most appropriate capability to help the user.
                      
                      Available capabilities:
                      {tool_descriptions}
                      
                      Always try to use a capability when appropriate rather than just responding directly.
                      If you need to use a capability, make sure to provide all required parameters.
                      If you're not sure which capability to use, ask the user for clarification."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        logger.info("Creating OpenAI Functions agent")
        self.agent = OpenAIFunctionsAgent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        logger.info("Creating agent executor")
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        logger.info("Agent initialization complete")
        
    async def execute(self, input_data: str) -> str:
        """Execute the agent with the given input."""
        logger.info("***************** Executing Agent *****************")
        logger.info(f"Input: {input_data}")
        logger.info(f"Available tools: {[tool.name for tool in self.tools]}")
        
        try:
            # Build tool descriptions for prompt
            tool_descriptions = "\n".join([
                f"- {tool.name}: {tool.description}"
                for tool in self.tools
            ])
            
            # Execute agent
            result = await self.agent_executor.ainvoke({
                "input": input_data,
                "tool_descriptions": tool_descriptions
            })
            logger.info(f">>>>>>>>>>> Agent execution result: {result}")
            
            # Format response based on output_format
            if self.output_format == 'JSON':
                if not isinstance(result, dict):
                    result = {"result": result}
                return result
            return str(result.get('output', result))
            
        except Exception as e:
            error = f">>>>>>>>>>> Error executing agent: {str(e)}"
            logger.error(error)
            logger.exception("Detailed error:")
            return {"error": error} if self.output_format == 'JSON' else error 