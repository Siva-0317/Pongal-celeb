from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import tempfile
import base64
import os
import traceback

app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Gemini Config --------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

Keep answers precise (4-5 sentences).
"""

# -------------------- Utils --------------------
def get_emotion(text: str):
    t = text.lower()
    if any(w in t for w in ["delicious", "yummy", "tasty", "great"]):
        return "excited"
    if any(w in t for w in ["sorry", "no"]):
        return "sad"
    if any(w in t for w in ["how", "what", "recipe"]):
        return "thinking"
    return "happy"

def text_to_speech(text: str, lang="ta"):
    tts = gTTS(text=text, lang=lang, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        audio_bytes = open(f.name, "rb").read()
    os.unlink(f.name)
    return base64.b64encode(audio_bytes).decode()

def speech_to_text(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    return r.recognize_google(audio)

# -------------------- Routes --------------------
@app.get("/")
async def root():
    return {"status": "Pongal Chatbot LIVE ✅"}

# -------- TEXT CHAT (TEXT → AUDIO INCLUDED) --------
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")

        if not message:
            return JSONResponse({"response": "Say something 😊", "emotion": "happy"})

        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = SYSTEM_PROMPT + f"\n\nUser: {message}\nBot:"
        result = model.generate_content(prompt)

        reply = result.text.strip()
        emotion = get_emotion(reply)
        audio_b64 = text_to_speech(reply)

        return JSONResponse({
            "text": reply,
            "emotion": emotion,
            "audio": audio_b64
        })

    except Exception as e:
        return JSONResponse({
            "text": "Something went wrong!",
            "emotion": "sad",
            "error": str(e)
        }, status_code=500)

# -------- VOICE CHAT (AUDIO → TEXT → AUDIO) --------
@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    try:
        # Save uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            temp.write(await file.read())
            temp_path = temp.name

        # Speech → Text
        user_text = speech_to_text(temp_path)
        os.unlink(temp_path)

        # Gemini reply
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = SYSTEM_PROMPT + f"\n\nUser: {user_text}\nBot:"
        result = model.generate_content(prompt)

        reply = result.text.strip()
        emotion = get_emotion(reply)
        audio_b64 = text_to_speech(reply)

        return JSONResponse({
            "user_text": user_text,
            "bot_text": reply,
            "emotion": emotion,
            "audio": audio_b64
        })

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse({
            "error": "Voice processing failed",
            "emotion": "sad"
        }, status_code=500)

@app.get("/health")
async def health():
    return {"status": "healthy"}
