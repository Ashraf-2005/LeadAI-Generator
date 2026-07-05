# LeadAI Architecture & Design Decisions

## Overview

LeadAI is a full-stack B2B SaaS application built with modern, production-ready patterns. This document explains the key architectural decisions and how to extend/maintain the system.

---

## Backend Architecture

### FastAPI Choice

**Why FastAPI?**
- Async-first (non-blocking I/O for AI API calls)
- Auto-generated OpenAPI docs (`/docs`)
- Built-in validation with Pydantic
- Excellent JSON serialization out of the box
- Modern Python ecosystem
- Easy to test and extend

**Structure:**
```
backend/
├── main.py               # App initialization, routers, startup/shutdown
├── models/               # Pydantic schemas (request/response contracts)
├── routers/              # Route handlers (auth, leads CRUD)
├── services/             # Business logic (LLM, scoring, emails)
└── database.py           # Data persistence (MongoDB + JSON fallback)
```

### Separation of Concerns

1. **Models** (`models/lead.py`): Data contracts
   - Ensures type safety across API
   - Pydantic auto-validates on every request

2. **Routers** (`routers/`): HTTP endpoints
   - Handles auth middleware
   - Delegates business logic to services
   - Returns standardized responses

3. **Services** (`services/`): Business logic
   - `llm_client.py`: LLM abstraction (easily swap providers)
   - `scoring.py`: Lead scoring algorithm + prompt
   - `email_generator.py`: Email drafting + prompt
   - All are async-capable

4. **Database** (`database.py`): Persistence abstraction
   - MongoDB for production
   - JSON file fallback for MVP
   - Could be extended to PostgreSQL, DynamoDB, etc. with minimal changes

---

## LLM Integration

### LLM Client Design (Provider-Agnostic)

**File:** `backend/services/llm_client.py`

```python
class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=...)  # <- Swap this for Gemini, Claude, etc.
    
    def call(self, system_prompt, user_message, temperature):
        # Generic call interface
        # Returns raw text
    
    def parse_json_response(self, response, expected_keys):
        # Robust JSON parsing with fallback
```

**To swap Groq → Gemini:**
1. Replace `from groq import Groq` with your provider's SDK
2. Update `__init__` to instantiate that client
3. Update `call()` to use the new API
4. Everything else stays the same ✅

### Prompt Engineering Philosophy

**Core principle:** Prevent hallucination

1. **Scoring Prompt** (`services/scoring.py`):
   - Explicit instruction: "Do not fabricate facts"
   - Grounds AI in only provided fields
   - Returns strict JSON structure
   - Lower temperature (0.3) for consistency

2. **Email Prompt** (`services/email_generator.py`):
   - Teaches AI to use placeholders instead of inventing
   - Marks output as "draft for human review"
   - Enforces word limit
   - Slightly higher temperature (0.5) for natural language

**Both prompts are top-of-file constants** — easy to edit and tune.

### Error Handling

- LLM API calls wrapped in try-except
- JSON parsing failures trigger retry (once)
- After retry, fallback to safe default with error flag
- Fallback values logged and visible in dashboard

---

## Frontend Architecture

### Single-Page App (SPA) Pattern

**Approach:** Vanilla JavaScript (no framework)
- Lightweight (~200 KB total)
- Fast initial load
- Works on all browsers
- Easy to customize

**Structure:**
```
frontend/
├── index.html          # Login page (checks token, redirects to dashboard)
├── dashboard.html      # Main UI (leads list, forms, modals)
└── static/
    ├── app.js          # Shared utilities + API client
    └── styles.css      # Tailwind + custom styles
```

### API Client Pattern

**File:** `static/app.js`

```javascript
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    // Automatically attaches JWT token to every request
    // Redirects to login if 401 (unauthorized)
}
```

**Benefits:**
- Consistent error handling
- Automatic token injection
- Single point to add logging/telemetry

### Dashboard Patterns

