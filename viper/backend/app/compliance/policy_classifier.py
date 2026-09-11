from typing import List, Dict

# Missing consent preamble keywords
CONSENT_KEYWORDS = ["consent", "recording", "agree", "permission", "aware", "record this"]

# Restricted locations / topics (Mock logic for restricted location recording)
RESTRICTED_LOCATIONS = ["bathroom", "restroom", "hospital room", "classified facility", "scif"]

def classify_policy_breaches(segments: List[Dict]) -> List[str]:
    """
    Checks the transcript segments for policy violations.
    1. Missing consent preamble (within first 30 seconds).
    2. Restricted location recording (mentioned or inferred).
    """
    violations = []
    
    full_text = " ".join([s["text"].lower() for s in segments])
    
    # 1. Missing Consent Preamble
    # Look at the first minute (e.g. segments under 60.0s)
    early_segments = [s for s in segments if s["start"] < 60.0]
    early_text = " ".join([s["text"].lower() for s in early_segments])
    
    has_consent = any(kw in early_text for kw in CONSENT_KEYWORDS)
    if not has_consent and len(early_segments) > 0:
        violations.append("POLICY BREACH: Missing explicit consent preamble in the first 60 seconds.")
        
    # 2. Restricted Location
    for loc in RESTRICTED_LOCATIONS:
        if loc in full_text:
            violations.append(f"POLICY BREACH: Restricted location mentioned/detected ({loc}).")
            
    return violations
