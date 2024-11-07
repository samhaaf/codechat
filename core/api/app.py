from fastapi import FastAPI, Depends, Request, HTTPException, Header
from starlette.responses import JSONResponse
from .schema import schema
from .db import get_db, engine  # Assuming engine is imported from your db module
from .auth import requires_access_token
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import auth
from . import graphql

app = FastAPI()

# Include submodule router(s)
app.include_router(auth.router, prefix="/_auth")
app.include_router(graphwl.router, prefix="/_graphql")

@app.post("/_ping")
async def status():
    return JSONResponse(content={
        'status': 'success'
    })
