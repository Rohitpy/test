# backend/app/agents/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)
from operator import add
from .sql_generator import SqlGeneratorAgent
from .sql_executor import execute_node

class AgentState(TypedDict):
    nl_query: str
    sql: Optional[str]
    previous_sql: Optional[str]
    results: Optional[List[Dict[str, Any]]]
    error: Optional[str]
    approved: bool
    status: str
    session_id: str
    messages: Annotated[List, add]  # For message history

# Initialize checkpointer for HITL persistence
checkpointer = MemorySaver()

# Build the state graph
workflow = StateGraph(AgentState)

#node table name
def generate_tablename_node(state: AgentState) -> AgentState:
    try:
        session_id = state.get("session_id", "default")
        agent = SqlGeneratorAgent(session_id)
        input_data = {
            "nl_query": state["nl_query"],
            "previous_sql": state.get("previous_sql"),
            "error": state.get("error", ""),
            "chat_history": ""  # Will be populated by memory
        }
        table_names = agent.process_table_schema(input_data)
        #sql = agent.process(input_data)
        state["table_name"] = table_names.strip()
        state["status"] = "generated"
        state["error"] = None  # Clear any previous errors
        return state
    
    except Exception as e:
        state["error"] = f"SQL generation failed: {str(e)}"
        state["status"] = "error"
        return state
    
# Node: Generate SQL
def generate_sql_node(state: AgentState) -> AgentState:
    try:
        session_id = state.get("session_id", "default")
        agent = SqlGeneratorAgent(session_id)
        input_data = {
            "nl_query": state["nl_query"],
            "previous_sql": state.get("previous_sql"),
            "error": state.get("error", ""),
            "chat_history": ""  # Will be populated by memory
        }
        sql = agent.process(input_data)
        state["sql"] = sql.strip()  # Clean up any extra whitespace
        state["previous_sql"] = sql  # For potential regeneration
        state["status"] = "generated"
        state["error"] = None  # Clear any previous errors
        return state
    except Exception as e:
        state["error"] = f"SQL generation failed: {str(e)}"
        state["status"] = "error"
        return state

# Node: Human Approval (interrupt point)
def human_approval_node(state: AgentState) -> AgentState:
    if not state.get("approved", False):
        state["status"] = "awaiting_approval"
        # In LangGraph, we handle interrupts through the compilation config
        return state
    state["status"] = "approved"
    return state

# Conditional edge function to determine next step after approval
def approval_condition(state: AgentState) -> str:
    if state.get("approved", False):
        return "execute"
    elif state.get("error") and not state.get("approved", False):
        return "generate_sql"  # Regenerate on error
    else:
        return "human_approval"  # Stay in approval loop

# Add nodes and edges
workflow.add_node("generate_table", generate_tablename_node)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("human_approval", human_approval_node)
workflow.add_node("execute", execute_node)

workflow.set_entry_point("generate_table")
workflow.add_edge("generate_table", "generate_sql")
workflow.add_edge("generate_sql", "human_approval")

# Add conditional edge from human_approval
workflow.add_conditional_edges(
    "human_approval",
    approval_condition,
    {
        "execute": "execute",
        "generate_sql": "generate_sql",
        "human_approval": "human_approval"
    }
)
workflow.add_edge("execute", END)

# Compile graph with interrupt
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_approval"]  # Pause before approval node
)

# Function to invoke the graph
async def run_agent(input_state: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    config = {"configurable": {"thread_id": session_id}}
    
    # Start or resume the graph execution
    try:
        # Check if this is a fresh start or resuming
        current_state = graph.get_state(config)
        
        if current_state and current_state.values:
            # Check if this is a new query vs continuing previous workflow
            current_status = current_state.values.get("status")
            current_nl_query = current_state.values.get("nl_query")
            new_nl_query = input_state.get("nl_query")
            
            is_new_query = (
                new_nl_query and 
                new_nl_query != current_nl_query and  # Different query text
                input_state.get("status") == "initialized" and
                not input_state.get("approved", False)
            )
            
            logger.info(f"State check - Current: {current_status}, Current NL: {current_nl_query}")
            logger.info(f"New input - Status: {input_state.get('status')}, NL: {new_nl_query}")
            logger.info(f"Is new query: {is_new_query}")
            
            if is_new_query:
                # This is a completely new query - reset all previous state
                logger.info(f"New query detected, resetting session state. Old: '{current_nl_query}', New: '{new_nl_query}'")
                current_state.values.clear()  # Clear all previous state
                current_state.values.update(input_state)  # Set fresh state
                # Start fresh workflow
                result = None
                async for event in graph.astream(input_state, config=config):
                    result = event
            else:
                # Resuming existing workflow - update specific values
                logger.info("Continuing existing workflow")
                for key, value in input_state.items():
                    current_state.values[key] = value
                # Continue from where we left off
                result = None
                async for event in graph.astream(None, config=config):
                    result = event
        else:
            # Fresh start
            result = None
            async for event in graph.astream(input_state, config=config):
                result = event
        
        # Get final state after execution
        final_state = graph.get_state(config)
        if final_state and final_state.values:
            # Check if we're interrupted (waiting for human approval)
            if final_state.next and "human_approval" in final_state.next:
                final_state.values["status"] = "awaiting_approval"
            return final_state.values
        else:
            return input_state
            
    except Exception as e:
        return {**input_state, "error": f"Graph execution error: {str(e)}", "status": "error"}
