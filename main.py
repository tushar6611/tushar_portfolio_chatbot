from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os
import difflib

from openai import OpenAI
from common.appLogger import AppLogger
from common.secrets_env import load_secrets_env_variables
from tushar.common_tushar_funcs import load_resume_text
from tushar.one_drive_resume_handler import generate_resume_download_link
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from common.db import SessionLocal, init_db, ChatUser, ChatMessage
import os

init_db()
# -------------------
# FastAPI setup
# -------------------
app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")

# -------------------
# Load secrets & client
# -------------------
load_secrets_env_variables()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = AppLogger({
    "name": "portfolio_bot",
    "log_file": "logs/portfolio.log",
    "log_level": "INFO",
    "log_to_stdout": True
})

# -------------------
# Load resume once
# -------------------
RESUME_TEXT = load_resume_text()

# -------------------
# Predefined answers
# -------------------
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

# -------------------
# Routes
# -------------------
@app.post("/save-username")
async def save_username(request: Request, username: str = Form(...)):
    db = SessionLocal()
    try:
        user = db.query(ChatUser).filter(ChatUser.username == username).first()
        if not user:
            user = ChatUser(username=username)
            db.add(user)
            db.commit()
        # Fetch previous chat history
        messages = db.query(ChatMessage).filter(ChatMessage.username == username).order_by(ChatMessage.created_at.asc()).all()
        chat_history = [{"message": m.message, "is_bot": m.is_bot} for m in messages]
        return {"success": True, "chat_history": chat_history}
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def username_page(request: Request):
    # Landing page with username form
    return templates.TemplateResponse("username.html", {"request": request})

@app.get("/chatpage", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
