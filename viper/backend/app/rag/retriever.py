from typing import List, Dict, Any
from app.rag.indexer import qdrant, encoder, COLLECTION_NAME
from qdrant_client.http import models as qmodels
import json
import httpx # for local Ollama integration

OLLAMA_URL = "http://localhost:11434/api/generate"
# Fallback local fast model
LLM_MODEL = "qwen2.5:0.5b" # Default to a fast qwen/llama locally, can be swapped.

def generate_local_llm_response(prompt: str, model: str = LLM_MODEL) -> str:
    """
    Calls local Ollama API to generate response.
    """
    try:
        response = httpx.post(OLLAMA_URL, json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }, timeout=30.0)
        
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"Error from LLM API: {response.text}"
    except httpx.RequestError as e:
        return f"Warning: Failed to connect to local LLM (Ollama). Ensure it is running on {OLLAMA_URL} with model {model}. Error: {e}"

def search_rag(query: str, user_role: str) -> Dict[str, Any]:
    """
    1. Embed query
    2. Enforce ACL explicitly via Filter
    3. Retrieve top K
    4. Compile Prompt
    5. Generate Answer via Ollama
    6. Return citations
    """
    
    vector = encoder.encode(query).tolist()
    
    # 2. ACL FILTERING - CRITICAL
    # Enforced BEFORE context reaches the LLM
    acl_filter = qmodels.Filter(
        must=[
            qmodels.FieldCondition(
                key="allowed_roles",
                match=qmodels.MatchAny(any=[user_role.lower(), "admin"]) # Admin can see all, or specific user role
            )
        ]
    )
    
    # 3. Retrieve
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        query_filter=acl_filter,
        limit=5,
        with_payload=True
    )
    
    if not hits:
        return {
            "answer": "I found no information matching your query in the meetings you have access to.",
            "citations": []
        }
        
    context_blocks = []
    citations = []
    
    for hit in hits:
        payload = hit.payload
        content = payload["content"]
        meeting_id = payload["meeting_id"]
        speaker_id = payload["speaker_id"]
        start_ts = payload["timestamp_start"]
        device = payload["device_serial"]
        
        context_blocks.append(f"[Meeting ID: {meeting_id} | Speaker: {speaker_id} | Timestamp: {start_ts}]: {content}")
        
        citations.append(f"Meeting M{str(meeting_id).zfill(3)} | {convert_ts(start_ts)} | {speaker_id} | {device}")

    # Deduplicate citations
    citations = list(set(citations))
    
    # 4. Compile Prompt
    context_str = "\\n".join(context_blocks)
    prompt = f"Use the following transcribed meeting snippets to answer the user's question. ONLY use the provided information.\n\nContext:\n{context_str}\n\nQuestion: {query}\n\nAnswer:"
    
    # 5. Generate
    answer = generate_local_llm_response(prompt)
    
    return {
        "answer": answer.strip(),
        "citations": citations
    }

def convert_ts(seconds_raw: float) -> str:
    # Convert 14.5 to 00:00:14
    seconds = int(seconds_raw)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
