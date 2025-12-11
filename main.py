import os
import re
import io
import json
import difflib
from difflib import SequenceMatcher
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from openai import OpenAI
from PyPDF2 import PdfReader
from io import BytesIO

# Internal imports
from common.appLogger import AppLogger
from common.secrets_env import load_secrets_env_variables
from tushar.common_tushar_funcs import load_resume_text
from tushar.one_drive_resume_handler import generate_resume_download_link
from common.db import SessionLocal, init_db, ChatUser, ChatMessage

import time
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from PyPDF2 import PdfReader
from openai import OpenAI
import math

# Initialize DB
init_db()

# Initialize FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")

# Load secrets & OpenAI client
load_secrets_env_variables()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Logger setup
logger = AppLogger({
    "name": "portfolio_bot",
    "log_file": "logs/portfolio.log",
    "log_level": "INFO",
    "log_to_stdout": True
})

# Load resume text once
RESUME_TEXT = load_resume_text()


# --------------------------------------------------------------------
# PREDEFINED ANSWERS
# --------------------------------------------------------------------
PREDEFINED_ANSWERS = {
    "how are you": "I'm just a program, but thanks for asking! How can I assist you with Tushar's profile today?",
    "hi": "Hi! I'm Tushar’s AI assistant. Ask about his skills, experience, projects, or type 'resume' to download his CV.",
    "tell me about tushar": "Tushar is a Full-Stack Developer & AI Engineer with strong experience in .NET, Python, Azure, and Multitenant systems.",
    "show me his skills": "Tushar's key skills:\n- Python, .NET Core, Node.js\n- Azure, Kubernetes, DevOps CI/CD\n- Next.js, React\n- Machine Learning & LLM Integrations\n- Multitenant Architecture\n- Microservices\n- SQL \n- Next Js \n- Jenkins\n- Docker\n- AI/ML Pipelines\n - Azure DevOps \n- Elasticsearch",
    "summarize his resume": "Tushar has 9 years of experience as a Full-Stack Developer and AI Engineer. He builds scalable systems, microservices, and multitenant apps with Azure and modern frameworks.",
    "what are his technical strengths?": "Tushar’s strengths include distributed systems, microservices, multitenancy, Azure cloud, AI integrations, and full-stack development.",
    "give me projects he has worked on": "Major Projects:\n- Multitenant Recruiter Platform (Next.js + Azure AD)\n- Resume Parsing ML Pipeline\n- Candidate Processing Microservices\n- Azure DevOps CI/CD for AKS Deployments",
    "what cloud experience does he have?": "Tushar has deep Azure experience: AKS, DevOps, Azure AD, Blob Storage, Functions, Key Vault, Pipelines, ACR.",
    "explain his multitenant implementation": "Tushar implemented multitenancy using Azure AD + NextAuth, tenant-specific routing, RBAC, and complete data isolation.",
    "how much experience does he have?": "Tushar has 9 years of professional experience.",
    "give me a short intro about him": "Tushar is a Senior Software Engineer experienced in AI, cloud, and full-stack development — building scalable enterprise systems.",
    "contact info": "You can reach Tushar at 8840872713, email: tusharchowdhury6611@gmail.com, LinkedIn: https://www.linkedin.com/in/tusharchowdhury1a996",
    "projects": "Tushar has worked on projects like a Multitenant Recruiter Platform, Resume Parsing ML Pipeline, Candidate Processing Microservices, and Azure DevOps CI/CD for AKS Deployments.",
    "skills": "Tushar's key skills:\n- Python, .NET Core, Node.js\n- Azure, Kubernetes, DevOps CI/CD\n- Next.js, React\n- Machine Learning & LLM Integrations\n- Multitenant Architecture\n- Microservices\n- SQL \n- Next Js \n- Jenkins\n- Docker\n- AI/ML Pipelines\n - Azure DevOps \n- Elasticsearch",
    "who is tushar": "Tushar Chowdury is a Senior Software Engineer with expertise in Python, .NET, Machine Learning, Azure, AWS, GCP, and scalable system design.",

    "experience summary": "Tushar has 9+ years of experience building scalable applications, integrating machine learning models, developing microservices, and leading engineering productivity improvements.",

    "current role": "Tushar is currently a Senior Software Engineer at Moback, working on ML models, scalable Python applications, cloud deployments, and backend systems.",

    "previous experience": "Tushar has worked at To The New, Chetu, CDRI, and Nigella Softwares — delivering scalable systems, solving performance bottlenecks, and mentoring teams.",

    "education": "Tushar completed his Master of Science in Computer Applications from BBD University, Lucknow (2012–2017).",

    "machine learning experience": "Tushar has hands-on experience with Scikit-learn, TensorFlow, Keras, predictive analytics, feature engineering, data preprocessing, and ML model deployment.",

    "cloud experience": "Tushar has used Azure, AWS, and GCP for deploying ML systems, backend services, microservices, pipelines, and scalable applications.",

    "python expertise": "Tushar is highly skilled in Python, data analysis, ML libraries (NumPy, Pandas, Scikit-learn, TensorFlow), API development, and scalable backend services.",

    "dotnet experience": "He has strong .NET and .NET Core experience, building enterprise-level applications and microservices.",

    "backend strengths": "His backend strengths include microservices architecture, SQL/NoSQL databases, data pipelines, and performance optimization.",

    "how he improved performance": "Tushar improved system performance by 70% at CDRI and 15–30% across other roles by optimizing architecture and integrating modern technologies.",

    "achievements": "Key achievements include ML model deployment, system performance boosts up to 70%, microservice modernization, and mentoring teams for productivity gains.",

    "team leadership": "He mentors junior developers, conducts code reviews, and helps teams follow best engineering practices.",

    "tech stack": "Primary technologies: Python, .NET Core, React, Next.js, ML frameworks, SQL, Azure, AWS, GCP, DevOps pipelines.",

    "what projects has he done": "Tushar has built ML pipelines, large-scale backend systems, microservices, Next.js frontends, and cloud-based production services.",

    "how many years experience": "Tushar has a total of 9 years of professional experience.",

    "strengths": "Strengths include problem solving, data-driven development, microservices, ML integration, and cloud infrastructure expertise.",

    "location": "Tushar is based in Bengaluru, KA 560102.",

    "contact": "You can contact him at 8840872713 or tusharchowdhury6611@gmail.com. LinkedIn: linkedin.com/in/tusharchowdhury1a996",

    "resume summary": "Tushar is a 9-year experienced Senior Software Engineer specializing in ML, scalable systems, Python, .NET, and cloud platforms.",

    "major companies": "He has worked at Moback, To The New, Chetu India, CDRI, and Nigella Softwares.",

    "skills list": "Technical skills include Python, .NET Core, React, Azure, AWS, GCP, Data Structures, TensorFlow, NumPy, Pandas, SQL, NoSQL, and microservices.",

    "why hire him": "He brings ML expertise, strong backend skills, cloud experience, and a history of improving performance and team productivity.",

    "career goals": "Tushar aims to build AI-driven platforms, scalable enterprise systems, and become a solution architect specializing in ML and cloud engineering.",

    "ml tools": "Tools: TensorFlow, Keras, Scikit-learn, Pandas, NumPy, Matplotlib, ML pipelines, predictive analytics.",

    "cloud platforms": "Cloud platforms he works with: Azure, AWS, GCP.",

    "leadership experience": "He has mentored junior engineers, led backend improvements, and guided ML pipeline integrations.",

    "domain experience": "Domains: Machine Learning, Cloud Computing, SaaS platforms, Scalable backend systems, Healthcare (CDRI), and product engineering.",

    "projects at moback": "At Moback, he built ML models, optimized Python pipelines, integrated ML into production, and improved data processing efficiency.",

    "projects at to the new": "At TTN, he built scalable applications, mentored devs, reviewed code, and solved complex backend issues.",

    "projects at chetu": "At Chetu, he improved system performance by 15% and created reusable components that boosted productivity by 30%.",

    "projects at cdri": "At CDRI, he improved system performance by 70% using optimized code and new technology integrations.",

    "projects at nigella": "At Nigella, he developed scalable code and improved system performance by 15%.",

    "full stack experience": "Full-stack experience includes React, Next.js, REST APIs, microservices, SQL/NoSQL, and cloud integration.",

    "data engineering skills": "Data engineering strengths include data preprocessing, feature engineering, cleaning, transformation, and pipeline automation.",

    "microservices experience": "He has built microservices in .NET Core and Python with SQL/NoSQL databases and cloud deployments.",

    "devops experience": "Experience with Azure DevOps, CI/CD pipelines, Docker, Kubernetes, and automated deployments.",

    "location preference": "He works remotely and is open to Bengaluru-based or remote opportunities.",

    "about his resume": "Tushar’s resume highlights 9 years of experience across Python, .NET, ML, cloud, microservices, and performance engineering."

}


