import os
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
import re

# We will initialize Presidio singleton
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# The user explicitly asked to redact:
# PERSON, EMAIL, PHONE, ADDRESS, CREDIT_CARD, BANK_ACCOUNT, NATIONAL_ID, MEDICAL_INFORMATION
# Some of these are built-in Presidio entities. 
PII_ENTITIES = [
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", 
    "CREDIT_CARD", "IBAN_CODE", "MEDICAL_LICENSE", 
    "US_BANK_NUMBER", "US_SSN", "UK_NHS"
]

def redact_text(text: str) -> str:
    # 1. Presidio built-in analysis
    results = analyzer.analyze(text=text, entities=PII_ENTITIES, language='en')
    
    # 2. Anonymize
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    
    redacted_text = anonymized_result.text
    
    # 3. Fallback Regex for any obvious credit cards not caught
    cc_regex = r'\b(?:\d[ -]*?){13,16}\b'
    redacted_text = re.sub(cc_regex, "[CREDIT_CARD]", redacted_text)
    
    return redacted_text
