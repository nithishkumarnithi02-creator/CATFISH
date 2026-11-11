
import os
import hmac
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

app = FastAPI(title="CATFISH AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nithishkumarnithi02-creator.github.io"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=6000)
    language: str = "auto"

@app.get("/health")
def health():
    return {"status": "online", "app": "CATFISH"}

@app.post("/v1/chat")
def chat(data: ChatRequest, authorization: str = Header(default="")):
    token = os.getenv("CATFISH_APP_TOKEN", "")
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not token or not hmac.compare_digest(
        authorization, "Bearer " + token
    ):
        raise HTTPException(status_code=401, detail="Invalid app token")

    if not api_key:
        raise HTTPException(status_code=503, detail="AI service not configured")

    language = {
        "ta": "Reply in Tamil.",
        "en": "Reply in English.",
        "hi": "Reply in Hindi.",
        "auto": "Reply in the user's language."
    }.get(data.language, "Reply in the user's language.")

    try:
        client = OpenAI(api_key=api_key)
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CATFISH, a helpful multilingual "
                        "personal AI assistant specializing in HR, "
                        "payroll, PF, ESI and workplace administration. "
                        + language
                    )
                },
                {"role": "user", "content": data.message}
            ],
            max_tokens=900
        )
        return {"reply": result.choices[0].message.content}
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI service request failed. Check server configuration."
        )