1. **Tabs**: Switch between views without page reload
2. **Modals**: Email preview, lead details, confirmations
3. **Filtering**: Real-time filter by score + search
4. **Status badges**: Visual indicators (Hot/Warm/Cold)

### UI Components

Built with **Tailwind CSS** (utility-first):
- No custom component library
- Responsive grid system
- Dark mode support ready (theme toggle stub)

---

## Database Design

### Schema (Lead Document)

```python
{
    "id": "unique-id",
    "company_name": "Acme Corp",
    "industry": "SaaS",
    "website": "https://acme.com",
    "notes": "Looking for lead scoring...",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "score": {
        "score_label": "Warm",
        "score_value": 75,
        "reason": "Active interest, industry fit...",
        "suggested_contact_role": "VP Sales"
    },
    "email": {
        "subject": "Let's help Acme scale faster",
        "body": "Hi there,\n\n..."
    },
    "email_generated": true,
    "email_sent": false,
    "notes_from_user": "Sent on Jan 15, waiting response"
}
```

### MongoDB vs. JSON Fallback

**MongoDB (Production)**:
- Scalable
- Indexed queries
- Atomic updates
- Built-in replication

**JSON Fallback (MVP)**:
- Zero setup required
- File-based persistence (`data/leads.json`)
- Suitable for <1000 leads
- No external dependencies

**Switch at runtime** via connection attempt in `database.py`.

---

## Authentication (MVP Single-Role)

**Current:** Hardcoded username/password
```python
VALID_USERNAME = "sales"
VALID_PASSWORD = "sales123"
```

**Future upgrade path:**
```python
# Option 1: Database of users
users_db = {
    "sales1": {"password_hash": "...", "role": "sales"},
    "admin1": {"password_hash": "...", "role": "admin"}
}

# Option 2: OAuth2 (Google, Okta, Azure AD)
# FastAPI has built-in OAuth2 support

# Option 3: SAML/OIDC for enterprise
```

**JWT flow:**
1. POST `/auth/login` → verify credentials
2. Return access token (24-hour expiry)
3. Frontend stores in localStorage
4. Every API call includes: `Authorization: Bearer <token>`
5. Backend validates token signature + expiry

---

## API Design

### REST Conventions

```
GET    /leads              # List all leads
GET    /leads/{id}         # Get single lead
POST   /leads              # Create lead (auto-score + email)
PATCH  /leads/{id}         # Update lead (mark sent, add notes)
DELETE /leads/{id}         # Delete lead

POST   /leads/bulk/upload  # CSV import (multipart form)
POST   /leads/{id}/score   # Re-score lead
POST   /leads/{id}/email   # Regenerate email

POST   /auth/login         # Get JWT token
GET    /auth/verify        # Check token validity
```

### Error Responses

```json
{
    "detail": "Lead not found"
}
```

**Status codes:**
- `200 OK` – Success
- `201 Created` – Resource created
- `400 Bad Request` – Invalid input
- `401 Unauthorized` – Missing/expired token
- `404 Not Found` – Resource not found
- `500 Internal Server Error` – Server error

---

## Async Patterns

**Why async?**
- LLM API calls (~500ms–2s latency)
- Without async, each request blocks the thread
- With async, server handles multiple requests concurrently

**Usage:**
```python
@router.post("/leads/")
async def create_lead(lead_create: LeadCreate):
    # Perform database write
    lead = database.create_lead(lead_create)
    
    # Async LLM call (doesn't block other requests)
    score = await score_lead(...)
    
    # Update database
    database.update_lead(lead.id, {"score": score.dict()})
    
    return lead
```

---

## Docker Deployment

### Services

**Dockerfile** (Backend):
- Python 3.11 slim base
- Installs dependencies from `requirements.txt`
- Runs `uvicorn` on port 8000

**docker-compose.yml**:
```yaml
services:
  backend:    # FastAPI app
  mongo:      # MongoDB (optional)
  nginx:      # Reverse proxy + static files
```

**Why Nginx?**
- Serves static frontend (HTML, CSS, JS)
- Reverse proxy to backend API
- Single entry point (`:80`)
- Easy SSL/TLS termination

