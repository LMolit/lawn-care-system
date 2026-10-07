from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import RateLimitError
from app.dependencies import get_db
from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.routers import (
    analytics,
    auth,
    customers,
    expenses,
    invoices,
    jobs,
    leads,
    payments,
    properties,
    reviews,
    routes,
    services,
)

app = FastAPI()

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(reviews.router)
app.include_router(customers.router)
app.include_router(properties.router)
app.include_router(services.router)
app.include_router(jobs.router)
app.include_router(routes.router)
app.include_router(invoices.router)
app.include_router(payments.router)
app.include_router(expenses.router)
app.include_router(analytics.router)


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


@app.exception_handler(ValidationError)
def validation_error_handler(request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "validation_error", "message": exc.message, "detail": None},
    )


@app.exception_handler(RateLimitError)
def rate_limit_handler(request, exc: RateLimitError):
    return JSONResponse(
        status_code=429,
        content={"error": "rate_limited", "message": exc.message, "detail": None},
        headers={"Retry-After": str(exc.retry_after)},
    )