# --------------------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------------------

def extract_pdf_text_from_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# -------------------------------------------------
# Embeddings + similarity
# -------------------------------------------------
def embedding(text):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


def semantic_score(resume_text, job_desc):
    emb_resume = embedding(resume_text)
    emb_job = embedding(job_desc)
    score = cosine_similarity(emb_resume, emb_job)
    return round(max(0, min(1, score)) * 100, 2)


# -------------------------------------------------
# Resume analysis
# -------------------------------------------------
def analyze_resume(resume_text, job_desc, score):
    prompt = f"""
Resume:
{resume_text}

Job Description:
{job_desc}

Match Score: {score}%

Return JSON with keys:
strengths, weaknesses, suggestions
5 items each.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {
            "strengths": [],
            "weaknesses": [],
            "suggestions": []
        }
def sse_event(progress: int, message: str):
    return f"data: {json.dumps({'progress': progress, 'message': message})}\n\n"

# -------------------------------------------------
# SSE STREAM ROUTE
# -------------------------------------------------

# -------------------------------------------------
# HTML
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def welcome_page(request: Request):
    """Welcome / Username screen"""
    return templates.TemplateResponse("username.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

def clean_words(text):
    return re.findall(r"\b[a-zA-Z0-9+#.]+\b", text.lower())


def extract_skills_simple(text):
    """Lightweight skill detection using simple keyword scanning."""
    keywords = [
        "python", "fastapi", "sql", "azure", "aws", "gcp",
        "ml", "ai", "docker", "kubernetes", "react", "next.js"
    ]
    text = text.lower()
    return [k for k in keywords if k in text]


# ---------------------------
#  OPENAI EMBEDDING UTILS
# ---------------------------
def cosine_similarity(a, b):
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0
    return dot / (na * nb)


def get_embedding(text):
    result = client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:2000]
    )
    return result.data[0].embedding


# --------------------------------------------------------------------
# SCORE CALCULATIONS (NO heavy ML, NO spaCy, NO SentenceTransformer)
# --------------------------------------------------------------------

def keyword_score(resume_text, jd_text):
    resume_words = set(clean_words(resume_text))
    jd_words = clean_words(jd_text)
    matches = [w for w in jd_words if w in resume_words]
    missing = list(set(jd_words) - resume_words)

    if not jd_words:
        return 0, []

    score = (len(matches) / len(jd_words)) * 100
    return round(score, 2), missing


def semantic_score(resume_text, jd_text):
    try:
        emb_r = get_embedding(resume_text)
        emb_j = get_embedding(jd_text)
        sim = cosine_similarity(emb_r, emb_j)
        return round(sim * 100, 2)
    except Exception as e:
        logger.error(f"Semantic scoring error: {e}")
        return 50.0


def skill_score(resume_text, jd_text):
    resume_skills = extract_skills_simple(resume_text)
    jd_skills = extract_skills_simple(jd_text)

    matches = [s for s in jd_skills if s in resume_skills]
    missing = list(set(jd_skills) - set(resume_skills))

    if not jd_skills:
        return 0, [], []

    score = len(matches) / len(jd_skills) * 100
    return round(score, 2), matches, missing


def experience_score(resume_text, jd_text):
    resume_years = re.findall(r"(\d+)\+?\s*years", resume_text.lower())
    jd_years = re.findall(r"(\d+)\+?\s*years", jd_text.lower())

    if not resume_years or not jd_years:
        return 50

    resume_exp = max(map(int, resume_years))
    required_exp = max(map(int, jd_years))

    score = min(100, (resume_exp / required_exp) * 100)
    return round(score, 2)


# --------------------------------------------------------------------
# ROUTES
# --------------------------------------------------------------------



@app.get("/chatpage", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Main AI Chat page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/save-username")
async def save_username(request: Request, username: str = Form(...)):
    db = SessionLocal()
    try:
        user = db.query(ChatUser).filter(ChatUser.username == username).first()
        if not user:
            db.add(ChatUser(username=username))
            db.commit()

        # Return chat history
        messages = db.query(ChatMessage).filter(
            ChatMessage.username == username
        ).order_by(ChatMessage.created_at.asc()).all()

        chat_history = [
            {"message": m.message, "is_bot": m.is_bot} for m in messages
        ]

        return {"success": True, "chat_history": chat_history}

    finally:
        db.close()


@app.post("/chat")
async def chat(message: str = Form(...), username: str = Form(...)):
    text = message.lower().strip()
    db = SessionLocal()
    try:
        # Save user message
        db.add(ChatMessage(username=username, message=message, is_bot=False))
        db.commit()

        # Predefined answers
        best_match = difflib.get_close_matches(text, PREDEFINED_ANSWERS.keys(), n=1, cutoff=0.5)
        if "resume" in text or "cv" in text or "download" in text:
            link = generate_resume_download_link()
            response_text = f"Here is Tushar's resume: {link}\n \n LinkedIn: https://www.linkedin.com/in/tusharchowdhury1a996"
        elif best_match:
            response_text = PREDEFINED_ANSWERS[best_match[0]]
        
        # Save bot response
        db.add(ChatMessage(username=username, message=response_text, is_bot=True))
        db.commit()
        return {"response": response_text}
    finally:
        db.close()
def extract_keywords(text: str):
    """Extract skill-like words from resume or JD."""
    text = text.lower()
    words = re.findall(r"[a-zA-Z]+(?:\s[a-zA-Z]+)?", text)
    return set([w.strip() for w in words if len(w.strip()) > 2])

def match_skills(resume_text: str, job_description: str):
    """Match resume skills vs job description skills."""
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    matched = sorted(list(resume_keywords & jd_keywords))
    missing = sorted(list(jd_keywords - resume_keywords))

    return matched, missing

def calculate_match_score(matched, missing):
    """Simple score calculation based on matched skills."""
    total = len(matched) + len(missing)
    if total == 0:
        return 0

    return round((len(matched) / total) * 100)
def extract_pdf_text(file: UploadFile) -> str:
    """Wrapper to extract PDF text from UploadFile."""
    pdf_bytes = file.file.read()
    return extract_pdf_text_from_bytes(pdf_bytes)
# ---------------------------
# Fuzzy matching utilities
# ---------------------------
def extract_keywords(text: str):
    """Extract skill-like or relevant words/phrases from text."""
    text = text.lower()
    # Words or 2-3 word phrases
    words = re.findall(r"[a-zA-Z0-9#+]+(?:\s[a-zA-Z0-9#+]+){0,2}", text)
    return set([w.strip() for w in words if len(w.strip()) > 1])

def fuzzy_match(word, candidates, threshold=0.75):
    """Return True if word matches any candidate above threshold similarity."""
    for c in candidates:
        if SequenceMatcher(None, word, c).ratio() >= threshold:
            return True
    return False

def match_skills_fuzzy(resume_text: str, job_description: str, threshold=0.75):
    """Match resume skills vs job description skills using fuzzy logic."""
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    matched = []
    missing = []

    for jd_kw in jd_keywords:
        if fuzzy_match(jd_kw, resume_keywords, threshold):
            matched.append(jd_kw)
        else:
            missing.append(jd_kw)

    return matched, missing

def calculate_fuzzy_score(matched, missing):
    """Score based on fuzzy matched skills."""
    total = len(matched) + len(missing)
    if total == 0:
        return 0
    return round((len(matched) / total) * 100, 2)

@app.post("/resume-progress")
async def resume_progress(file: UploadFile = File(...), job_description: str = Form(...)):
    # Read PDF content
    pdf_bytes = await file.read()
    resume_text = extract_pdf_text_from_bytes(pdf_bytes)
    jd_text = job_description.strip()

    async def event_stream():
        # 10% - reading resume
        yield sse_event(10, "Reading resume...")

        # 30% - extracted text
        yield sse_event(30, "Extracted resume text.")

        # 50% - fuzzy skill matching
        matched_skills, missing_skills = match_skills_fuzzy(resume_text, jd_text, threshold=0.75)
        yield sse_event(50, "Matching skills...")

        # 80% - calculate fuzzy score
        skill_score_value = calculate_fuzzy_score(matched_skills, missing_skills)
        yield sse_event(80, "Calculating score...")

        # Experience score
        exp_score_value = experience_score(resume_text, jd_text)

        # Final score (weighted)
        final_score = round(
            skill_score_value * 0.7 +  # fuzzy skill weight
            exp_score_value * 0.3,     # experience weight
            2
        )

        # 100% - done
        final_payload = {
            "progress": 100, 
            "final_score": final_score,
            "fuzzy_skill_match_score": skill_score_value,
            "experience_score": exp_score_value,
            "matched_skills": matched_skills[:50],
            "missing_skills": missing_skills[:50]
        }
        yield f"data: {json.dumps(final_payload)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

