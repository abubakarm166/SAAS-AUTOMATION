from fastapi import FastAPI

from app.routers import auth, billing, health, jobs, worker

app = FastAPI(title="SnapShot API", version="0.1.0")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(billing.router)
app.include_router(worker.router)
