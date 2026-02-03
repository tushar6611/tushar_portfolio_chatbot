import os
import re
import json
import math
import difflib
from io import BytesIO
from datetime import datetime
from difflib import SequenceMatcher

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    StreamingResponse
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from PyPDF2 import PdfReader

# Internal imports
from common.appLogger import AppLogger
from common.db import SessionLocal, init_db, ChatUser, ChatMessage
from tushar.common_tushar_funcs import load_resume_text
from tushar.one_drive_resume_handler import generate_resume_download_link


# -------------------------------------------------
# INIT
# -------------------------------------------------

init_db()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")

logger = AppLogger({
    "name": "portfolio_bot",
    "log_file": "logs/portfolio.log",
    "log_level": "INFO",
    "log_to_stdout": True
})

RESUME_TEXT = load_resume_text()


# -------------------------------------------------
# PREDEFINED CHAT ANSWERS
# -------------------------------------------------

PREDEFINED_ANSWERS = {
    "hi": "Hi! I'm Tushar’s assistant. Ask about skills, experience, projects, or type 'resume' to download his CV.",
    "how are you": "I'm doing great! How can I help you today?",
    "who is tushar": "Tushar Chowdhury is a Senior Software Engineer with 9+ years of experience.",
    "skills": "Python, .NET Core, Azure, AWS, React, Next.js, Docker, Kubernetes, ML, Microservices",
    "experience": "Tushar has over 9 years of experience in full-stack and AI engineering.",
    "projects": "Multitenant Recruiter Platform, Resume Parsing ML Pipeline, AKS CI/CD systems",
    "contact": "Email: tusharchowdhury6611@gmail.com | Phone: 8840872713"
}


# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def extract_pdf_text_from_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def clean_words(text: str):
    return re.findall(r"\b[a-zA-Z0-9+#.]+\b", text.lower())


def extract_skills_simple(text: str):
    keywords = [
        "python", "fastapi", "sql", "azure", "aws", "gcp",
        "docker", "kubernetes", "react", "next.js",
        "ml", "ai", "microservices", "devops"
    ]
    text = text.lower()
    return [k for k in keywords if k in text]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0
    return dot / (na * nb)


# -------------------------------------------------
# SCORING (NO AI)
# -------------------------------------------------

def keyword_score(resume_text, jd_text):
    resume_words = set(clean_words(resume_text))
    jd_words = clean_words(jd_text)

    if not jd_words:
        return 0, []

    matches = [w for w in jd_words if w in resume_words]
    missing = list(set(jd_words) - resume_words)
    score = (len(matches) / len(jd_words)) * 100

    return round(score, 2), missing


def skill_score(resume_text, jd_text):
    resume_skills = extract_skills_simple(resume_text)
    jd_skills = extract_skills_simple(jd_text)

    if not jd_skills:
        return 0, [], []

    matches = [s for s in jd_skills if s in resume_skills]
    missing = list(set(jd_skills) - set(resume_skills))
    score = (len(matches) / len(jd_skills)) * 100

    return round(score, 2), matches, missing


def experience_score(resume_text, jd_text):
    resume_years = re.findall(r"(\d+)\+?\s*years", resume_text.lower())
    jd_years = re.findall(r"(\d+)\+?\s*years", jd_text.lower())

    if not resume_years or not jd_years:
        return 50

    resume_exp = max(map(int, resume_years))
    required_exp = max(map(int, jd_years))

    return round(min(100, (resume_exp / required_exp) * 100), 2)


# -------------------------------------------------
# FUZZY MATCHING
# -------------------------------------------------

def extract_keywords(text):
    text = text.lower()
    words = re.findall(r"[a-zA-Z0-9#+]+(?:\s[a-zA-Z0-9#+]+){0,2}", text)
    return set(w.strip() for w in words if len(w.strip()) > 1)


def fuzzy_match(word, candidates, threshold=0.75):
    return any(
        SequenceMatcher(None, word, c).ratio() >= threshold
        for c in candidates
    )


def match_skills_fuzzy(resume_text, jd_text, threshold=0.75):
    resume_kw = extract_keywords(resume_text)
    jd_kw = extract_keywords(jd_text)

    matched, missing = [], []
    for kw in jd_kw:
        if fuzzy_match(kw, resume_kw, threshold):
            matched.append(kw)
        else:
            missing.append(kw)

    return matched, missing


def calculate_fuzzy_score(matched, missing):
    total = len(matched) + len(missing)
    if total == 0:
        return 0
    return round((len(matched) / total) * 100, 2)


def sse_event(progress, message):
    return f"data: {json.dumps({'progress': progress, 'message': message})}\n\n"


# -------------------------------------------------
# ROUTES
# -------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def welcome_page(request: Request):
    return templates.TemplateResponse("username.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/chatpage", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/save-username")
async def save_username(username: str = Form(...)):
    db = SessionLocal()
    try:
        if not db.query(ChatUser).filter(ChatUser.username == username).first():
            db.add(ChatUser(username=username))
            db.commit()

        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.username == username)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        return {
            "success": True,
            "chat_history": [
                {"message": m.message, "is_bot": m.is_bot}
                for m in messages
            ]
        }
    finally:
        db.close()


@app.post("/chat")
async def chat(message: str = Form(...), username: str = Form(...)):
    db = SessionLocal()
    text = message.lower().strip()

    try:
        db.add(ChatMessage(username=username, message=message, is_bot=False))
        db.commit()

        if "resume" in text or "cv" in text:
            response = generate_resume_download_link()
        else:
            match = difflib.get_close_matches(text, PREDEFINED_ANSWERS.keys(), 1, 0.5)
            response = PREDEFINED_ANSWERS.get(match[0], "Sorry, I didn’t understand.") if match else "Sorry, I didn’t understand."

        db.add(ChatMessage(username=username, message=response, is_bot=True))
        db.commit()

        return {"response": response}
    finally:
        db.close()


@app.post("/resume-progress")
async def resume_progress(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    pdf_bytes = await file.read()
    resume_text = extract_pdf_text_from_bytes(pdf_bytes)

    async def stream():
        yield sse_event(10, "Reading resume...")
        yield sse_event(30, "Extracted text")

        matched, missing = match_skills_fuzzy(resume_text, job_description)
        yield sse_event(60, "Matching skills")

        skill_score = calculate_fuzzy_score(matched, missing)
        exp_score = experience_score(resume_text, job_description)

        final_score = round(skill_score * 0.7 + exp_score * 0.3, 2)

        yield f"data: {json.dumps({
            'progress': 100,
            'final_score': final_score,
            'skill_score': skill_score,
            'experience_score': exp_score,
            'matched_skills': matched[:50],
            'missing_skills': missing[:50]
        })}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
