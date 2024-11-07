import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from functools import wraps
import bcrypt
from .. import db
from ..config import Config
import uuid


# Secret key for JWT encoding
JWT_SECRET = Config.JWT_SECRET


def get_user(email):
    query = "SELECT * FROM logscale.user WHERE $and(%s)"
    user = db.execute(query, [{"email": email}])
    return user[0] if user else None


def update_user(email, values):
    query = f"UPDATE logscale.user SET $set(%s) WHERE email = %s"
    db.execute(query, [values, email])


def check_password_hash(email, password):
    user = get_user(email)
    print(f"Debug - Email: {email}, Password: {password}, User: {user}")

    if user:
        stored_password_hash = user['password_hash'].encode('utf-8')
        print(f"Debug - Stored Password Hash: {stored_password_hash}")

        return bcrypt.checkpw(password.encode('utf-8'), stored_password_hash)
        
    else:
        print("User not found.")
        return False


def new_password_hash(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    return hashed_password


def set_password_hash(email, password):
    hashed_password = new_password_hash(password).decode('utf-8')
    update_user(email, {'password_hash': hashed_password})


def is_admin(email):
    user = get_user(email)
    return user['is_admin'] if user else False


def create_refresh_token(user_uid):
    # Create a new UUID for this specific refresh token
    new_uid = uuid.uuid4()

    # Generate the JWT payload
    payload = {
        "user_uid": user_uid,
        "type": "refresh",
        "uid": str(new_uid),  # Use the newly generated UUID
        "issued": int(datetime.now().timestamp()),
        "ttl": 3600 * 24 * 7,
    }

    # Encode the JWT token
    encoded_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    # Insert the new refresh token into the database
    query = """
        INSERT INTO logscale.refresh_token ($columns(%0))
        VALUES $values(%0);
    """
    values = {k:v for k,v in payload.items() if k in ['user_uid', 'uid', 'ttl']}
    db.execute(query, [values])

    return encoded_token


def create_access_token(user_uid):
    payload = {
        "user_uid": user_uid,
        "type": "access",
        "uid": "access_uid",
        "issued": int(datetime.now().timestamp()),
        "ttl": 3600 * 5,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(encoded_token):
    decoded_token = jwt.decode(encoded_token, JWT_SECRET, algorithms=["HS256"])
    if decoded_token["issued"] + decoded_token["ttl"] <= int(datetime.now().timestamp()):
        return None
    # decoded_token["current_time"] = int(datetime.now().timestamp())
    return decoded_token


def verify_token(encoded_token, do_raise=True):
    decoded_token = decode_token(encoded_token)

    # General check for token validity
    if decoded_token is None:
        if do_raise:
            raise HTTPException(status_code=403, detail="Expired or invalid token")
        return False

    # Check if token has expired
    issued_timestamp = datetime.fromtimestamp(decoded_token['issued'])
    ttl = timedelta(seconds=decoded_token['ttl'])
    if issued_timestamp + ttl <= datetime.now():
        if do_raise:
            raise HTTPException(status_code=403, detail="Token has expired")
        return False

    # Specific check for refresh tokens
    if decoded_token['type'] == 'refresh':
        query = """
            SELECT is_invalidated, issued_timestamp, ttl
            FROM logscale.refresh_token
            WHERE uid = %s
        """
        refresh_token_data = db.execute(query, values=[decoded_token['uid']])

        if not refresh_token_data:
            if do_raise:
                raise HTTPException(status_code=403, detail="Invalid refresh token")
            return False

        is_invalidated, _, _ = refresh_token_data[0].values()
        if is_invalidated:
            if do_raise:
                raise HTTPException(status_code=403, detail="Refresh token has been invalidated")
            return False

    return True




def get_new_token_headers(user_uid: str):
    headers = {}
    headers["X_Refresh_Token"] = create_refresh_token(user_uid)
    headers["X_Access_Token"] = create_access_token(user_uid)
    return headers


def invalidate_refresh_tokens(refresh_token_uid=None, user_uid=None):
    """
    Invalidate refresh tokens based on either refresh_token_uid or user_uid.

    :param refresh_token_uid: The unique identifier for the refresh token.
    :param user_uid: The unique identifier for the user.
    """
    if refresh_token_uid:
        # Invalidate the specific refresh token by its UID
        query = "UPDATE logscale.refresh_token SET invalidated = TRUE WHERE uid = %s"
        db.execute(query, values=[refresh_token_uid])
    elif user_uid:
        # Invalidate all refresh tokens associated with a specific user
        query = "UPDATE logscale.refresh_token SET invalidated = TRUE WHERE user_uid = %s"
        db.execute(query, values=[user_uid])
    else:
        raise ValueError("Either refresh_token_uid or user_uid must be provided.")


def create_user(email, password):
    hashed_password = new_password_hash(password).decode('utf-8')
    query = """
        INSERT INTO logscale.user (email, password_hash, is_admin)
        VALUES (%s, %s, %s);
    """
    try:
        db.execute(query, values=[email, hashed_password, False])  # Assuming new users are not admins by default
    except Exception as e:
        # You can also specify the type of exception based on what your DB library might raise
        raise HTTPException(status_code=400, detail=str(e))
