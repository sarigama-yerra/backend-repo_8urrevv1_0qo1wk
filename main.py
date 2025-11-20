import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone

app = FastAPI(title="Saikumar Dusa Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=5, max_length=2000)

# In a real app, you'd persist contact messages. We'll store them if DB is configured.
try:
    from database import db
except Exception:
    db = None

@app.get("/")
async def root():
    return {"message": "Portfolio API running", "owner": "Saikumar Dusa"}

@app.post("/api/contact")
async def submit_contact(payload: ContactMessage):
    doc = {
        **payload.model_dump(),
        "created_at": datetime.now(timezone.utc)
    }
    if db is not None:
        try:
            db["contact"].insert_one(doc)
            return {"ok": True, "stored": True}
        except Exception:
            return {"ok": True, "stored": False}
    return {"ok": True, "stored": False}

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
        from database import db as db_conn
        if db_conn is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db_conn.name if hasattr(db_conn, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db_conn.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
