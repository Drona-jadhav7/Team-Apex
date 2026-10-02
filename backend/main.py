from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import application from backend.app.main
from backend.app.main import app as superindia_app
from backend.app.core.config import settings

# Ensure CORSMiddleware is fully configured to accept requests from tunneled public domains
# (e.g. *.trycloudflare.com, *.loca.lt, and localhost)
app = superindia_app

# Re-affirm CORS configuration for any direct imports of backend.main:app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)