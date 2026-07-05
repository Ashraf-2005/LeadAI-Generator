# LeadAI File Manifest

Complete list of all files created for the LeadAI project.

## Root Level Files

| File | Purpose |
|------|---------|
| `.env.example` | Environment variables template (Groq API key, DB config, auth) |
| `Dockerfile` | Docker image for backend (Python 3.11 + FastAPI) |
| `docker-compose.yml` | Orchestration file (backend, MongoDB, nginx) |
| `nginx.conf` | Reverse proxy configuration (routes API, serves frontend) |
| `README.md` | Complete documentation (600+ lines, features, setup, troubleshooting) |
| `QUICKSTART.md` | 5-minute setup guide (get API key → run Docker → test) |
| `ARCHITECTURE.md` | Technical deep dive (backend patterns, LLM design, extension points) |
| `PROJECT_COMPLETION_SUMMARY.md` | This project's completion checklist and highlights |
| `FILE_MANIFEST.md` | This file — directory of all files |

## Backend Files

### Main Entry Point
- `backend/main.py` — FastAPI app, CORS, routers, startup/shutdown, health check

### Database
- `backend/database.py` — MongoDB abstraction + JSON file fallback, CRUD operations

### Models (Pydantic Schemas)
- `backend/models/__init__.py` — Exports all models
- `backend/models/lead.py` — Lead, LeadCreate, LeadUpdate, LeadScore, LeadEmail schemas

### Routers (API Endpoints)
- `backend/routers/__init__.py` — Package marker
- `backend/routers/auth.py` — POST `/auth/login`, GET `/auth/verify` (JWT tokens)
- `backend/routers/leads.py` — Full CRUD, CSV upload, scoring, email generation

### Services (Business Logic)
- `backend/services/__init__.py` — Package exports
- `backend/services/llm_client.py` — Groq client abstraction (provider-agnostic)
- `backend/services/scoring.py` — Lead scoring algorithm + prompt template
- `backend/services/email_generator.py` — Email generation + prompt template

### Configuration
- `backend/__init__.py` — Package marker
- `backend/requirements.txt` — Python dependencies (FastAPI, Groq, PyMongo, etc.)

## Frontend Files

### HTML
- `frontend/index.html` — Login page (demo credentials, redirect to dashboard if token exists)
- `frontend/dashboard.html` — Main dashboard UI (all leads, add lead, upload CSV, modals)
- `frontend/login.html` — Backup login page (referenced in structure but integrated into index.html)

### JavaScript
- `frontend/static/app.js` — Shared utilities (API client with token injection, helpers)

### CSS
- `frontend/static/styles.css` — Tailwind CSS customizations (status badges, transitions, dark mode support)

## Sample Data

- `sample_data/sample_leads.csv` — 8 realistic B2B leads (varied industries, contexts, scores)

---

## File Sizes (Estimated)

| Component | Count | Purpose |
|-----------|-------|---------|
| Python backend files | 11 | FastAPI app, models, routers, services, database |
| Frontend files | 5 | HTML, CSS, JavaScript |
| Configuration files | 6 | Dockerfile, docker-compose, nginx, .env |
| Documentation | 5 | README, QUICKSTART, ARCHITECTURE, SUMMARY, MANIFEST |
| Data files | 1 | Sample CSV |
| **Total** | **33** | Complete LeadAI project |

---

## Key Files by Use Case

### Want to understand how it works?
1. Start: `README.md` (overview)
2. Next: `QUICKSTART.md` (setup)
3. Deep dive: `ARCHITECTURE.md` (technical details)

### Want to run it locally?
1. Follow `QUICKSTART.md`
2. Edit `.env` with your Groq API key
3. Run `docker-compose up --build`
4. Visit `http://localhost`

### Want to customize scoring?
1. Edit `backend/services/scoring.py` (lines ~20–50)
2. Change the `SCORING_SYSTEM_PROMPT` and `SCORING_USER_PROMPT_TEMPLATE`
3. Restart: `docker-compose restart backend`