**nginx.conf logic:**
```
GET  /           → frontend/index.html
GET  /static/*   → frontend/static/*
GET  /api/*      → backend:8000
```

---

## Extension Points

### 1. Add a New Feature

Example: "Save email templates"

1. **Model** → Add `EmailTemplate` in `models/lead.py`
2. **Router** → Add `/templates` routes in `routers/leads.py`
3. **Database** → Add collection in `database.py`
4. **Frontend** → Add tab in `dashboard.html`
5. **API client** → Update `app.js` utility

### 2. Add New LLM Provider

1. Edit `services/llm_client.py`
2. Replace Groq import + instantiation
3. Update `call()` method signature
4. Test with existing prompts

### 3. Add Role-Based Access Control (RBAC)

1. Update `auth.py` to check user role
2. Add middleware to check permissions per route
3. Database: add `role` field to users
4. Frontend: conditionally show admin-only tabs

### 4. Integrate with CRM (Salesforce, HubSpot)

1. Add `services/crm_client.py`
2. Implement sync logic in `routers/leads.py` (webhook listener or scheduled job)
3. Map LeadAI → CRM fields
4. Add UI toggle "Sync to CRM"

### 5. Add Email Sending (SendGrid, Mailgun)

1. Add `services/email_client.py`
2. Button → "Send Email" (instead of just copy)
3. Track opens/clicks via CRM webhook
4. Update lead status automatically

---

## Performance Considerations

### Current Bottlenecks

1. **LLM API latency**: 500ms–2s per lead
   - Mitigated by async (doesn't block server)
   - Could add background job queue for bulk operations

2. **JSON file I/O**: Reading/writing entire file on every operation
   - Mitigated by MongoDB fallback
   - Upgrade to MongoDB for production

3. **Frontend search**: Linear search on all leads
   - Mitigated by small dataset (MVP)
   - Add API-side search + pagination for scale

### Optimization Ideas (Future)

- **Job queue** (Celery, Bull): Batch score/email in background
- **Caching**: Cache LLM responses for similar leads
- **Pagination**: `GET /leads?page=1&limit=20`
- **Elasticsearch**: Full-text search on notes
- **CDN**: Serve static assets from edge

---

## Security Checklist

- ✅ JWT token validation on every request
- ✅ CORS headers (adjust `*` for production)
- ✅ No secrets in code (all in `.env`)
- ✅ Input validation (Pydantic)
- ⚠️ **TODO for production:**
  - Enable HTTPS/TLS
  - Rate limiting
  - CSRF protection
  - Sanitize user inputs in emails
  - Audit logging
  - Database encryption at rest

---

## Monitoring & Logging

**Current logging:**
- Python standard `logging` module
- INFO level by default
- Backend logs visible in `docker-compose logs`

**Ideas for production:**
- Ship logs to CloudWatch, Datadog, or ELK
- Alert on error spikes
- Track LLM API latency
- Monitor database query performance

---

## Testing Strategy

**Current:** No tests (MVP scope)

**Recommended test structure:**
```
backend/tests/
├── test_auth.py         # Login, token validation
├── test_leads.py        # CRUD operations
├── test_scoring.py      # Score logic + mock LLM
├── test_email_gen.py    # Email generation + mock LLM
└── conftest.py          # Pytest fixtures, mocks
```

**Run tests:**
```bash
pytest backend/tests/ -v
```

---

## Deployment Checklist

- [ ] Set `ENV=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Remove `*` CORS origins
- [ ] Use MongoDB Atlas (or managed DB)
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring
- [ ] Load test (k6, JMeter)
- [ ] Backup database
- [ ] Document runbooks (deploy, rollback, disaster recovery)

---

## Questions?

Refer to:
- [README.md](./README.md) – Feature overview
- [QUICKSTART.md](./QUICKSTART.md) – Getting started
- Code comments in each service file

---

**LeadAI: Built for developers, designed for scale.** 🚀
