# service/chatbot_service.py

from service.helpers import small_talk_response, document_response, decide_intent_fast
from service.crew_setup import ProductManualCrew 

# Instantiate the crew
crew_obj = ProductManualCrew()

def handle_query(user_query: str) -> str:
    """Fast local handler — uses helpers directly (no Crew)."""
    intent = decide_intent_fast(user_query)

    if intent == "small_talk":
        return small_talk_response(user_query) or "Hello! How can I help you today?"
    
    return document_response(user_query)


def handle_query_with_crew(user_query: str) -> str:
    intent = decide_intent_fast(user_query)
    # Handle small talk locally
    if intent == "small_talk":
        return small_talk_response(user_query) or "Hello! How can I help you today?"
    # Run manual query via Crew
    try:
        return crew_obj.run_manual_task(user_query)
    except Exception as e:
        return f"⚠️ Crew error: {str(e)}\n\nFalling back to direct document search.\n\n" + document_response(user_query)