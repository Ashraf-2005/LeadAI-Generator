import httpx
import sys
import os

# We can also verify directly in MongoDB using the database module
sys.path.append(os.path.dirname(__file__))
import database

def run_tests():
    print("=== STARTING INTEGRATION TESTS ===")
    
    # 1. Verify Database is using MongoDB (Atlas)
    database.init_db()
    if not database.USE_MONGODB:
        print("❌ ERROR: Database is not using MongoDB! It fell back to JSON.")
        sys.exit(1)
    print("✅ CONFIRMED: Connected to MongoDB Atlas successfully.")

    # Base URL for API
    base_url = "http://localhost:8000/api"
    
    # 2. Login to get JWT Token
    print("\n--- Testing Login ---")
    login_data = {
        "username": "sales",
        "password": "sales123"
    }
    response = httpx.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful.")

    # 3. Create a lead (Hot lead notes to trigger scoring and email generation)
    print("\n--- Testing Create Lead, Scoring & Email Generation ---")
    test_lead = {
        "company_name": "Atlas Cloud Test Inc",
        "industry": "Cloud Computing",
        "website": "https://atlas-test.com",
        "notes": "Urgent requirement. They need an AI lead scoring pipeline integrated immediately. Budget is $150k. The CTO requested a demo for next Monday. Extremely high intent."
    }
    
    response = httpx.post(f"{base_url}/leads/", json=test_lead, headers=headers, timeout=30.0)
    if response.status_code != 200:
        print(f"❌ Lead creation failed: {response.text}")
        sys.exit(1)
        
    lead_data = response.json()
    lead_id = lead_data["id"]
    print(f"✅ Lead created successfully with ID: {lead_id}")
    
    # Verify scoring pipeline
    score = lead_data.get("score")
    if not score:
        print("❌ Lead was not scored!")
        sys.exit(1)
        
    print(f"   Score Value: {score['score_value']}")
    print(f"   Score Label: {score['score_label']}")
    print(f"   Reason: {score['reason']}")
    print(f"   Suggested Contact Role: {score['suggested_contact_role']}")
    
    if score['score_value'] < 70:
        print("❌ Score value is lower than expected for high-intent notes.")
        sys.exit(1)
    print("✅ AI Scoring pipeline works correctly.")

    # Verify email generation
    email = lead_data.get("email")
    email_generated = lead_data.get("email_generated")
    print(f"   Email Generated Flag: {email_generated}")
    if not email_generated or not email:
        print("❌ Email was not generated for Hot/Warm lead!")
        sys.exit(1)
        
    print(f"   Email Subject: {email['subject']}")
    print(f"   Email Body Preview: {email['body'][:150]}...")
    print("✅ AI Email generation works correctly.")

    # 4. Verify presence in MongoDB Atlas directly via database driver
    print("\n--- Verifying Lead exists in Atlas Cluster ---")
    db_lead = database.get_lead(lead_id)
    if not db_lead:
        print(f"❌ Lead {lead_id} could not be found directly in the MongoDB Atlas database!")
        sys.exit(1)
    print(f"✅ Confirmed lead is saved in MongoDB Atlas. Company: {db_lead.company_name}")

    # 5. Verify Remove Lead feature
    print("\n--- Testing Remove Lead ---")
    del_response = httpx.delete(f"{base_url}/leads/{lead_id}", headers=headers)
    if del_response.status_code != 200:
        print(f"❌ Lead deletion failed: {del_response.text}")
        sys.exit(1)
    print("✅ Lead deleted via API successfully.")
    
    # Double check it is deleted from database
    deleted_lead = database.get_lead(lead_id)
    if deleted_lead:
        print("❌ Error: Lead still exists in database after deletion!")
        sys.exit(1)
    print("✅ Confirmed lead is no longer in MongoDB Atlas database.")
    
    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
