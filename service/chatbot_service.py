import os
import requests
from openai import AzureOpenAI
from service.vector_store import load_vector_store
import random
import urllib.parse

# -------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------
from dotenv import load_dotenv

from utils.document_search import DocumentSearchTool
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_API_VERSION = "2024-05-01-preview"

# -------------------------------------------------------------
# Initialize Azure OpenAI Client
# -------------------------------------------------------------
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_API_VERSION
)

# -------------------------------------------------------------
# Load the FAISS Vector Store
# -------------------------------------------------------------
vectorstore = DocumentSearchTool().load_vectorstore()

# -------------------------------------------------------------
# Small talk / greetings
# -------------------------------------------------------------
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "hola", "namaste"]
SMALL_TALK = {
    # --- Feelings / wellbeing ---
    "how are you": [
        "I'm doing great! How about you?",
        "All good here — how are you doing today?",
        "I'm fine, thanks! What about you?",
        "Feeling energized and ready to help! How about you?",
        "Doing well, just enjoying my day! How about you?"
    ],
    "how is it going": [
        "Everything's going smoothly! And you?",
        "All good here! How's your day going?",
        "Pretty good, thanks! How about yourself?"
    ],

    # --- Casual greetings / small talk ---
    "what's up": [
        "Not much! How can I help you today?",
        "Just here to assist you! What's up with you?",
        "Helping people and answering questions! What about you?",
        "All good here! What’s going on with you?"
    ],
    "hi": [
        "Hey! How’s it going?",
        "Hello there! 😊 What’s up?",
        "Hi! Ready to help you with anything you need."
    ],
    "hello": [
        "Hello! How are you today?",
        "Hi there! How’s everything going?",
        "Hey! Great to see you here."
    ],

    # --- Gratitude / appreciation ---
    "thank you": [
        "You're very welcome! 😊",
        "No problem! Happy to help!",
        "Anytime! Glad I could assist you.",
        "Of course! Always here to help you."
    ],
    "thanks": [
        "You're welcome! 😄",
        "No worries! Happy to help.",
        "Glad I could help! 🙂",
        "Anytime! Let me know if you need anything else."
    ],

    # --- Work / study related ---
    "what are you doing": [
        "Just chatting and helping out! What about you?",
        "Answering questions and assisting! How's your day going?",
        "I'm helping people like you! What are you up to?"
    ],
    "are you busy": [
        "Not at all! I'm always here to help you.",
        "I have time for you! How can I assist?",
        "Nope, just ready to chat with you!"
    ],

    # --- Random small talk ---
    "tell me a joke": [
        "Why did the computer show up at work late? It had a hard drive! 😄",
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "I would tell you a joke about UDP… but you might not get it. 😆"
    ],
    "what's your name": [
        "I'm your friendly Product Manual Assistant! You can call me Assistant.",
        "I go by Assistant! How can I help you today?",
        "Just your helpful assistant here to answer your questions."
    ]
}


# -------------------------------------------------------------
# Main Chatbot Logic
# -------------------------------------------------------------
def ask_question(user_query: str, history=None) -> str:
    q = user_query.strip()
    if not q:
        return "Please ask something."

    u = q.lower()

    # --- Step 0: Greetings / small talk ---
    for g in GREETINGS:
        if g in u:
            return random.choice([
                "Hello! 👋 How can I assist you today?",
                "👋 Hello there! I'm your Product Manual Assistant. How are you doing today? 😊 What can I help you with?"
            ])
    for key, responses in SMALL_TALK.items():
        if key in u:
            return random.choice(responses)
    print("Vectorstore:", vectorstore)
    # --- Step 2: PDF-based answer ---
    docs = vectorstore.similarity_search(q, k=3)
    context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant context found."

    # --- Step 3: Build prompt ---
    system_prompt = (
        "You are a friendly assistant for a manufacturing product manual. "
        "Answer naturally like a human and stay factual based on the document context. "
        "If unclear, politely say so and guide the user helpfully."
    )

    conversation_context = ""
    if history:
        for turn in history[-3:]:
            conversation_context += f"{turn['role'].capitalize()}: {turn['message']}\n"

    prompt = f"""
{conversation_context}

Document Context:
{context}

User Question:
{q}

Now respond in a friendly and conversational way.
"""

    # --- Step 4: Query Azure GPT ---
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=800
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"⚠️ Oops! Something went wrong: {str(e)}"

    # --- Step 5: Add personality ---
    if "thank" in u:
        answer += " 😊 You're very welcome! Always happy to help."

    return answer
