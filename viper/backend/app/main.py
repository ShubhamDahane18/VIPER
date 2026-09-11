from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
import os

from app.models.db import engine, init_db
from app.models.schema import User, Meeting, AuditLog
from app.api.endpoints import router as api_router

app = FastAPI(title="Project VIPER API", description="Prototype Backend for VIPER Voice Intelligence Platform", version="1.0.0")

app.include_router(api_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health_check():
    return {"status": "healthy"}
