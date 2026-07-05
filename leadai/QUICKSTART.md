# LeadAI Quick Start Guide

Get up and running with LeadAI in 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- A Groq API key (free tier available at https://console.groq.com)

## Step 1: Get Your Groq API Key

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up (free) or log in
3. Create an API key
4. Copy it (you'll need it in Step 2)

## Step 2: Configure Environment

Create a `.env` file in the `leadai/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here_change_in_production
SALES_USERNAME=sales
SALES_PASSWORD=sales123
ENV=development
```

## Step 3: Start LeadAI

```bash
docker-compose up --build
```

Wait for output like:
```
backend      | INFO:     Application startup complete
nginx        | ...started...
```

This spins up:
- **Backend API** (FastAPI): http://localhost:8000
- **Frontend**: http://localhost (or http://127.0.0.1)
- **MongoDB**: localhost:27017 (optional; falls back to JSON if unavailable)
- **API Documentation**: http://localhost:8000/docs

## Step 4: Login

1. Open http://localhost in your browser
2. Login with:
   - **Username**: `sales`
   - **Password**: `sales123`

## Step 5: Try It Out

### Option A: Add a Single Lead

1. Click **"Add Lead"** tab
2. Fill in:
   - **Company**: Acme Corp
   - **Industry**: SaaS
   - **Website**: https://acme.com (optional)
   - **Notes**: "We talked to their CTO at TechConf. They mentioned they need better lead scoring. Budget is $50k/year. Very interested, wants a demo."
3. Click **"Add Lead"**
4. Watch the AI automatically score it and generate an email ✨

### Option B: Upload Sample CSV

1. Click **"Upload CSV"** tab
2. Click **"Download Sample CSV"** link
3. Upload the downloaded file
4. Watch LeadAI score all 8 leads and generate emails 📊

## Step 6: Review & Manage Leads

On the **"All Leads"** tab:
- 🔴 **Hot** leads: Score ≥ 80 (high priority)
- 🟡 **Warm** leads: Score 50–79 (follow up)
- 🔵 **Cold** leads: Score < 50 (low priority)

For each lead:
- **👁️ View** details
- **📧 Preview** the AI-generated email draft
- **📋 Copy** to clipboard
- **✓ Mark** as sent once you reach out

## Next Steps

### Advanced Features

- **Re-score**: Open a lead, click "Re-score" to recalculate score
- **Regenerate email**: Open a lead, click "Regenerate Email" for a new draft
- **Delete**: Remove unwanted leads
- **Search**: Find leads by company name
- **Filter**: Show only Hot, Warm, or Cold leads

### Configuration

- **Adjust scoring threshold**: Edit `LEAD_SCORE_THRESHOLD` in `.env` (default 70)
  - Leads scoring below this won't auto-generate emails
- **Change auth credentials**: Edit `SALES_USERNAME` and `SALES_PASSWORD` in `.env`
- **Tune AI behavior**: Edit prompts in:
  - `backend/services/scoring.py` (scoring logic)
  - `backend/services/email_generator.py` (email generation)

### Deployment

When ready for production:
1. Set `ENV=production` in `.env`
2. Use a strong `SECRET_KEY`
3. Use MongoDB Atlas (cloud) instead of local MongoDB
4. Configure HTTPS/TLS in Nginx
5. Restrict CORS origins (remove `*` in `main.py`)

## Troubleshooting

### "Connection refused" when accessing dashboard
- Check Docker is running: `docker ps`
- Check all services are up: `docker-compose logs`
- Wait a few seconds for services to fully start

### "GROQ_API_KEY not found"
- Verify `.env` file exists with your API key
- Restart: `docker-compose restart backend`

### "Failed to connect to MongoDB"
- Normal — LeadAI falls back to JSON file storage automatically
- Leads stored in `data/leads.json`
- Check `docker-compose logs mongo` if concerned

### No leads showing after upload
- Check browser console (F12) for errors
- Check backend logs: `docker-compose logs backend`
- Try refreshing the page

### Email drafts not appearing
- Lead's score must be ≥ `LEAD_SCORE_THRESHOLD` (default 70)
- Try lowering threshold: set `LEAD_SCORE_THRESHOLD=50` in `.env` and restart

## Stopping LeadAI

```bash
docker-compose down
```

To remove volumes (data):
```bash
docker-compose down -v
```

## Full Documentation

See [README.md](./README.md) for:
- Complete feature overview
- Architecture & tech stack
- Detailed setup instructions
- Prompt engineering guide
- Deployment options
- Known limitations
- Future roadmap

---

**You're all set! Start adding leads and let AI help qualify them.** 🚀

Questions? Check the [Troubleshooting](./README.md#troubleshooting) section in README.md.
