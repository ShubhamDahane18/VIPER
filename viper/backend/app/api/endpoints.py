from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlmodel import Session, select
from typing import List
from datetime import datetime
import os

from app.models.db import get_session
from app.models.schema import User, Meeting, AuditLog, ActionItem
from app.services.stt import transcribe_audio
from app.services.pii_redaction import redact_text
from app.compliance.policy_classifier import classify_policy_breaches
from app.rag.indexer import chunk_and_index
from app.rag.retriever import search_rag
from app.agents.workflow import process_transcript_actions

router = APIRouter()

# --- UTILS ---
def create_audit(session: Session, user_id: int, action: str, entity: str = None, desc: str = None):
    log = AuditLog(user_id=user_id, action=action, entity=entity, description=desc)
    session.add(log)
    session.commit()

# --- AUTH MOCK ---
# Simplified auth for prototype: pass username in header
from fastapi import Header
def get_current_user(x_username: str = Header(default="admin_user"), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == x_username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# --- UPLOAD & INGEST PIPELINE ---
@router.post("/meetings/ingest")
async def ingest_audio(
    title: str = Form(...),
    allowed_roles: str = Form("admin,legal,engineering,sales"),
    device_serial: str = Form("HR191-000"),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. Save file locally
    os.makedirs(f"viper_storage", exist_ok=True)
    file_path = f"viper_storage/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    meeting = Meeting(title=title, allowed_roles=allowed_roles, device_serial=device_serial, 
                      audio_file_path=file_path, uploaded_by_user_id=user.id)
    session.add(meeting)
    session.commit()
    session.refresh(meeting)
    
    create_audit(session, user.id, "audio upload", f"Meeting {meeting.id}", "Ingested new audio from device")

    # 2. STT
    segments = transcribe_audio(file_path)
    
    # 3. Policy Classifier
    violations = classify_policy_breaches(segments)
    
    # 4. PII Redaction
    for seg in segments:
        seg["text"] = redact_text(seg["text"])
        
    redacted_transcript_path = f"viper_storage/redacted_{meeting.id}.json"
    import json
    with open(redacted_transcript_path, "w") as f:
        json.dump(segments, f)
        
    meeting.transcript_redacted_path = redacted_transcript_path
    session.add(meeting)
    session.commit()
    
    # 5. RAG Indexing
    chunk_and_index(meeting.id, meeting.device_serial, meeting.allowed_roles, segments)
    
    # 6. LangGraph Actions
    full_text = " ".join([s["text"] for s in segments])
    actions = process_transcript_actions(full_text, meeting.id)
    
    for a in actions:
        task = ActionItem(
            meeting_id=meeting.id,
            task_description=a.get("task", ""),
            owner=a.get("owner", ""),
            deadline=a.get("deadline", "")
        )
        session.add(task)
    session.commit()
    
    return {
        "status": "success", 
        "meeting_id": meeting.id,
        "violations_detected": violations,
        "actions_extracted": len(actions)
    }

# --- RAG QUERY ---
@router.get("/search")
def search(query: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    create_audit(session, user.id, "RAG query", "Qdrant", f"Queried: {query}")
    
    # Enforce ACL: user.role is passed to RAG
    # This prevents unauthorized chunks from reaching LLM context
    result = search_rag(query, user.role)
    return result

# --- OTHER ENDPOINTS ---
@router.get("/meetings")
def get_meetings(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # ACL for meetings visible in dashboard
    all_meetings = session.exec(select(Meeting)).all()
    # Basic filter for MVP
    visible = [m for m in all_meetings if user.role.lower() in [r.strip().lower() for r in m.allowed_roles.split(',')] or user.role.lower() == "admin"]
    return visible

@router.get("/actions/pending")
def get_pending_actions(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(ActionItem).where(ActionItem.status == "PENDING APPROVAL")).all()

@router.post("/actions/{action_id}/approve")
def approve_action(action_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    action = session.exec(select(ActionItem).where(ActionItem.id == action_id)).first()
    if action:
        action.status = "APPROVED"
        session.commit()
        create_audit(session, user.id, "action approval", f"Action {action_id}")
        return {"status": "approved"}
        
@router.post("/actions/{action_id}/reject")
def reject_action(action_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    action = session.exec(select(ActionItem).where(ActionItem.id == action_id)).first()
    if action:
        action.status = "REJECTED"
        session.commit()
        create_audit(session, user.id, "action rejection", f"Action {action_id}")
        return {"status": "rejected"}

@router.get("/audit")
def get_audit_log(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return session.exec(select(AuditLog).order_by(AuditLog.timestamp.desc())).all()
