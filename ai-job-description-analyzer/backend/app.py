from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from jd_analyzer import analyze_job_description

app = FastAPI(title="AI Job Description Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class JDRequest(BaseModel):
    job_description: str
    resume_text: str = ""

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("../frontend/index.html") as f:
        return f.read()

@app.post("/analyze")
async def analyze(req: JDRequest):
    if len(req.job_description.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description too short")
    result = analyze_job_description(req.job_description, req.resume_text)
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}
