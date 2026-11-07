"""
Transparent, deterministic job matching against VERIFIED profile data only.

Every component returns (points, max_points, explanation). Missing job data is
never guessed: it gets half credit and is reported as "not stated".
"""
import hashlib
import re
from urllib.parse import urlsplit, urlunsplit

from .models import JobMatch, JobPreference, PrivateFact

# Vocabulary used to detect technologies in untrusted job text.
TECH_VOCAB = [
    "Python", "Django", "Django REST Framework", "DRF", "FastAPI", "Flask", "Celery", "Redis", "PostgreSQL", "MySQL",
    "SQLite", "MongoDB", "Docker", "Docker Compose", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Nginx", "Git",
    "GitHub", "GitLab", "CI/CD", "REST", "GraphQL", "JWT", "WebSockets", "Django Channels", "JavaScript", "TypeScript",
    "Vue.js", "Vue", "React", "Angular", "Node.js", "HTML", "CSS", "Bootstrap", "Tailwind", "PHP", "Laravel", "Java",
    "Spring", "C#", ".NET", "Go", "Golang", "Ruby", "Rails", "Elasticsearch", "RabbitMQ", "Kafka", "Terraform",
    "Microservices", "Pytest", "Unit testing", "PWA",
]
ALIASES = {"drf": "django rest framework", "vue": "vue.js", "golang": "go", "rest": "restful api design",
           "postgres": "postgresql", "websockets": "django channels (websockets)", "tailwind": "tailwind css",
           "html": "html5", "css": "css3"}
SENIORITY_WORDS = {"junior": ["junior", "entry", "graduate", "intern"], "mid": ["mid", "intermediate", "mid-level"],
                   "senior": ["senior", "sr.", "lead", "principal", "staff"]}


def normalize_url(url):
    parts = urlsplit(url.strip())
    query = "&".join(p for p in parts.query.split("&") if p and not p.lower().startswith(("utm_", "ref=", "source=", "trk")))
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), query, ""))


def url_hash(url):
    return hashlib.sha256(normalize_url(url).encode()).hexdigest()


def fingerprint(company, title, location=""):
    norm = lambda s: re.sub(r"[^a-z0-9؀-ۿ]+", " ", (s or "").lower()).strip()
    return hashlib.sha256(f"{norm(company)}|{norm(title)}|{norm(location)}".encode()).hexdigest()


def _canon(skill):
    s = skill.strip().lower()
    return ALIASES.get(s, s)


def verified_skills():
    """Skills from the public CV data (core.Skill active rows) + verified private facts."""
    from core.brand_content import SKILL_GROUPS
    skills = {_canon(s) for group in SKILL_GROUPS for s in group[3]}
    try:
        from core.models import Skill
        skills |= {_canon(n) for n in Skill.objects.filter(is_active=True).values_list("name", flat=True)}
    except Exception:  # core schema differences must not break matching
        pass
    return skills


def verified_years():
    fact = PrivateFact.objects.filter(section="identity", key="years-experience", status="verified").first()
    try:
        return int(re.match(r"\d+", fact.value_en).group()) if fact else None
    except (AttributeError, ValueError):
        return None


def extract_skills(text):
    found = []
    for tech in TECH_VOCAB:
        if re.search(r"(?<![\w.])" + re.escape(tech) + r"(?![\w])", text or "", re.IGNORECASE):
            found.append(tech)
    return found


def _has(skill, mine):
    c = _canon(skill)
    return c in mine or any(c in m or m in c for m in mine if len(m) > 3 and len(c) > 3)


