# 🚀 LeadAI — START HERE

Welcome to LeadAI, an AI-powered sales lead qualification tool. This document gets you from zero to fully working in 5 minutes.

---

## What Is LeadAI?

LeadAI helps sales teams:
1. **Score leads** automatically (Hot/Warm/Cold) using AI
2. **Suggest contact roles** to target (CTO, Founder, VP Sales, etc.)
3. **Generate personalized email drafts** ready to send
4. **Manage leads** in one dashboard

**Key principle:** AI drafts, humans decide. All emails are reviewed before sending—no auto-send.

---

## ⚡ 5-Minute Quick Start

### Step 1: Get Your Groq API Key (1 min)

1. Go to https://console.groq.com
2. Sign up (free) or log in
3. Create an API key
4. Copy it

### Step 2: Configure LeadAI (1 min)

1. In the `leadai/` folder, copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and paste your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Step 3: Start LeadAI (2 min)

```bash
docker-compose up --build
```

Wait for output like:
```
backend | INFO:     Application startup complete
```

### Step 4: Login & Test (1 min)

1. Open http://localhost in your browser
2. Login with:
   - **Username**: `sales`
   - **Password**: `sales123`
3. Click "Upload CSV" → "Download Sample CSV" → upload it
4. Watch AI automatically score all leads and generate emails 🎉

---

## 📊 What Happens Next?

You'll see a dashboard with:

- **All Leads** tab: Table of leads with scores (Hot 🔴 / Warm 🟡 / Cold 🔵)
- **Add Lead** tab: Form to manually add one lead
- **Upload CSV** tab: Bulk import multiple leads

For each lead:
- 📊 **AI Score**: Hot/Warm/Cold + reason
- 👤 **Suggested Contact**: Who to reach out to
- 📧 **Email Draft**: Ready to copy and send

---

## 🎯 Next Steps

### Option 1: Explore More (15 minutes)

1. Try adding a single lead manually
2. View lead details (click 👁️)
3. Preview email drafts (click 📧)
4. Filter by score or search by company name

### Option 2: Understand How It Works (30 minutes)

Read these in order:
1. [QUICKSTART.md](./QUICKSTART.md) — Detailed 5-minute guide
2. [README.md](./README.md) — Complete feature overview
3. [ARCHITECTURE.md](./ARCHITECTURE.md) — Technical design (for developers)

### Option 3: Deploy to Production (1 hour)

Follow [README.md Deployment Section](./README.md#deployment)

### Option 4: Customize for Your Team (1-2 hours)

Edit these files to customize:
- **Scoring logic**: `backend/services/scoring.py`
- **Email templates**: `backend/services/email_generator.py`
- **Dashboard styling**: `frontend/static/styles.css`
- **Auth credentials**: `.env` file

---

## ❓ Common Questions

### Q: Do I need MongoDB installed?
**A:** No! LeadAI falls back to local file storage automatically. MongoDB is optional for production scale.

### Q: Can I change the AI scoring logic?
**A:** Yes! Edit `backend/services/scoring.py`. The prompt is at the top of the file, easy to customize.

### Q: How do I add more features?
**A:** See [ARCHITECTURE.md Extension Points](./ARCHITECTURE.md#extension-points) section.

### Q: Can I replace Groq with another AI provider?
**A:** Yes! Edit `backend/services/llm_client.py`. It's designed for easy provider swaps.

### Q: How do I stop LeadAI?
**A:** Press `Ctrl+C` in the terminal where `docker-compose up` is running. Or:
```bash
docker-compose down
```

### Q: How do I see the API documentation?
**A:** Visit http://localhost:8000/docs (FastAPI auto-generates it)

---

## 🐛 Troubleshooting

### "Connection refused" when accessing dashboard
- ✅ Check Docker is running: `docker ps`
- ✅ Check all services are up: `docker-compose logs`
- ✅ Wait 10 seconds, services need time to start

### "GROQ_API_KEY not found" error
- ✅ Check `.env` file exists and has your key
- ✅ Restart: `docker-compose restart backend`

### "Failed to connect to MongoDB"
- ✅ Normal! LeadAI uses local JSON storage if MongoDB is down
- ✅ Leads still save to `data/leads.json`

### No emails generated for some leads
- ✅ Lead score must be ≥ 70 (configurable in `.env`)
- ✅ Adjust `LEAD_SCORE_THRESHOLD=50` and restart

**More troubleshooting?** See [README.md Troubleshooting](./README.md#troubleshooting)

---

## 📁 Project Structure

```
leadai/
├── START_HERE.md              ← You are here
├── QUICKSTART.md              ← Detailed 5-min guide
├── README.md                  ← Full documentation
├── ARCHITECTURE.md            ← Technical deep dive
├── .env.example               ← Copy to .env, add Groq API key
├── docker-compose.yml         ← Run with: docker-compose up --build
├── Dockerfile                 ← Backend container
├── nginx.conf                 ← Reverse proxy
├── backend/                   ← FastAPI app
│   ├── main.py
│   ├── models/                ← Data schemas
│   ├── routers/               ← API endpoints
│   ├── services/              ← AI scoring & emails
│   └── database.py            ← MongoDB + JSON storage
├── frontend/                  ← Dashboard UI
│   ├── index.html             ← Login page
│   ├── dashboard.html         ← Main dashboard
│   └── static/                ← CSS, JavaScript
└── sample_data/               ← Example CSV to test with
```

---

## 🎓 Key Concepts

### Lead Score
- **Hot (80–100)**: High priority, clear buying signals
- **Warm (50–79)**: Moderate interest, follow up soon
- **Cold (0–49)**: Low priority, check back later

### Email Generation
- AI drafts personalized cold emails (under 120 words)
- Marked as "draft for human review" (not auto-sent)
- References industry + specific lead notes
- Uses placeholders like [Your Product] where it lacks info

### Database
- **MongoDB**: Production-ready, scalable
- **JSON file**: Local storage, no setup needed
- LeadAI uses MongoDB if available, falls back to JSON automatically

---

## 💡 Tips

1. **Rich notes = better AI**: The more context in lead notes, the better the scoring and emails
2. **Review before sending**: Always edit AI-generated emails before sending
3. **Tune the threshold**: Lower `LEAD_SCORE_THRESHOLD` in `.env` if you want more email generation
4. **Retry scoring**: If score seems off, open the lead and click "Re-score"
5. **Save samples**: Copy well-written email drafts as examples for the AI to learn from

---

## 🚀 You're Ready!

1. Get your Groq API key (1 min)
2. Configure `.env` (1 min)
3. Run `docker-compose up --build` (2 min)
4. Login and upload sample CSV (1 min)

**Total: 5 minutes to your first working lead qualification system.**

---

## 📚 Documentation Map

- **START_HERE.md** (this file) — Quick overview & getting started
- **QUICKSTART.md** — Detailed 5-minute setup walkthrough
- **README.md** — Complete feature guide & troubleshooting
- **ARCHITECTURE.md** — Technical design for developers
- **FILE_MANIFEST.md** — Complete file listing
- **PROJECT_COMPLETION_SUMMARY.md** — Full project checklist

---

## 🎉 What's Next?

✅ Got it running? → Explore the dashboard, upload leads, preview emails

✅ Want to learn more? → Read [QUICKSTART.md](./QUICKSTART.md)

✅ Want to customize? → Read [ARCHITECTURE.md](./ARCHITECTURE.md)

✅ Want full docs? → Read [README.md](./README.md)

---

**Questions?** Every question is answered in one of the docs above. Happy selling! 🚀

---

**LeadAI: AI assists, humans decide. Simple. Effective. Ready to scale.** 💪
