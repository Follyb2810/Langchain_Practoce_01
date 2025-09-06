from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

ll = ""


@tool
def classify_triage(vitals: dict) -> dict:
    """Use Mistral to classify patient vitals into triage categories."""
    prompt = f"""
    You are a medical triage classifier. Classify the patient into one of:
    - Green: simple complaint, minor issues, no immediate attention
    - Orange: moderate complexity, requires further examination, not life threatening
    - Red: life threatening emergency

    Patient vitals:
    Heart Rate: {vitals.get("heart_rate")}
    Systolic BP: {vitals.get("systolic_bp")}
    Diastolic BP: {vitals.get("diastolic_bp")}
    Temperature: {vitals.get("temperature")}
    Weight: {vitals.get("weight")}
    Symptoms: {vitals.get("symptoms")}

    Return JSON ONLY in this format:
    {{
      "triage": "Green|Orange|Red",
      "reason": "...",
      "advice": "...",
      "recommendedRole": "general|cardiologist|pulmonologist|other"
    }}
    """

    # Query Mistral via Ollama
    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        result = json.loads(response.content)
    except Exception:
        # fallback rule-based classification
        hr = vitals.get("heart_rate", 0)
        temp = vitals.get("temperature", 0)
        sys = vitals.get("systolic_bp", 0)
        dia = vitals.get("diastolic_bp", 0)
        if hr > 120 or temp > 39 or sys > 180 or dia > 110:
            return {
                "triage": "Red",
                "reason": "Critical vitals detected.",
                "advice": "Seek immediate emergency medical attention.",
                "recommendedRole": "cardiologist",
            }
        return {
            "triage": "Green",
            "reason": "Vitals are within safe ranges.",
            "advice": "Routine follow-up only.",
            "recommendedRole": "general",
        }

    return result
