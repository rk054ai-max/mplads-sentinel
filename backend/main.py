from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import works as works_router
from backend.api.routes import work as work_router

app = FastAPI(title="MPLADS Sentinel")

# Allow the frontend (likely served from file:// or localhost) to call the API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "mplads-sentinel"}


# Include API routers under /api/v1
app.include_router(works_router.router, prefix="/api/v1")
app.include_router(work_router.router, prefix="/api")
