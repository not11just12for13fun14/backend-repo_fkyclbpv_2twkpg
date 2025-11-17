import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Member, Equipment, Reservation, Report

app = FastAPI(title="BUA Lier – Utlån av utstyr API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "BUA-style API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                response["collections"] = db.list_collection_names()
                response["connection_status"] = "Connected"
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"
    return response


# --------- Public catalog endpoints ---------
class EquipmentQuery(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None


@app.get("/api/equipment")
def list_equipment(q: Optional[str] = None, category: Optional[str] = None, location: Optional[str] = None):
    """Simple catalog query over title, tags, category, location"""
    try:
        filter_dict: dict = {"is_active": True}
        if category:
            filter_dict["category"] = {"$regex": f"^{category}$", "$options": "i"}
        if location:
            filter_dict["location"] = {"$regex": f"^{location}$", "$options": "i"}
        if q:
            filter_dict["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
                {"category": {"$regex": q, "$options": "i"}},
            ]
        items = get_documents("equipment", filter_dict)
        # Convert ObjectId to string
        for item in items:
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/equipment")
def create_equipment(payload: Equipment):
    try:
        new_id = create_document("equipment", payload)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- Membership ---------
@app.post("/api/members")
def create_member(payload: Member):
    try:
        new_id = create_document("member", payload)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- Reservations ---------
@app.post("/api/reservations")
def create_reservation(payload: Reservation):
    try:
        new_id = create_document("reservation", payload)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- Reports (donation/repair) ---------
@app.post("/api/reports")
def create_report(payload: Report):
    try:
        new_id = create_document("report", payload)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
