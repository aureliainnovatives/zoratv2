from typing import Dict, List, Any, Annotated, TypedDict, Tuple, Union
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor
from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
import re

class ToolAction(BaseModel):
    """Model for tool selection output."""
    tool_name: str = Field(description="Name of the tool to use")
    tool_input: str = Field(description="Input to pass to the tool")
    reasoning: str = Field(description="Reasoning for selecting this tool")

class AgentState(TypedDict):
    """State for the agent graph."""
    messages: List[BaseMessage]
    next_step: str
    tools: List[BaseTool]
    tool_results: List[Dict[str, Any]]
    current_tool: Union[ToolAction, None]
    error_count: int

class GraphBuilder:
    """Builds LangGraph-based agent execution graphs."""
    
    def __init__(self, llm, tools: List[BaseTool]):
        self.llm = llm
        self.tools = tools
        self.tool_executor = ToolExecutor(tools)
        self.output_parser = PydanticOutputParser(pydantic_object=ToolAction)
        
    def build_graph(self) -> Graph:
        """Build the agent execution graph."""
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tool_executor", self._tool_executor_node)
        workflow.add_node("controller", self._controller_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define edges
        workflow.add_edge("agent", "tool_executor")
        workflow.add_edge("tool_executor", "controller")
        workflow.add_edge("controller", "agent")
        workflow.add_edge("error_handler", "agent")
        workflow.add_edge("error_handler", "controller")
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Compile the graph
        return workflow.compile()
    
    async def _agent_node(self, state: AgentState) -> Dict:
        """Agent node that decides what to do next."""
        messages = state["messages"]
        tools = state["tools"]
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant with access to the following tools:
{tool_desc}

To use a tool, respond in the following format:
{format_instructions}

Choose the most appropriate tool based on the user's request."""),
            *[("human" if i % 2 == 0 else "assistant", msg.content) 
              for i, msg in enumerate(messages)]
        ])
        
        # Format tool descriptions
        tool_desc = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
        
        # Get LLM response
        messages = prompt.format_messages(
            tool_desc=tool_desc,
            format_instructions=self.output_parser.get_format_instructions(),
            input=messages[-1].content
        )
        
        response = await self.llm.agenerate([messages])
        response_text = response.generations[0].text
        
        try:
            # Parse tool selection
            tool_action = self.output_parser.parse(response_text)
            
            return {
                "messages": state["messages"] + [AIMessage(content=response_text)],
                "next_step": "tool_executor",
                "current_tool": tool_action,
                "error_count": state["error_count"]
            }
        except Exception as e:
            return {
                "messages": state["messages"] + [
                    AIMessage(content=response_text),
                    SystemMessage(content=f"Error parsing tool selection: {str(e)}")
                ],
                "next_step": "error_handler",
                "current_tool": None,
                "error_count": state["error_count"] + 1
            }
    
    async def _tool_executor_node(self, state: AgentState) -> Dict:
        """Execute the selected tool."""
        if not state["current_tool"]:
            return {
                "next_step": "error_handler",
                "error_count": state["error_count"] + 1
            }
            
        tool_action = state["current_tool"]
        
        try:
            result = await self.tool_executor.aexecute({
                "name": tool_action.tool_name,
                "input": tool_action.tool_input
            })
            
            return {
                "tool_results": state["tool_results"] + [result],
                "next_step": "controller",
                "messages": state["messages"] + [
                    SystemMessage(content=f"Tool {tool_action.tool_name} executed successfully: {result}")
                ],
                "error_count": state["error_count"]
            }
        except Exception as e:
            return {
                "next_step": "error_handler",
                "messages": state["messages"] + [
                    SystemMessage(content=f"Tool execution error: {str(e)}")
                ],
                "error_count": state["error_count"] + 1
            }
    
    async def _controller_node(self, state: AgentState) -> Dict:
        """Control flow node that decides whether to continue or stop."""
        messages = state["messages"]
        tool_results = state["tool_results"]
        
        # Create the prompt for decision
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Based on the conversation and tool results so far, decide if we need to:
1. Use another tool (respond with 'continue')
2. Provide final answer (respond with 'end')

Current tool results:
{tool_results}"""),
            *[("human" if i % 2 == 0 else "assistant", msg.content) 
              for i, msg in enumerate(messages)]
        ])
        
        response = await self.llm.agenerate([
            prompt.format_messages(
                tool_results=json.dumps(tool_results, indent=2)
            )
        ])
        
        decision = response.generations[0].text.strip().lower()
        
        if "continue" in decision and state["error_count"] < 3:
            return {"next_step": "agent"}
        return {"next_step": "end"}
    
    async def _error_handler_node(self, state: AgentState) -> Dict:
        """Handle errors in the workflow."""
        if state["error_count"] >= 3:
            return {
                "messages": state["messages"] + [
                    SystemMessage(content="Maximum error count reached. Ending execution.")
                ],
                "next_step": "end"
            }
            
        return {
            "next_step": "agent",
            "messages": state["messages"] + [
                SystemMessage(content="Retrying with error handler guidance...")
            ]
        }

class AgentGraph:
    """Main agent graph class."""
    
    def __init__(self, llm, capabilities: List[BaseTool]):
        self.graph_builder = GraphBuilder(llm, capabilities)
        self.graph = self.graph_builder.build_graph()
    
    async def execute(self, input_text: str) -> str:
        """Execute the agent graph with input."""
        initial_state = AgentState(
            messages=[HumanMessage(content=input_text)],
            next_step="agent",
            tools=self.graph_builder.tools,
            tool_results=[],
            current_tool=None,
            error_count=0
        )
        
        try:
            final_state = await self.graph.arun(initial_state)
            
            # Format final response
            final_messages = [
                msg for msg in final_state["messages"] 
                if isinstance(msg, (HumanMessage, AIMessage))
            ]
            return final_messages[-1].content
            
        except Exception as e:
            return f"Error in agent execution: {str(e)}" 