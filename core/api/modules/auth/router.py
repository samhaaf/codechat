from fastapi import APIRouter, Header, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from .utils import (
    check_password_hash,
    new_password_hash,
    create_refresh_token,
    requires_access_token,
    decode_token,
    get_user,
    update_user,
    create_user,
    get_new_token_headers,
    invalidate_refresh_tokens,
    verify_token
)
from pydantic import BaseModel
import json

router = APIRouter()


class LoginInput(BaseModel):
    email: str
    password: str


class SetPasswordInput(BaseModel):
    email: str
    old_password: str
    new_password: str


class CreateUserInput(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(data: LoginInput, response: Response):
    if not check_password_hash(data.email, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = get_user(data.email)

    if user['needs_new_password']:
        return JSONResponse(
            status_code=401,
            content={
                'status': 'error',
                'needs_new_password': True,
                'error': 'Need to update your password.'
            }
        )

    # Update the headers with new tokens
    token_headers = get_new_token_headers(user["uid"])
    for cookie_name, cookie_value in token_headers.items():
        response.set_cookie(key=cookie_name, value=cookie_value, httponly=True, secure=False, samesite='Strict', path='/')

    response.headers["content-type"] = "application/json"
    response.body = json.dumps({
        'status': 'success',
        'needs_new_password': False
    }).encode('utf-8')
    response.status_code = 200

    return response


@router.get("/get_token_headers")
@requires_refresh_token
async def get_token_headers(response: Response, refresh_token=None):

    user = get_user(refresh_token['user_uid'])

    if user['needs_new_password']:
        raise HTTPException(status_code=403, detail="New password required.")

    token_headers = get_new_token_headers(user_uid)
    for cookie_name, cookie_value in token_headers.items():
        response.set_cookie(key=cookie_name, value=cookie_value, httponly=True, secure=False, samesite='Strict', path='/')

    response_content = {
        'status': 'success'
    }
    response.body = json.dumps(response_content).encode('utf-8')
    response.headers["content-type"] = "application/json"
    response.status_code = 200

    return response


@router.post("/set_password")
async def set_password(data: SetPasswordInput):
    if not check_password_hash(data.email, data.old_password):
        raise HTTPException(status_code=401, detail="Invalid old password")

    update_user(data.email, {
        'needs_new_password': False,
        'password_hash': new_password_hash(data.new_password)
    })

    return {
        "status": "success",
        "detail": "Password updated successfully"
    }


@router.post("/me")
@requires_access_token
async def me(acces_token=None):
    return {
        'status': 'success',
        'user_uid': access_token['user_uid']
    }


@router.post("/logout")
@requires_refresh_token
async def logout(refresh_token=None):

    invalidate_refresh_tokens(refresh_token_uid=refresh_token['uid'])

    return {
        "status": "success",
        "detail": "Successfully logged out"
    }


@router.post("/logout_everywhere")
@requires_refresh_token
async def logout_everywhere(refresh_token=None):

    invalidate_refresh_tokens(user_uid=refresh_token['user_uid'])

    return {
        "status": "success",
        "detail": "Successfully logged out from all devices"
    }


@router.post("/create_user")
@requires_access_token
async def create_user(data: CreateUserInput, access_token=None):

    user = get_user(access_token['user_uid'])

    if not user['is_admin']:
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    # Create the new user
    create_user(data.email, data.password)

    return {
        "status": "success",
        "detail": "User created successfully"
    }
