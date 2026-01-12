from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from typing import Optional

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# System prompt for Pongal celebration food chatbot
SYSTEM_PROMPT = """You are a friendly and enthusiastic AI assistant for the Pongal Celebrations 2026 event at Easwari Engineering College's Department of Computer Science and Engineering.

EVENT DETAILS:
- Event: Thai Pongal Celebrations (Thamizhar Thirunaal)
- Date: 13 January 2026
- Venue: Easwari Engineering College, Chennai
- Organized by: Department of Computer Science and Engineering

COMPLETE FOOD MENU (16 items):
1. Panagam - Traditional jaggery drink
2. Sweet Pongal - Main dish for 200 people (made with rice, moong dal, jaggery, ghee, cashew, raisins)
3. Ven Pongal - Savory rice and lentil dish (in-charge: Maheswari Mam)
4. Varagu Pongal (Sweet version) - Millet-based sweet dish (in-charge: Indira Mam)
5. Thinai Pongal - Foxtail millet sweet pongal (in-charge: Adeline Mam)
6. Gulab Jamun - Popular Indian sweet dessert (in-charge: Anand Sir)
7. Black Channa Sundal - Protein-rich chickpea snack (in-charge: Shankar Sir)
8. White Channa Sundal - Light chickpea preparation (in-charge: Dharanya Mam)
9. Groundnut Sundal - Roasted peanut snack (in-charge: Gowthami Mam)
10. Milk Payasam - Creamy rice pudding dessert (to be confirmed, in-charge: Padma Mam)
11. Adai Payasam - Traditional lentil-based sweet (to be confirmed, in-charge: Liya Mam)
12. Kilangu (2 types) - Boiled sweet potato (Sakkari) and tapioca (Marvalli) (in-charge: Indumathy Mam)
13. Panakilangu - Palm tuber preparation (in-charge: Nirmala Mam)
14. Vadai - Crispy lentil fritters
15. Sugarcane (cleaned and cubed) - Fresh sugarcane pieces prepared by students
16. Sweet Pongal (additional) - In-charge: Kavitha Mam

PREVIOUS CELEBRATIONS HIGHLIGHTS:
- 2025: Pongal Making Competition winner - 2nd Place for Exceptional Flavour
- Past menu items include: Panjamirtham, Ven Pongal, Payasam, Vegetable Kootu, Thinai Pongal, Rava Pongal, Black Kavuni Rice Pongal, Sakkarai Pongal, Akkara Vadisal

YOUR ROLE:
- Answer questions about the food items, ingredients, and preparation
- Explain the cultural significance of Pongal dishes
- Provide details about faculty in-charge for each dish
- Share information about the celebration activities
- Be warm, enthusiastic, and respectful of Tamil culture
- Keep responses conversational and concise (2-4 sentences)
- If asked about items not on the menu, politely mention they're not part of this year's celebration but acknowledge their popularity

RESPONSE STYLE:
- Use a friendly, celebratory tone
- Occasionally use Tamil food terms naturally
- Express enthusiasm about traditional festival foods
- If uncertain, say you'll check with the organizing team
- Suggest complementary dishes when relevant
"""

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[list] = []

class ChatResponse(BaseModel):
    response: str
    emotion: str

def determine_emotion(text: str) -> str:
    """Analyze response text to determine appropriate emotion"""
    text_lower = text.lower()
    
    # Excited/Happy for food-related enthusiasm
    if any(word in text_lower for word in ['delicious', 'yummy', 'tasty', 'sweet', 'amazing', 'love', '!', 'celebrate', 'festival', 'pongal']):
        return 'excited'
    
    # Thinking for explanations or details
    if any(word in text_lower for word in ['made with', 'prepared', 'ingredients', 'recipe', 'how', 'traditional', 'cultural']):
        return 'thinking'
    
    # Concerned for uncertainties or confirmations pending
    if any(word in text_lower for word in ['to be confirmed', 'maybe', 'uncertain', 'check']):
        return 'concerned'
    
    # Sad for unavailable items or negative responses
    if any(word in text_lower for word in ['sorry', 'not available', "don't have", 'unfortunately', 'no']):
        return 'sad'
    
    # Happy for greetings and general info
    if any(word in text_lower for word in ['hello', 'hi', 'welcome', 'yes', 'available', 'sure']):
        return 'happy'
    
    return 'neutral'

@app.get("/")
def read_root():
    return {"status": "Pongal Celebration Chatbot API is running", "event": "Pongal 2026 - Easwari Engineering College"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Build conversation context
        context = SYSTEM_PROMPT + "\n\nCONVERSATION:\n"
        if request.conversation_history:
            for msg in request.conversation_history[-6:]:  # Last 6 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                context += f"{role}: {content}\n"
        
        context += f"user: {request.message}\nassistant:"
        
        # Generate response
        response = model.generate_content(context)
        bot_response = response.text.strip()
        
        # Determine emotion
        emotion = determine_emotion(bot_response)
        
        return ChatResponse(response=bot_response, emotion=emotion)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "event": "Pongal Celebrations 2026"}

@app.get("/menu")
def get_menu():
    """Endpoint to retrieve complete menu"""
    menu = [
        {"id": 1, "name": "Panagam", "type": "Beverage", "incharge": "Venue"},
        {"id": 2, "name": "Sweet Pongal", "type": "Main", "incharge": "At the venue", "servings": 200},
        {"id": 3, "name": "Ven Pongal", "type": "Main", "incharge": "Maheswari Mam"},
        {"id": 4, "name": "Varagu Pongal (Sweet)", "type": "Millet Special", "incharge": "Indira Mam"},
        {"id": 5, "name": "Thinai Pongal", "type": "Millet Special", "incharge": "Adeline Mam"},
        {"id": 6, "name": "Gulab Jamun", "type": "Dessert", "incharge": "Anand Sir"},
        {"id": 7, "name": "Black Channa Sundal", "type": "Snack", "incharge": "Shankar Sir"},
        {"id": 8, "name": "White Channa Sundal", "type": "Snack", "incharge": "Dharanya Mam"},
        {"id": 9, "name": "Groundnut Sundal", "type": "Snack", "incharge": "Gowthami Mam"},
        {"id": 10, "name": "Milk Payasam", "type": "Dessert", "incharge": "Padma Mam", "status": "To be confirmed"},
        {"id": 11, "name": "Adai Payasam", "type": "Dessert", "incharge": "Liya Mam", "status": "To be confirmed"},
        {"id": 12, "name": "Kilangu (Sakkari & Marvalli)", "type": "Traditional", "incharge": "Indumathy Mam"},
        {"id": 13, "name": "Panakilangu", "type": "Traditional", "incharge": "Nirmala Mam"},
        {"id": 14, "name": "Vadai", "type": "Snack", "incharge": "TBD"},
        {"id": 15, "name": "Sugarcane (cubed)", "type": "Fresh", "incharge": "Students"},
        {"id": 16, "name": "Sweet Pongal", "type": "Main", "incharge": "Kavitha Mam"}
    ]
    return {"event": "Pongal 2026", "total_items": 16, "menu": menu}
