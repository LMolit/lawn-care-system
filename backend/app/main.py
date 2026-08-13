from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.exceptions import NotFoundError, ConflictError
from app.routers import auth, leads

app = FastAPI()

app.include_router(auth.router)
app.include_router(leads.router)

@app.exception_handler(NotFoundError)
def not_found_handler(request, exc: NotFoundError):
    return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": exc.message, "detail": None},
            )

@app.exception_handler(ConflictError)
def conflict_handler(request, exc: ConflictError):
    return JSONResponse(
            status_code=409,
            content={"error": "conflict", "message": exc.message, "detail": None},
            )

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

