from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import json
import traceback
import uuid
from groq import Groq  # Import Groq client
from gtts import gTTS   # Free Google TTS

app = FastAPI()

# CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Groq Client
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("✅ Groq API configured")
except Exception as e:
    print(f"❌ Groq API error: {e}")

# UPDATED SYSTEM PROMPT
SYSTEM_PROMPT = """You are a friendly Pongal Celebrations 2026 chatbot for Easwari Engineering College.

**IMPORTANT INSTRUCTION:** Regardless of the language the user speaks (English or Tamil), you must **ALWAYS REPLY IN TAMIL**. 
Your response will be read out loud by a text-to-speech engine, so keep it natural and conversational in Tamil.

MENU (Only discuss these items):
1. Panagam (பானகம்)
2. Thinai urundai (தினை உருண்டை)
3. Ven Pongal (வெண் பொங்கல்)
4. Varagu Pongal (வரகு பொங்கல்)
5. Thinai Pongal (தினை பொங்கல்)
6. Gulab Jamun (குலாப் ஜாமூன்)
7. Black Channa Sundal (கருப்பு கொண்டைக்கடலை சுண்டல்)
8. White Channa Sundal (வெள்ளை கொண்டைக்கடலை சுண்டல்)
9. Groundnut Sundal (வேர்க்கடலை சுண்டல்)
10. Akkaruppatti Pongal (அக்கருப்பட்டி பொங்கல்)
11. Kilangu (கிழங்கு)
12. Panakilangu (பனங்கிழங்கு)
13. Sugarcane (கரும்பு)

Keep answers short and sweet (maximum 4-5 sentences)."""

def get_emotion(text):
    text = text.lower()
    if any(word in text for word in ['super', 'nalla', 'suvai', 'happy', 'santhosham']):
        return 'excited'
    if any(word in text for word in ['sorry', 'mannikka', 'illai']):
        return 'sad'
    if any(word in text for word in ['epadi', 'enna', 'recipe', '?']):
        return 'thinking'
    return 'happy'

@app.get("/")
async def root():
    return {"status": "Pongal Chatbot LIVE (Groq Edition) ✅", "url": "https://pongal-celeb.onrender.com"}

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "") if data else ""
        print(f"📨 Received: {message}")
        
        if not message:
            return JSONResponse({
                "response": "தயவுசெய்து ஏதாவது கேளுங்கள்! 😊",
                "emotion": "happy"
            })
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=700,
        )

        bot_reply = chat_completion.choices[0].message.content.strip()
        emotion = get_emotion(bot_reply)
        print(f"🤖 Reply (Tamil): {bot_reply}")
        
        return JSONResponse({
            "response": bot_reply,
            "emotion": emotion
        })
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(traceback.format_exc())
        return JSONResponse({
            "response": "மன்னிக்கவும், ஒரு சிறு தவறு நடந்துவிட்டது. மீண்டும் முயற்சிக்கவும்.",
            "emotion": "sad"
        }, status_code=500)

@app.post("/tts")
async def tts(request: Request):
    """Generate Tamil speech audio from text using gTTS (free)"""
    try:
        data = await request.json()
        text = data.get("text", "")
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)

        # Generate MP3 file with gTTS
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text, lang="ta")
        tts.save(filename)

        # Return the file directly
        return FileResponse(filename, media_type="audio/mpeg")

    except Exception as e:
        print(f"❌ TTS ERROR: {e}")
        return JSONResponse({"error": "TTS failed"}, status_code=500)

@app.get("/health")
async def health():
    return {"status": "healthy", "groq": os.getenv("GROQ_API_KEY") is not None}
