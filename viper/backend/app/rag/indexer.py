import os
import uuid
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer

# Initialize Local Qdrant (in-memory or file for prototype)
# We can swap to a real server URL easily
QDRANT_PATH = os.getenv("QDRANT_PATH", ":memory:")
# Initialize early so it's loaded in memory, avoid blocking later
encoder = SentenceTransformer("all-MiniLM-L6-v2")

if QDRANT_PATH == ":memory:":
    qdrant = QdrantClient(location=":memory:")
else:
    qdrant = QdrantClient(path=QDRANT_PATH)

COLLECTION_NAME = "viper_transcripts"

# Create collection if it doesn't exist
try:
    if not qdrant.collection_exists(collection_name=COLLECTION_NAME):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(
                size=encoder.get_sentence_embedding_dimension(),
                distance=qmodels.Distance.COSINE
            ),
        )
except Exception:
    pass

def chunk_and_index(meeting_id: int, device_serial: str, allowed_roles: str, redacted_segments: List[Dict]):
    """
    Chunks the REDACTED transcript segments, embedding them into Qdrant.
    Attached metadata MUST include meeting_id, speaker_id, timestamp_start, timestamp_end, allowed_roles.
    """
    roles_list = [role.strip().lower() for role in allowed_roles.split(",")]
    points = []
    
    for seg in redacted_segments:
        text = seg["text"]
        
        # We process segment by segment for deep citation accuracy
        # (For a real system, you might chunk multiple segments if they are short)
        
        vector = encoder.encode(text).tolist()
        
        point_id = str(uuid.uuid4())
        
        payload = {
            "meeting_id": meeting_id,
            "device_serial": device_serial,
            "speaker_id": seg["speaker"],
            "timestamp_start": seg["start"],
            "timestamp_end": seg["end"],
            "allowed_roles": roles_list, # IMPORTANT: LIST OF ROLES
            "content": text
        }
        
        points.append(qmodels.PointStruct(id=point_id, vector=vector, payload=payload))
        
    if points:
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