def compute(job, preference=None, save=True):
    pref = preference or JobPreference.active()
    mine = verified_skills()
    required = job.required_skills or extract_skills(job.description)
    preferred = job.preferred_skills or []
    parts = {}

    # 1. Technical skills (40)
    if required:
        have = [s for s in required if _has(s, mine)]
        missing = [s for s in required if not _has(s, mine)]
        pts = round(30 * len(have) / len(required))
        if preferred:
            pts += round(10 * sum(_has(s, mine) for s in preferred) / len(preferred))
        else:
            pts += round(10 * len(have) / len(required))
        parts["skills"] = (pts, 40, f"Matches {len(have)}/{len(required)} required skills" +
                           (f"; missing: {', '.join(missing)}" if missing else ""), {"have": have, "missing": missing})
    else:
        parts["skills"] = (20, 40, "No skills stated or detected in the posting", {})

    # 2. Experience (15)
    years = verified_years()
    if job.min_years is None:
        parts["experience"] = (8, 15, "Experience requirement not stated", {})
    elif years is None:
        parts["experience"] = (8, 15, f"Job asks {job.min_years}+ years; your verified years are not recorded", {})
    else:
        ok = years >= job.min_years
        parts["experience"] = (15 if ok else max(0, 15 - 5 * (job.min_years - years)), 15,
                               f"Job asks {job.min_years}+ years; verified: {years}", {})

    # 3. Location / work mode (15)
    if not pref:
        parts["location"] = (8, 15, "No active job preference", {})
    else:
        loc_ok = (not pref.locations) or any(l.lower() in (job.location + " " + job.market).lower() for l in pref.locations)
        mode_ok = (not pref.work_modes) or job.work_mode in pref.work_modes or job.work_mode == "unknown"
        parts["location"] = ((10 if loc_ok else 0) + (5 if mode_ok else 0), 15,
                             f"Location {'matches' if loc_ok else 'outside'} preferences; work mode {job.get_work_mode_display()}", {})

    # 4. Seniority (10)
    text = f"{job.title} {job.seniority}".lower()
    detected = next((lvl for lvl, words in SENIORITY_WORDS.items() if any(w in text for w in words)), "")
    if not detected:
        parts["seniority"] = (5, 10, "Seniority not stated", {})
    elif pref and pref.seniority:
        parts["seniority"] = (10 if detected in pref.seniority else 2, 10, f"Posting looks {detected}; you target {', '.join(pref.seniority)}", {})
    else:
        parts["seniority"] = (5, 10, f"Posting looks {detected}; no seniority preference set", {})

    # 5. Language (5)
    lang = job.language_requirements.lower()
    if not lang:
        parts["language"] = (3, 5, "Language requirements not stated", {})
    else:
        fluent_only = any(w in lang for w in ("native english", "fluent english", "c1", "c2"))
        parts["language"] = (2 if fluent_only else 5, 5, f"Requires: {job.language_requirements} (your verified English: intermediate)" if fluent_only else f"Requires: {job.language_requirements}", {})

    # 6. Salary (5)
    if not job.salary_text:
        parts["salary"] = (3, 5, "Salary not published", {})
    elif pref and pref.salary_min:
        nums = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]{2,}", job.salary_text)]
        top = max(nums) if nums else None
        ok = top is None or top >= pref.salary_min
        parts["salary"] = (5 if ok else 0, 5, f"Published: {job.salary_text}", {})
    else:
        parts["salary"] = (3, 5, f"Published: {job.salary_text}; no salary preference set", {})

    # 7. Relevance (10)
    roles = [r.lower() for r in (pref.roles if pref else [])] or ["backend", "python", "django", "software engineer"]
    excluded = [t for t in (pref.excluded_tech if pref else []) if t.lower() in (job.description + job.title).lower()]
    rel = 10 if any(r in job.title.lower() for r in roles) else (5 if any(r in job.description.lower() for r in roles) else 0)
    if excluded:
        rel = 0
    parts["relevance"] = (rel, 10, ("Title matches a target role" if rel == 10 else "Partially relevant" if rel else "Not a target role") +
                          (f"; excluded technology present: {', '.join(excluded)}" if excluded else ""), {"excluded": excluded})

    score = sum(p[0] for p in parts.values())
    breakdown = {k: {"points": p[0], "max": p[1], "why": p[2], **p[3]} for k, p in parts.items()}
    if save:
        JobMatch.objects.update_or_create(job=job, defaults={"preference": pref, "score": score, "breakdown": breakdown})
    return score, breakdown
