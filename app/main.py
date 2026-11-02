
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1 import api_router
from app.core.database import get_db

app = FastAPI(
    title="DueMate API",
    description="Subscription, bill, and document expiry reminders.",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": "duemate",
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )
