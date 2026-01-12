from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import os
import json
import traceback

app = FastAPI()

# CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    print("✅ Gemini API configured")
except Exception as e:
    print(f"❌ Gemini API error: {e}")

SYSTEM_PROMPT = """You are a friendly Pongal Celebrations 2026 chatbot for Easwari Engineering College.

MENU (answer ONLY these items):
1. Panagam
2. Sweet Pongal 
3. Ven Pongal 
4. Varagu Pongal
5. Thinai Pongal
6. Gulab Jamun
7. Black Channa Sundal
8. White Channa Sundal
9. Groundnut Sundal
10. Milk Payasam
11. Adai Payasam
12. Kilangu
13. Panakilangu
14. Vadai
15. Sugarcane
16. Sweet Pongal

Keep answers short (1-2 sentences)."""

def get_emotion(text):
    text = text.lower()
    if any(word in text for word in ['delicious', 'yummy', 'tasty', 'great']):
        return 'excited'
    if any(word in text for word in ['sorry', 'no']):
        return 'sad'
    if any(word in text for word in ['how', 'what', 'recipe']):
        return 'thinking'
    return 'happy'

@app.get("/")
async def root():
    return {"status": "Pongal Chatbot LIVE ✅", "url": "https://pongal-celeb.onrender.com"}

@app.post("/chat")
async def chat(request: Request):
    try:
        # Handle ANY request format
        data = await request.json()
        message = data.get("message", "") if data else ""
        
        print(f"📨 Received: {message}")
        
        if not message:
            return JSONResponse({
                "response": "Send me a message! 😊", 
                "emotion": "happy"
            })
        
        # Generate response
        model = genai.GenerativeModel('gemini-2.5-flash')
        full_prompt = SYSTEM_PROMPT + f"\n\nUser: {message}\nBot:"
        response = model.generate_content(full_prompt)
        bot_reply = response.text.strip()[:200]  # Limit length
        
        emotion = get_emotion(bot_reply)
        print(f"🤖 Reply: {bot_reply}")
        
        return JSONResponse({
            "response": bot_reply,
            "emotion": emotion
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse({
            "response": f"Oops! {error_msg[:50]}... Try again!",
            "emotion": "sad"
        }, status_code=500)

@app.get("/health")
async def health():
    return {"status": "healthy", "gemini": os.getenv("GEMINI_API_KEY") is not None}
