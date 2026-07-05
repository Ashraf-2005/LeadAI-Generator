import os
import json
from datetime import datetime
from typing import List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from models.lead import Lead, LeadCreate
import logging

logger = logging.getLogger(__name__)

# Try MongoDB, fall back to JSON file
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
USE_MONGODB = True
mongo_client = None
db = None

# JSON file storage (fallback)
JSON_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "leads.json")


def init_db():
    """Initialize database connection."""
    global mongo_client, db, USE_MONGODB
    
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        mongo_client.admin.command('ping')
        db = mongo_client['leadai']
        logger.info("✓ Connected to MongoDB")
        USE_MONGODB = True
    except (ConnectionFailure, Exception) as e:
        logger.warning(f"MongoDB connection failed: {e}. Using JSON file storage.")
        USE_MONGODB = False
        os.makedirs(os.path.dirname(JSON_DB_PATH), exist_ok=True)
        if not os.path.exists(JSON_DB_PATH):
            with open(JSON_DB_PATH, 'w') as f:
                json.dump({"leads": []}, f)


def _get_leads_from_json() -> List[dict]:
    """Read leads from JSON file."""
    if not os.path.exists(JSON_DB_PATH):
        return []
    with open(JSON_DB_PATH, 'r') as f:
        data = json.load(f)
    return data.get("leads", [])


def _save_leads_to_json(leads: List[dict]):
    """Save leads to JSON file."""
    os.makedirs(os.path.dirname(JSON_DB_PATH), exist_ok=True)
    with open(JSON_DB_PATH, 'w') as f:
        json.dump({"leads": leads}, f, indent=2, default=str)


def create_lead(lead_create: LeadCreate) -> Lead:
    """Create a new lead."""
    lead_dict = lead_create.dict()
    lead_dict["created_at"] = datetime.utcnow()
    lead_dict["updated_at"] = datetime.utcnow()
    lead_dict["email_generated"] = False
    lead_dict["email_sent"] = False
    
    if USE_MONGODB and db is not None:
        result = db['leads'].insert_one(lead_dict)
        lead_dict["id"] = str(result.inserted_id)
    else:
        leads = _get_leads_from_json()
        lead_dict["id"] = str(len(leads) + 1)
        leads.append(lead_dict)
        _save_leads_to_json(leads)
    
    return Lead(**lead_dict)


def get_lead(lead_id: str) -> Optional[Lead]:
    """Retrieve a single lead by ID."""
    if USE_MONGODB and db is not None:
        from bson.objectid import ObjectId
        try:
            lead_doc = db['leads'].find_one({"_id": ObjectId(lead_id)})
            if lead_doc:
                lead_doc["id"] = str(lead_doc.pop("_id"))
                return Lead(**lead_doc)
        except Exception as e:
            logger.error(f"Error fetching lead from MongoDB: {e}")
    else:
        leads = _get_leads_from_json()
        for lead in leads:
            if lead.get("id") == lead_id:
                return Lead(**lead)
    return None


def get_all_leads() -> List[Lead]:
    """Retrieve all leads."""
    if USE_MONGODB and db is not None:
        leads = []
        for lead_doc in db['leads'].find():
            lead_doc["id"] = str(lead_doc.pop("_id"))
            leads.append(Lead(**lead_doc))
        return leads
    else:
        leads_data = _get_leads_from_json()
        return [Lead(**lead) for lead in leads_data]


def update_lead(lead_id: str, lead_data: dict) -> Optional[Lead]:
    """Update a lead."""
    lead_data["updated_at"] = datetime.utcnow()
    
    if USE_MONGODB and db is not None:
        from bson.objectid import ObjectId
        try:
            result = db['leads'].find_one_and_update(
                {"_id": ObjectId(lead_id)},
                {"$set": lead_data},
                return_document=True
            )
            if result:
                result["id"] = str(result.pop("_id"))
                return Lead(**result)
        except Exception as e:
            logger.error(f"Error updating lead in MongoDB: {e}")
    else:
        leads = _get_leads_from_json()
        for i, lead in enumerate(leads):
            if lead.get("id") == lead_id:
                lead.update(lead_data)
                _save_leads_to_json(leads)
                return Lead(**lead)
    return None


def delete_lead(lead_id: str) -> bool:
    """Delete a lead."""
    if USE_MONGODB and db is not None:
        from bson.objectid import ObjectId
        try:
            result = db['leads'].delete_one({"_id": ObjectId(lead_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting lead from MongoDB: {e}")
    else:
        leads = _get_leads_from_json()
        original_len = len(leads)
        leads = [l for l in leads if l.get("id") != lead_id]
        if len(leads) < original_len:
            _save_leads_to_json(leads)
            return True
    return False


def search_leads_by_name(name: str) -> List[Lead]:
    """Search for leads by company name (case-insensitive)."""
    if USE_MONGODB and db is not None:
        import re
        query = {"company_name": re.compile(f"^{re.escape(name)}$", re.IGNORECASE)}
        leads = []
        for lead_doc in db['leads'].find(query):
            lead_doc["id"] = str(lead_doc.pop("_id"))
            leads.append(Lead(**lead_doc))
        return leads
    else:
        leads_data = _get_leads_from_json()
        name_lower = name.lower()
        results = [l for l in leads_data if l.get("company_name", "").lower() == name_lower]
        return [Lead(**l) for l in results]
