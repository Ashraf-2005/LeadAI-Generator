# LeadAI - AI-Powered Sales Lead Qualification & Email Assistant

## Problem Statement

Sales and marketing teams receive leads from many sources — website contact forms, LinkedIn, exhibitions, referrals, purchased lists — each with basic info like company name, website, industry, and notes about what they need. 

**The challenge:** Manually reviewing every lead to judge how promising it is, then writing a personalized outreach email for each one, is slow and inconsistent. Good opportunities get missed simply because there isn't time to give every lead proper attention.

## Solution

LeadAI is a web tool where sales people upload leads (CSV or manual entry) and AI automatically:

1. **Scores each lead** — Hot / Warm / Cold — with a clear, specific reason
2. **Suggests the likely decision-maker role** to target (e.g., CTO, Founder, Head of Operations)
3. **Drafts a personalized, ready-to-edit cold email** referencing that lead's specific industry/notes

The sales person reviews everything on a dashboard and manually approves/sends emails they like. **The AI assists and drafts — it does not auto-send anything. Human stays in the loop.**

---

## Core Features

### ✅ Lead Input
- **CSV upload** for bulk lead import (5–100+ leads at a time)
- **Manual entry form** for single leads
- Auto-parsing and validation of required fields

### ✅ AI Scoring
- Every lead gets a score: **Hot (80+), Warm (50–79), Cold (<50)** — plus 0–100 numeric score
- Written reason grounded strictly in the lead's provided fields (no fabrication)
- Suggested contact role (CTO, Founder, VP Sales, etc.)

### ✅ AI Email Generation
- Personalized cold emails for leads at or above a configurable threshold (default: Warm, 70+)
- References specific industry/notes naturally — not generic templated text
- Under 120 words, professional, includes clear CTA
- Marked as **draft for human review** — never implies already sent

### ✅ Dashboard
- List all leads with sortable/filterable score
- Search by company name
- Editable email preview before copy/send
- Mark emails as sent once you're confident

### ✅ Basic Auth (MVP)
- Single-role login (sales user)
- JWT-based session tokens
- No multi-role complexity (designed for small teams)

### ✅ Lead History
- All leads persisted with scores and emails
- Viewable across sessions
- Delete leads if needed

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Backend** | FastAPI (Python) | Async, modern, simple to extend |
| **LLM** | Groq (Llama 2/Mixtral) | Fast, API-based; one-file swap to Gemini |
| **Database** | MongoDB + JSON fallback | MongoDB for production; JSON file for MVP/local dev |
| **Frontend** | HTML, CSS, JavaScript + Tailwind | No heavy framework; responsive and lightweight |
| **Deployment** | Docker + docker-compose | One-command startup; includes Nginx reverse proxy |

---

## Project Structure

```
leadai/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # DB abstraction (MongoDB + JSON fallback)
│   ├── requirements.txt         # Python dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   └── lead.py             # Pydantic models (Lead, LeadScore, LeadEmail)
│   ├── routers/
│   │   ├── auth.py             # Login/token endpoints
│   │   └── leads.py            # CRUD + AI scoring/email generation
│   └── services/
│       ├── llm_client.py       # LLM abstraction (Groq/Gemini-ready)
│       ├── scoring.py          # Lead scoring logic & prompt
│       ├── email_generator.py  # Email generation logic & prompt
│       └── __init__.py
├── frontend/
│   ├── index.html              # Login page
│   ├── dashboard.html          # Main dashboard (leads, add, upload)
│   └── static/
│       ├── app.js              # Shared utilities + API client
│       └── styles.css          # Custom Tailwind styles
├── sample_data/
│   └── sample_leads.csv        # 8 realistic example leads
├── .env.example                # Environment variables template
├── Dockerfile                  # Docker image for backend
├── docker-compose.yml          # One-command startup: all services
├── nginx.conf                  # Reverse proxy & frontend serving
└── README.md                   # This file
```

---

## Setup & Installation