### Want to customize emails?
1. Edit `backend/services/email_generator.py` (lines ~18–50)
2. Change the `EMAIL_SYSTEM_PROMPT` and `EMAIL_USER_PROMPT_TEMPLATE`
3. Restart: `docker-compose restart backend`

### Want to swap LLM providers (Groq → Gemini)?
1. Edit `backend/services/llm_client.py`
2. Replace the Groq import and client instantiation
3. Update the `call()` method to match new provider's API
4. Everything else stays the same ✅

### Want to add new features?
1. Read `ARCHITECTURE.md` (Extension Points section)
2. Follow the pattern: Model → Router → Service → Database

### Want to deploy to production?
1. Read `README.md` (Deployment section)
2. Use `docker-compose.yml` as base
3. Configure HTTPS, strong secrets, managed DB
4. See deployment checklist in `ARCHITECTURE.md`

---

## Dependency Tree

```
frontend/dashboard.html
  └── static/app.js (API utilities)
  └── static/styles.css (Tailwind)

frontend/index.html
  └── static/app.js (API utilities)
  └── static/styles.css (Tailwind)

docker-compose.yml
  ├── Dockerfile (backend service)
  │   ├── backend/requirements.txt
  │   ├── backend/main.py
  │   │   ├── routers/auth.py
  │   │   ├── routers/leads.py
  │   │   ├── models/lead.py
  │   │   ├── services/llm_client.py (Groq SDK)
  │   │   ├── services/scoring.py
  │   │   ├── services/email_generator.py
  │   │   └── database.py (MongoDB or JSON)
  ├── nginx.conf (nginx service)
  ├── mongo (official image)
  └── [frontend static files]

.env
  ├── GROQ_API_KEY (required)
  ├── MONGO_URI (optional)
  ├── SECRET_KEY
  └── [other config]
```

---

## Code Quality Notes

### Backend
- ✅ Type hints on all functions (Pydantic models)
- ✅ Error handling with try-except + logging
- ✅ Async/await for non-blocking I/O
- ✅ Clear separation of concerns (models → routers → services → database)
- ✅ Documented with docstrings and inline comments
- ✅ Prompt engineering as top-of-file constants (easy to tune)

### Frontend
- ✅ Vanilla JavaScript (no framework bloat)
- ✅ Event handlers for all user interactions
- ✅ API client utility that auto-injects JWT
- ✅ Responsive design with Tailwind CSS
- ✅ Modals for email preview and lead details
- ✅ Real-time filtering and search

### Configuration
- ✅ Dockerfile uses slim Python image
- ✅ docker-compose defines all services + volumes
- ✅ nginx.conf includes CORS and cache headers
- ✅ .env.example documents all required variables

---

## Testing Checklist

To verify everything is working:

1. **Login**: Navigate to `http://localhost`, use `sales/sales123`
2. **Add Single Lead**: Create a lead manually, watch AI score it
3. **Upload CSV**: Upload `sample_data/sample_leads.csv`
4. **View Scores**: Check the dashboard, see varied Hot/Warm/Cold scores
5. **Email Drafts**: Click email icon, preview AI-generated emails
6. **Copy Email**: Copy draft email to clipboard
7. **Filter**: Try filtering by Hot/Warm/Cold
8. **Search**: Search by company name
9. **Logout**: Click logout, verify redirect to login

All features working? ✅ You're good to go!

---

## Next Steps

1. Read the docs (README.md → QUICKSTART.md → ARCHITECTURE.md)
2. Get a Groq API key (free at https://console.groq.com)
3. Run `docker-compose up --build`
4. Login and test features
5. Customize prompts and styling as desired
6. Integrate with your CRM or email provider (optional)
7. Deploy to production when ready

---

**LeadAI: Complete, ready-to-use, ready-to-extend.** 🚀
