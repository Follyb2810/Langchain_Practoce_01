from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

# === Local Ollama LLM ===
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

# === JSON Schema ===
TRIAGE_SCHEMA = {
    "triage": "string (Green, Orange, Red)",
    "reason": "string (why this category was chosen)",
    "advice": "string (clear medical advice for patient)",
    "recommendedRole": "string (doctor role to consult, e.g. general, cardiologist)",
}

# === Prompt Template ===
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a health triage assistant. Classify vitals into one of "
            "Green, Orange, or Red. Output ONLY valid JSON with keys: "
            f"{list(TRIAGE_SCHEMA.keys())}"
        ),
        ("human", "{vitals}"),
    ]
)

chain = prompt | llm | JsonOutputParser()


def rule_based_fallback(vitals: dict) -> dict:
    """Fallback if AI fails."""
    hr = vitals.get("heart_rate", 0)
    temp = vitals.get("temperature", 0)
    sys = vitals.get("systolic_bp", 0)
    dia = vitals.get("diastolic_bp", 0)

    # Red: life threatening
    if hr > 120 or temp > 39 or sys > 180 or dia > 110:
        return {
            "triage": "Red",
            "reason": "Critical vitals detected.",
            "advice": "Seek immediate emergency medical attention.",
            "recommendedRole": "cardiologist",
        }

    # Orange: requires urgent consultation
    if hr > 100 or temp > 38 or sys > 150 or dia > 95:
        return {
            "triage": "Orange",
            "reason": "Moderately abnormal vitals, requires examination.",
            "advice": "Schedule urgent consultation.",
            "recommendedRole": "general",
        }

    # Green: safe
    return {
        "triage": "Green",
        "reason": "Vitals within safe ranges.",
        "advice": "Routine follow-up only.",
        "recommendedRole": "general",
    }


# === LangChain Tool ===
from langchain_core.tools import tool

@tool
def classify_triage(vitals: dict) -> dict:
    """Classify patient vitals into triage category using AI + fallback rules."""
    try:
        result = chain.invoke({"vitals": str(vitals)})
        return result
    except (OutputParserException, Exception) as e:
        print(f"[Fallback Triggered] Error: {e}")
        return rule_based_fallback(vitals)




REQUIRED_FIELDS = ["heart_rate", "systolic_bp", "diastolic_bp", "temperature", "weight", "symptoms"]

def validate_vitals_input(user_input: dict) -> bool:
    """Check if user input looks like proper vitals dict."""
    return all(field in user_input for field in REQUIRED_FIELDS)


@tool
def classify_triage(vitals: dict) -> dict:
    """Classify patient vitals into triage category using AI + fallback rules."""
    if not validate_vitals_input(vitals):
        return {
            "triage": "Orange",
            "reason": "Incomplete or unstructured input. Unable to process full vitals.",
            "advice": "Please provide complete vital signs to continue.",
            "recommendedRole": "general",
        }

    try:
        result = chain.invoke({"vitals": str(vitals)})
        return result
    except (OutputParserException, Exception) as e:
        print(f"[Fallback Triggered] Error: {e}")
        return rule_based_fallback(vitals)

# from langchain_core.tools import tool

# @tool
# def classify_triage(vitals: dict) -> dict:
#     """Classify patient vitals into triage category."""
#     try:
#         hr = vitals.get("heart_rate", 0)
#         temp = vitals.get("temperature", 0)
#         sys = vitals.get("systolic_bp", 0)
#         dia = vitals.get("diastolic_bp", 0)

#         # Red: life threatening
#         if hr > 120 or temp > 39 or sys > 180 or dia > 110:
#             return {
#                 "triage": "Red",
#                 "reason": "Critical vitals detected.",
#                 "advice": "Seek immediate emergency medical attention.",
#                 "recommendedRole": "cardiologist",
#             }

#         # Orange: requires physical exam
#         if hr > 100 or temp > 38 or sys > 150 or dia > 95:
#             return {
#                 "triage": "Orange",
#                 "reason": "Moderately abnormal vitals, requires examination.",
#                 "advice": "Schedule urgent consultation.",
#                 "recommendedRole": "general",
#             }

#         # Green: safe
#         return {
#             "triage": "Green",
#             "reason": "Vitals within safe ranges.",
#             "advice": "Routine follow-up only.",
#             "recommendedRole": "general",
#         }

#     except Exception:
#         # fallback
#         return {
#             "triage": "Green",
#             "reason": "Defaulted to safe fallback.",
#             "advice": "Monitor your health and consult if needed.",
#             "recommendedRole": "general",
#         }
