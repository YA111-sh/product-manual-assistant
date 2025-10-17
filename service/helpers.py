# service/helpers.py

import os
import random
from dotenv import load_dotenv
from openai import AzureOpenAI
from service.vector_store import load_vector_store
import re

load_dotenv()

# ---------------------- Azure/OpenAI Setup ----------------------
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("CHAT_COMPLETIONS_DEPLOYMENT_NAME")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_API_VERSION,
)

# ---------------------- Load FAISS Vectorstore ----------------------
vectorstore = load_vector_store()
# check how many documents are loaded

# ---------------------- Small Talk ----------------------
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "hola", "namaste"]
SMALL_TALK = {
    "how are you": [
        "I'm doing great! How about you?",
        "All good here — how are you doing today?",
        "I'm fine, thanks! What about you?",
    ],
    "how is it going": [
        "Everything's going smoothly! And you?",
        "All good here! How's your day going?",
    ],
    "what's up": [
        "Not much! How can I help you today?",
        "Just here to assist you! What's up with you?",
    ],
    "thank you": [
        "You're very welcome! 😊",
        "No problem! Happy to help!",
    ],
    "tell me a joke": [
        "Why did the computer show up late? It had a hard drive! 😄",
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    ],
    "what's your name": [
        "I'm your friendly Product Manual Assistant! You can call me Assistant.",
        "I go by Assistant — how can I help?",
    ],
    "who are you": [
        "I'm an AI assistant trained to help with product manuals.",
        "I'm your assistant — ask me anything about the manual!",
    ],
}

def small_talk_response(user_query: str):
    """Detect and return small talk replies with fuzzy matching."""
    u = user_query.lower().strip()
    # Match greetings anywhere in the query
    for g in GREETINGS:
        if re.search(r'\b' + re.escape(g) + r'\b', u):
            return random.choice([
                "👋 Hi! How can I assist you today?",
                "Hey there! 😊 How’s your day going?",
                "Hello! I'm ready to help — what would you like to know?"
            ])
    # Match small talk keywords
    for key, responses in SMALL_TALK.items():
        if key in u:
            return random.choice(responses)
    return None

# ---------------------- Intent Detection ----------------------
def decide_intent_fast(user_query: str) -> str:
    """Classify query as small talk or manual-related."""
    u = user_query.lower().strip()
    if small_talk_response(u):
        return "small_talk"

    # manual_keywords = [
    #     "manual", "spec", "specification", "module", "installation", "install",
    #     "troubleshoot", "error", "fault", "pressure", "voltage", "current",
    #     "how to", "how do i", "safety", "maintenance", "replace", "remove",
    #     "sar", "absorption", "warranty", "certification", "title of the manual"
    # ]
    # if any(kw in u for kw in manual_keywords):
    #     return "manual_query"

    # Short questions likely small talk
    if len(u.split()) <= 4 and u.endswith("?"):
        return "small_talk"

    return "manual_query"

# ---------------------- Document Response ----------------------
def document_response(user_query: str, k: int = 3) -> str:
    """Perform vector search + LLM answer generation with context awareness."""
    print("query data:",user_query)
    
    try:
        docs = vectorstore.similarity_search(user_query, k=k)
    except Exception as e:
        return f"⚠️ Error while searching documents: {str(e)}"

    if not docs:
        return (
            "I couldn't find relevant content in the uploaded manuals. "
            "Could you clarify or provide more details?"
        )

    # Summarize top chunks
    context = "\n\n".join(doc.page_content for doc in docs)
    system_prompt = (
    "You are a helpful assistant answering questions based on the provided product manual. "
    "If the answer is not directly in the context, give the best helpful response possible. "
    "Do not ask for clarification unless absolutely necessary."
    )


    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {user_query}\n\nContext:\n{context}"}
            ],
            temperature=0.0,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating answer: {str(e)}"
