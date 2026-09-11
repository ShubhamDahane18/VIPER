import json
import httpx
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from app.rag.retriever import LLM_MODEL, OLLAMA_URL

class AgentState(TypedDict):
    transcript: str
    meeting_id: int
    action_items_raw: str
    action_items_parsed: List[dict]
    needs_approval: bool

def node_extract_actions(state: AgentState):
    """
    Extracts action items, owners, and deadlines.
    """
    prompt = f"""
    Analyze the following transcript and extract all Action Items.
    Output ONLY valid JSON in this exact format:
    [
      {{"task": "Task description", "owner": "Name or Unknown", "deadline": "Deadline or None"}}
    ]
    
    Transcript:
    {state['transcript']}
    """
    
    try:
        response = httpx.post(OLLAMA_URL, json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json" # Ollama json mode
        }, timeout=45.0)
        
        if response.status_code == 200:
            raw = response.json().get("response", "[]")
        else:
            raw = "[]"
    except Exception:
        raw = "[]"
        
    return {"action_items_raw": raw}

def node_validate_actions(state: AgentState):
    """
    Validates JSON and sets flags.
    """
    try:
        parsed = json.loads(state['action_items_raw'])
        if not isinstance(parsed, list):
            parsed = []
    except json.JSONDecodeError:
        parsed = []
        
    return {
        "action_items_parsed": parsed, 
        "needs_approval": len(parsed) > 0
    }

def route_approval(state: AgentState):
    if state["needs_approval"]:
        return "queue_approval"
    return END

def node_queue_approval(state: AgentState):
    """
    In the real app, this creates ActionItem DB records with PENDING APPROVAL.
    We will actually do this in the FastAPI orchestrator by taking the final state graph output.
    """
    # Simply flag it, DB insertion happens in caller
    return {}

workflow = StateGraph(AgentState)

workflow.add_node("extract", node_extract_actions)
workflow.add_node("validate", node_validate_actions)
workflow.add_node("queue_approval", node_queue_approval)

workflow.set_entry_point("extract")
workflow.add_edge("extract", "validate")
workflow.add_conditional_edges("validate", route_approval, {
    "queue_approval": "queue_approval",
    END: END
})
workflow.add_edge("queue_approval", END)

app_graph = workflow.compile()

def process_transcript_actions(transcript: str, meeting_id: int) -> List[dict]:
    initial_state = {
        "transcript": transcript,
        "meeting_id": meeting_id,
        "action_items_raw": "",
        "action_items_parsed": [],
        "needs_approval": False
    }
    
    final_state = app_graph.invoke(initial_state)
    return final_state.get("action_items_parsed", [])
