from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai, os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Temporary CORS setup (later restrict to your Vercel frontend URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["https://your-frontend.vercel.app"] after deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    name: str
    feeling: str
    details: str | None = None

@app.post("/api/affirmation")
async def generate_affirmation(data: RequestData):
    if not data.name or not data.feeling:
        raise HTTPException(status_code=400, detail="Name and feeling are required.")

    # Time-of-day context
    hour = datetime.now().hour
    if hour < 12:
        context = "morning"
    elif hour < 18:
        context = "afternoon"
    else:
        context = "evening"

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":
                 "You are a supportive companion. Always respond with 2–4 warm sentences. "
                 "Use the user’s name and feeling naturally. Add a metaphor or time-of-day context when possible. "
                 "Never give medical advice or crisis counseling."},
                {"role":"user","content":
                 f"Name: {data.name}, Feeling: {data.feeling}, Details: {data.details or ''}, Time of day: {context}"}
            ]
        )
        affirmation = response["choices"][0]["message"]["content"]
        return {"affirmation": affirmation}
    except Exception:
        raise HTTPException(status_code=502, detail="Could not generate affirmation. Please try again later.")
