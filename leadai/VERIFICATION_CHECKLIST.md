# ✅ LeadAI Verification Checklist

## Pre-Deployment Verification

### 1. Services Running
- [ ] Docker containers started: `docker ps` shows 3 containers (backend, mongo, nginx)
- [ ] Backend log shows: `✓ Backend initialized`
- [ ] Backend log shows: `Uvicorn running on http://0.0.0.0:8000`

### 2. Authentication
- [ ] Can access login page at http://localhost:8000
- [ ] Login with credentials: `sales / sales123`
- [ ] Dashboard loads after login
- [ ] Can logout

### 3. CSV Upload
- [ ] Navigate to "Upload CSV" tab
- [ ] Click to upload sample_data/sample_leads.csv
- [ ] Upload shows "✓ Imported X leads"
- [ ] No upload errors displayed

### 4. AI Scoring
- [ ] After 30-60 seconds, refresh dashboard
- [ ] Leads now show score labels (Hot/Warm/Cold)
- [ ] Scores range from 0-100
- [ ] Each lead shows suggested contact role

### 5. Dashboard Sorting
- [ ] 🔴 HOT leads appear at top
- [ ] 🟡 WARM leads appear in middle
- [ ] 🔵 COLD leads appear below
- [ ] Pending leads appear last

### 6. Filtering
- [ ] "All" filter shows all leads
- [ ] "Hot" filter shows only Hot leads
- [ ] "Warm" filter shows only Warm leads
- [ ] "Cold" filter shows only Cold leads

### 7. Search
- [ ] Type company name in search box
- [ ] Leads filter by company name
- [ ] Search is case-insensitive

### 8. Email Generation
- [ ] Hot leads show "✓ Ready" in Email column
- [ ] Click 📧 icon for Hot leads
- [ ] Email modal shows subject and body
- [ ] Email is personalized to the company

### 9. Lead Details
- [ ] Click 👁️ icon on any lead
- [ ] Lead details modal shows all information
- [ ] Score reasoning is displayed
- [ ] Can delete lead from modal

### 10. Data Persistence
- [ ] Refresh page (F5)
- [ ] All leads still visible
- [ ] Scores are preserved
- [ ] Logout and login again
- [ ] All leads still in database

---

## Performance Checks

### Scoring Speed
- [ ] First 3 leads score within 15 seconds
- [ ] All 8 sample leads score within 60 seconds
- [ ] No timeout errors in backend logs

### API Response Time
- [ ] List leads: <500ms
- [ ] Login: <200ms
- [ ] Single lead fetch: <100ms

### Database Performance
- [ ] Can handle 100+ leads
- [ ] No duplicate leads after clean upload
- [ ] Database persists across restarts

---

## Error Handling

### Invalid Uploads
- [ ] CSV with missing required fields shows error
- [ ] Invalid email format shows error
- [ ] Empty file shows error

### Authentication
- [ ] Wrong password shows error
- [ ] Expired token prompts re-login
- [ ] Missing token returns 401

### Lead Operations
- [ ] Delete non-existent lead shows error
- [ ] Update non-existent lead shows error
- [ ] Invalid data format shows validation error

---

## API Tests (Using Curl)

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"sales","password":"sales123"}'
# Expected: 200 OK with access_token
```

### Test List Leads
```bash
curl -X GET http://localhost:8000/api/leads/ \
  -H "Authorization: Bearer <your_token>"
# Expected: 200 OK with array of leads
```

### Test Health
```bash
curl http://localhost:8000/health
# Expected: 200 OK with {"status": "healthy"}
```

---

## Browser Console Checks

1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Expected errors: NONE
4. Warnings are OK if from third-party libraries

---

## Final Verification

When all checkboxes are complete:

✅ **LeadAI is fully operational and ready for use!**

### Ready for Production?
- [ ] All checklist items completed
- [ ] No errors in browser console
- [ ] No errors in backend logs
- [ ] CSV upload works consistently
- [ ] AI scoring completes in <60 seconds
- [ ] Dashboard displays correctly on target browsers

### Minimum Browser Support
- ✓ Chrome 90+
- ✓ Firefox 88+
- ✓ Safari 14+
- ✓ Edge 90+

### System Requirements
- ✓ Docker & Docker Compose installed
- ✓ 4GB RAM minimum (2GB Docker, 2GB system)
- ✓ 5GB disk space (MongoDB data)
- ✓ Internet connection (Groq API calls)
- ✓ Groq API key configured

---

## Sign-Off

- **Tested By**: [Your Name]
- **Date**: [Date]
- **Status**: ☐ Ready for Staging | ☐ Ready for Production
- **Notes**: 

---

**All systems go! 🚀 LeadAI is ready to qualify leads with AI!**
