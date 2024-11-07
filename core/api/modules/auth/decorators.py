from ..decorators import fastapi_decorator


@fastapi_decorator
def requires_refresh_token(func):

    @wraps(func)
    async def wrapper(*args, request: Request = Depends(), **kwargs):
        x_refresh_token = request.cookies.get('X_Refresh_Token')

        if not x_refresh_token:
            print('403: No refresh token.')
            raise HTTPException(status_code=403, detail="No refresh token. Please login.")

        verify_token(x_refresh_token)

        return await func(*args, refresh_token = decode_token(x_refresh_token), **kwargs)

    return wrapper


@fastapi_decorator
def requires_access_token(func):

    async def wrapper(*args, request: Request, **kwargs):
        x_access_token = kwargs['request'].cookies.get('X_Access_Token')

        if not x_access_token:
            print('403: No access token.')
            raise HTTPException(status_code=403, detail="No access token. Please login.")

        verify_token(x_access_token)

        return await func(*args, access_token = decode_token(x_access_token), **kwargs)

    return wrapper
