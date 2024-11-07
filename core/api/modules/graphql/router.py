from fastapi import FastAPI, Depends,  Response, Request, HTTPException, Header

from starlette.responses import JSONResponse
from .schema import schema
from .db import get_db, engine  # Assuming engine is imported from your db module
from .auth import requires_access_token
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import auth

app = FastAPI()

# Global variable to store the last connection check time
last_db_check_time = None

# Include submodule router(s)
app.include_router(auth.router, prefix="/auth")

router = APIRouter()


@router.post("/")
@auth.requires_access_token
async def graphql_endpoint(request: Request, db: Session = Depends(get_db), access_token=None):
    global last_db_check_time

    # Check if we need to test the DB connection
    current_time = datetime.now()
    if last_db_check_time is None or (current_time - last_db_check_time) > timedelta(minutes=10):
        print('Checking database connection..')
        try:
            # Try pinging the DB to see if it's reachable
            engine.ping()
            # Update the last check time
            last_db_check_time = current_time
            print('Connected to db.')
        except:
            print('Database was unreachable.')
            # If DB is not reachable, return a 500 error
            raise HTTPException(status_code=500, detail="Database is not reachable")

    body = await request.json()
    query = body.get("query")
    variables = body.get("variables")
    context_value = {
        "session": db,
        "user_uid": auth.decode_token(x_access_token)['user_uid']
    }
    result = await schema.execute_async(
        query,
        variables=variables,
        context_value=context_value
    )
    response = {
        "data": result.data,
        "errors": [str(err) for err in result.errors] if result.errors else None,
        "status": "success" if not result.errors else "error",
    }

    return JSONResponse(content=response)
