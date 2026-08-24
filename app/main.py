"""
ForensicRecover — Main Application Entry Point
Digital Evidence Recovery, Verification, Preservation & Investigation Platform
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.database.database import init_db, async_session
from app.models.user import User
from app.utils.security import hash_password

from app.api import auth, cases, evidence, recovery, integrity, custody, reports, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    await init_db()
    await seed_admin_user()

    # Ensure required directories exist
    os.makedirs("forensic/images", exist_ok=True)
    os.makedirs("forensic/recovered", exist_ok=True)
    os.makedirs("forensic/test-data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    print("=" * 60)
    print("  ForensicRecover -- Platform Ready")
    print("  URL: http://127.0.0.1:8000")
    print("  Admin: admin / ForensicAdmin@2026")
    print("=" * 60)

    yield

    # Shutdown
    print("ForensicRecover shutting down...")


app = FastAPI(
    title="ForensicRecover",
    description="Digital Evidence Recovery, Verification, Preservation & Investigation Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(recovery.router)
app.include_router(integrity.router)
app.include_router(custody.router)
app.include_router(reports.router)
app.include_router(dashboard.router)

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")


@app.get("/")
async def serve_login():
    """Serve the login page."""
    return FileResponse(os.path.join(frontend_dir, "index.html"))


@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse(os.path.join(frontend_dir, "dashboard.html"))


@app.get("/cases")
async def serve_cases():
    return FileResponse(os.path.join(frontend_dir, "cases.html"))


@app.get("/evidence")
async def serve_evidence():
    return FileResponse(os.path.join(frontend_dir, "evidence.html"))


@app.get("/recovery")
async def serve_recovery():
    return FileResponse(os.path.join(frontend_dir, "recovery.html"))


@app.get("/custody")
async def serve_custody():
    return FileResponse(os.path.join(frontend_dir, "custody.html"))


@app.get("/reports")
async def serve_reports():
    return FileResponse(os.path.join(frontend_dir, "reports.html"))


async def seed_admin_user():
    """Create the default admin user on first run."""
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin = User(
                name="System Administrator",
                username="admin",
                password_hash=hash_password("ForensicAdmin@2026"),
                role="ADMIN",
            )
            db.add(admin)
            await db.commit()
            print("  [OK] Default admin user created")
