from fastapi import FastAPI

from backend.api.location import router as location_router

from backend.api.water import router as water_router

app = FastAPI(
    title="India AI Grid API",
    description="AI infrastructure intelligence backend for India",
    version="0.1.0",
)


app.include_router(location_router)


@app.get("/")
def root():
    return {
        "name": "India AI Grid API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }

app.include_router(water_router)