### Prerequisites
- Docker & Docker Compose (recommended)
- OR Python 3.11+ with pip (for local development)
- Groq API key (get free at [https://console.groq.com](https://console.groq.com))

### Option 1: Docker (Recommended)

1. **Clone or download** the project.

2. **Create `.env` file** from template:
   ```bash
   cp .env.example .env
   ```

3. **Add your Groq API key** to `.env`:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_secret_key_here_change_in_production
   ```

4. **Start all services**:
   ```bash
   docker-compose up --build
   ```

   This starts:
   - **Backend API**: `http://localhost:8000`
   - **Frontend**: `http://localhost`
   - **MongoDB**: `localhost:27017` (optional; falls back to JSON if down)
   - **API Docs**: `http://localhost:8000/docs`

5. **Login** at `http://localhost`:
   - Username: `sales`
   - Password: `sales123`

6. **Upload sample data**:
   - Go to the "Upload CSV" tab
   - Download and upload the sample CSV provided in the app

---

### Option 2: Local Development (No Docker)

1. **Create Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Create `.env`** file:
   ```bash
   cp .env.example .env
   ```

4. **Add Groq API key** to `.env`.

5. **Run backend**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

6. **Serve frontend** (separate terminal):
   - Open `frontend/index.html` in a browser, OR
   - Use a simple HTTP server: `python -m http.server 8080` in the `frontend/` directory

---

## Usage

### 1. Login
- Navigate to `http://localhost` (or your deployment URL)
- Use demo credentials: `sales` / `sales123`

### 2. Add a Single Lead
- Click **"Add Lead"** tab
- Fill in: Company Name, Industry, Website (optional), Notes
- Click **"Add Lead"**
- AI automatically scores the lead and generates an email (if score ≥ threshold)

### 3. Upload Leads (CSV)
- Click **"Upload CSV"** tab
- Download the sample CSV to see the format, or prepare your own:
  ```
  company_name,industry,website,notes
  Acme Corp,SaaS,https://acme.com,"Looking for lead scoring, mentioned budget concerns"
  ```
- Upload the file
- Bulk scoring and email generation happens automatically

### 4. Review & Manage Leads
- **All Leads** tab shows a table of all leads
- **Filter** by score (Hot, Warm, Cold) or search by company name
- **View lead details**: Click the eye icon
- **Preview email draft**: Click the email icon (for Warm+ leads)
- **Copy email**: Open draft, click "Copy Email", paste into your email client
- **Mark as sent**: Track which emails have been sent

### 5. Re-score or Regenerate Email
- Open lead details and click "Re-score" to recalculate the score
- Click "Regenerate Email" to draft a new version

---

## Prompt Engineering (Core Logic)

### Lead Scoring Prompt

Located in `backend/services/scoring.py`:

```python
SCORING_SYSTEM_PROMPT = """You are a senior B2B sales analyst...
CRITICAL: Do not assume, invent, or infer any facts not explicitly stated:
- Do not fabricate budget information
- Do not assume company size or stage
- Do not invent buying signals, timelines, or intent
- Ground your analysis ONLY in the provided fields

Return ONLY valid JSON...
"""
```

**Key design choices:**
- Explicit instruction to avoid hallucination
- Strict JSON-only output for reliable parsing
- Includes fallback/retry logic if JSON parsing fails
- Lower temperature (0.3) for consistent scoring

### Email Generation Prompt

Located in `backend/services/email_generator.py`:

```python
EMAIL_SYSTEM_PROMPT = """You are a skilled B2B sales copywriter...
- Reference specific details from the company's industry and notes naturally
- Keep under 120 words
- Use placeholders like [Your Product] where you lack specifics
- Always mark as draft for review
- Never imply the email has been sent
"""
```

**Key design choices:**
- Encourages personalization and natural references
- Strict word limit (under 120 words)
- Teaches model to use placeholders instead of inventing details
- Emphasizes "draft for human review" to set expectations
- Slightly higher temperature (0.5) for more natural, less robotic writing

Both prompts are editable constants at the top of their respective service files for easy tuning.

---

## Configuration

### Environment Variables (`.env`)

```bash
# Groq API
GROQ_API_KEY=your_api_key_here

# MongoDB (optional; falls back to JSON if unavailable)
MONGO_URI=mongodb://localhost:27017

# JWT / Security
SECRET_KEY=your_secret_key_here

# Auth (MVP)
SALES_USERNAME=sales
SALES_PASSWORD=sales123

# Scoring Threshold (score >= this value triggers email generation)
LEAD_SCORE_THRESHOLD=70

# Environment
ENV=development  # or production
```

### Scoring Threshold

- Default: **70** (Warm range)
- Only leads scoring ≥ 70 automatically get emails generated
- Adjust `LEAD_SCORE_THRESHOLD` in `.env` to change

### Swap LLM Provider (Groq → Gemini, etc.)

1. Edit `backend/services/llm_client.py`
2. Replace the `Groq` client with your provider's SDK (e.g., `google.generativeai`)
3. Update the `call()` method to use the new API
4. Rest of the codebase remains unchanged ✅

---

## Deployment

### Docker (Production-Ready)

1. Build and push image:
   ```bash
   docker build -t leadai:latest .
   docker push your-registry/leadai:latest
   ```

2. Deploy with `docker-compose`:
   ```bash
   docker-compose up -d
   ```

3. **Scale** (optional):
   - Run multiple backend instances with a load balancer
   - Use MongoDB Atlas (managed cloud DB) instead of local MongoDB

### Env-Specific Tips

- **Development**: `ENV=development` enables hot reload and verbose logging
- **Production**: 
  - Set `ENV=production`
  - Use strong `SECRET_KEY`
  - Enable HTTPS/TLS in Nginx
  - Use managed MongoDB or set up replication
  - Restrict CORS origins (not `*`)

---

## Known Limitations

### Scoring Quality Depends on Notes Richness
- The AI scores **only** using the fields provided. If notes are vague ("Interested in our services"), scoring will be conservative.
- **Mitigation**: Train your team to capture context during initial contact — pain points, company size hints, timeline signals, budget pointers.

### No Auto-Send by Design
- LeadAI generates drafts; sending is always manual. This prevents costly mistakes and maintains brand control.
- **Why**: "Human in the loop" is a feature, not a limitation — reduces liability and ensures quality.

### Single-Role MVP
- Only one login role (sales user) — no multi-team support or role-based access control.
- **Upgrade path**: Add admin/manager roles, audit logs, and team workspaces as your org scales.

### MongoDB Optional
- For MVP, LeadAI falls back to JSON file storage in `data/leads.json`. Perfect for <1000 leads.
- **Upgrade path**: MongoDB Atlas (cloud) for production and scalability.

### LLM Hallucination Risk
- Prompts explicitly forbid fabrication, but LLMs can still occasionally invent details.
- **Mitigation**: Humans always review scores and emails before action — not a blocker.

### No Real-Time Collaboration
- Single user at a time. Multiple concurrent sales reps would overwrite each other.
- **Upgrade path**: Implement websockets + conflict resolution if needed.

---

## Sample Data

`sample_data/sample_leads.csv` includes 8 realistic B2B leads with varied industries and contexts:

| Company | Industry | Context | Expected Score |
|---------|----------|---------|-----------------|
| Techwave Analytics | SaaS | Growing startup, $50k budget, clear pain | **Hot** |
| GreenEnergy Solutions | Clean Energy | Enterprise, 50-person sales team, slow response | **Warm** |
| FinTech Innovators | FinTech | Series B, $10M funding, expanding GTM | **Hot** |
| RetailMax Stores | Retail | 200+ locations, sales director interest, budget hesitant | **Warm** |
| CloudBase Inc | Cloud Infrastructure | Inbound lead volume issue, very engaged | **Hot** |
| HealthPlus Consulting | Healthcare | Healthcare sector, unresponsive after initial interest | **Cold** |
| DataDrive Systems | Data & Analytics | VC-backed, specific request for AI scoring | **Hot** |
| WorkFlow Pro | HR Tech | SMB target, cold outreach, budget constraints | **Cold** |

Use this to test the dashboard, filtering, scoring, and email generation.

---

## Testing the API

### Via FastAPI Docs
1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" and paste your access token (get via login endpoint)
3. Try endpoints: `/leads/`, `/leads/bulk/upload`, `/leads/{id}/score`, etc.

### Via cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"sales","password":"sales123"}'

# List leads (use token from login response)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/leads/
```

---

## Troubleshooting

### "GROQ_API_KEY not set"
- Check `.env` file has `GROQ_API_KEY=...`
- Restart backend: `docker-compose restart backend`

### "Failed to connect to MongoDB"
- MongoDB is optional. LeadAI falls back to JSON file storage automatically.
- Check Docker logs: `docker-compose logs mongo`
- Leads will be stored in `data/leads.json` if MongoDB is down.

### Frontend shows blank page
- Check browser console (F12) for errors
- Verify Nginx is running: `docker-compose logs nginx`
- Try hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)

### JSON parse error in LLM response
- Groq API occasionally returns malformed JSON
- LeadAI retries once, then falls back to safe default
- Check backend logs: `docker-compose logs backend`
- If persistent, lower `temperature` in `scoring.py` or `email_generator.py`

### Emails not generating for some leads
- Likely score is below threshold (default 70)
- Adjust `LEAD_SCORE_THRESHOLD` in `.env` and restart
- Or manually trigger: open lead details, click "Regenerate Email"

---

## Future Enhancements

1. **Multi-role RBAC**: Admin, manager, sales rep roles
2. **CRM integration**: Sync with Salesforce, HubSpot
3. **A/B email templates**: Test which email drafts get better responses
4. **Lead scoring feedback loop**: Improve AI based on "sent" vs "deleted" ratio
5. **Analytics dashboard**: Conversion funnel, response rates, best-performing templates
6. **Webhook / Zapier support**: Trigger on new leads from external sources
7. **Real-time collaboration**: Multiple users on dashboard (websockets)
8. **Custom scoring rules**: Industry-specific, territory-specific thresholds
9. **Email scheduling**: Schedule sends via common email providers

---

## Contributing

This is a portfolio project. Fork, extend, and share your improvements!

---

## License

MIT License — use freely for personal and commercial projects.

---

## Support

For issues or questions:
1. Check **Troubleshooting** section above
2. Review FastAPI logs: `docker-compose logs backend`
3. Check frontend browser console (F12 Developer Tools)
4. Inspect Docker container: `docker exec -it leadai-backend bash`

---

## Credits

Built with:
- **FastAPI** – Modern Python web framework
- **Groq API** – Fast LLM inference
- **MongoDB** – NoSQL database
- **Tailwind CSS** – Utility-first CSS
- **Docker** – Containerization

---

**LeadAI: Empower your sales team with AI-assisted lead qualification.** 🚀
