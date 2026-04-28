import re
from typing import Dict, Any, List

ROLE_CATEGORIES = {
    "AI/ML Engineer": ["machine learning", "deep learning", "model training", "pytorch", "tensorflow", "mlops", "llm", "transformer", "neural network", "computer vision", "nlp", "feature engineering"],
    "Data Scientist": ["data analysis", "statistics", "a/b testing", "hypothesis", "pandas", "numpy", "jupyter", "r ", "matplotlib", "visualization", "regression", "classification"],
    "Backend Engineer": ["api", "microservices", "database", "sql", "postgresql", "redis", "docker", "kubernetes", "rest", "graphql", "system design"],
    "Frontend Engineer": ["react", "angular", "vue", "css", "html", "javascript", "typescript", "ui", "ux", "responsive"],
    "DevOps/MLOps": ["ci/cd", "deployment", "monitoring", "kubernetes", "terraform", "aws", "gcp", "azure", "pipeline", "automation"],
}

BENEFIT_KEYWORDS = ["salary", "equity", "stock", "remote", "hybrid", "401k", "health", "dental", "vision", "pto", "flexible", "bonus", "relocation", "visa"]

SENIORITY_SIGNALS = {
    "Junior / Entry": ["junior", "entry", "0-2 years", "1-2 years", "new grad", "recent graduate", "internship"],
    "Mid-Level": ["mid", "2-4 years", "3-5 years", "intermediate"],
    "Senior": ["senior", "5+ years", "4+ years", "lead", "principal"],
    "Staff / Director": ["staff", "director", "head of", "vp ", "vice president", "manager"],
}

RED_FLAGS = [
    ("rockstar", "Vague 'rockstar/ninja' culture language"),
    ("ninja", "Vague 'rockstar/ninja' culture language"),
    ("must know everything", "Unrealistic requirement breadth"),
    ("10+ years", "Potentially inflated experience requirements"),
    ("15+ years", "Very inflated experience requirements"),
    ("unpaid", "Unpaid work red flag"),
    ("equity only", "Equity-only compensation red flag"),
    ("wear many hats", "Possible understaffed team"),
]

def detect_role_type(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    for role, keywords in ROLE_CATEGORIES.items():
        scores[role] = sum(1 for k in keywords if k in text_lower)
    return max(scores, key=scores.get)

def extract_requirements(text: str) -> Dict[str, List[str]]:
    text_lower = text.lower()
    must_have, nice_have = [], []

    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower().strip()
        if any(w in line_lower for w in ["required", "must have", "must-have", "essential", "minimum"]):
            must_have.append(line.strip())
        elif any(w in line_lower for w in ["preferred", "nice to have", "plus", "bonus", "desired"]):
            nice_have.append(line.strip())

    return {
        "must_have": [r for r in must_have if len(r) > 5][:8],
        "nice_to_have": [r for r in nice_have if len(r) > 5][:6],
    }

def extract_skills_from_jd(text: str) -> List[str]:
    all_tech = [
        "python", "java", "javascript", "typescript", "go", "rust", "c++", "scala", "r",
        "pytorch", "tensorflow", "keras", "scikit-learn", "hugging face", "langchain",
        "react", "node.js", "fastapi", "django", "flask", "spring",
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "spark", "airflow", "dbt", "kafka", "mlflow", "wandb",
        "git", "linux", "bash", "rest api", "graphql"
    ]
    text_lower = text.lower()
    return [t for t in all_tech if t in text_lower]

def detect_red_flags(text: str) -> List[str]:
    text_lower = text.lower()
    return [msg for keyword, msg in RED_FLAGS if keyword in text_lower]

def extract_benefits(text: str) -> List[str]:
    text_lower = text.lower()
    found = [b for b in BENEFIT_KEYWORDS if b in text_lower]
    return found

def detect_seniority(text: str) -> str:
    text_lower = text.lower()
    for level, signals in SENIORITY_SIGNALS.items():
        if any(s in text_lower for s in signals):
            return level
    return "Not specified"

def compute_match_score(jd_text: str, resume_text: str) -> Dict[str, Any]:
    if not resume_text.strip():
        return {"score": None, "matched_skills": [], "missing_skills": []}
    jd_skills = set(extract_skills_from_jd(jd_text))
    resume_lower = resume_text.lower()
    matched = [s for s in jd_skills if s in resume_lower]
    missing = [s for s in jd_skills if s not in resume_lower]
    score = round((len(matched) / len(jd_skills)) * 100) if jd_skills else 0
    return {"score": score, "matched_skills": matched, "missing_skills": missing[:10]}

def generate_insights(text: str, role: str, skills: List[str], seniority: str) -> List[str]:
    insights = []
    text_lower = text.lower()

    if "remote" in text_lower:
        insights.append("✅ Remote work is mentioned — confirm if fully remote or hybrid.")
    if "visa" in text_lower or "sponsorship" in text_lower:
        insights.append("📋 Visa sponsorship mentioned — verify the details if you need it.")
    if len(skills) > 12:
        insights.append(f"⚠️ This role lists {len(skills)} tech skills — a high bar. Focus on the most critical ones.")
    if seniority == "Senior" and "3" not in text_lower:
        insights.append("👔 Senior role — emphasize leadership, architecture decisions, and mentoring in your application.")
    if "startup" in text_lower or "fast-paced" in text_lower:
        insights.append("🚀 Startup environment mentioned — expect broader responsibilities and faster pace.")
    if role == "AI/ML Engineer":
        insights.append("🤖 Strong AI/ML role — highlight model training, deployment, and any production ML experience.")
    if not insights:
        insights.append("📝 Read the full JD carefully and tailor your resume to match the top 3 required skills.")
    return insights[:5]

def analyze_job_description(jd_text: str, resume_text: str = "") -> Dict[str, Any]:
    role = detect_role_type(jd_text)
    skills = extract_skills_from_jd(jd_text)
    requirements = extract_requirements(jd_text)
    red_flags = detect_red_flags(jd_text)
    benefits = extract_benefits(jd_text)
    seniority = detect_seniority(jd_text)
    match = compute_match_score(jd_text, resume_text)
    insights = generate_insights(jd_text, role, skills, seniority)

    word_count = len(jd_text.split())
    complexity = "High" if word_count > 600 else "Medium" if word_count > 300 else "Low"

    return {
        "role_type": role,
        "seniority_level": seniority,
        "required_skills": skills,
        "requirements": requirements,
        "red_flags": red_flags,
        "benefits_mentioned": benefits,
        "match_score": match,
        "insights": insights,
        "stats": {
            "word_count": word_count,
            "complexity": complexity,
            "skills_required": len(skills),
            "red_flags_count": len(red_flags),
        }
    }
