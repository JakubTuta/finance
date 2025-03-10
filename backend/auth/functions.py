import datetime
import os
import typing

import bson
import fastapi
from fastapi.security import OAuth2PasswordBearer
from helpers import database
from jose import JWTError, jwt
from passlib.context import CryptContext

from . import models

ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
REFRESH_TOKEN_EXPIRE_HOURS = 24 * 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# CREATE TOKENS


def _generate_token(
    secret_key: typing.Optional[str],
    token_type: typing.Literal["access", "refresh"],
    expire_hours: int,
    user: typing.Optional[models.User] = None,
    user_id: typing.Optional[str] = None,
) -> typing.Optional[str]:
    if secret_key is None:
        return None

    if user is not None and user.id is not None:
        user_id = str(user.id)

    elif user_id is None:
        return None

    expires = datetime.datetime.now() + datetime.timedelta(hours=expire_hours)

    payload = {
        "sub": str(user_id),
        "token_type": token_type,
        "exp": int(expires.timestamp()),
    }

    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)


def generate_access_token(**kwargs) -> typing.Optional[str]:
    return _generate_token(
        ACCESS_SECRET_KEY, "access", ACCESS_TOKEN_EXPIRE_HOURS, **kwargs
    )


def generate_refresh_token(**kwargs) -> typing.Optional[str]:
    return _generate_token(
        REFRESH_SECRET_KEY, "refresh", REFRESH_TOKEN_EXPIRE_HOURS, **kwargs
    )


def generate_tokens(**kwargs) -> typing.Optional[models.TokenPair]:
    access_token = generate_access_token(**kwargs)
    refresh_token = generate_refresh_token(**kwargs)

    if access_token is None or refresh_token is None:
        return None

    return models.TokenPair(access=access_token, refresh=refresh_token)


# REFRESH TOKEN


def refresh_access_token(refresh_token: str) -> typing.Optional[str]:
    if REFRESH_SECRET_KEY is None or ACCESS_SECRET_KEY is None:
        return None

    if not verify_refresh_token(refresh_token):
        return None

    payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")

    if user_id is None:
        return None

    return generate_access_token(user_id=user_id)


# DECODE TOKENS


def decode_token(
    token: str, token_type: typing.Literal["access", "refresh"]
) -> typing.Dict[str, typing.Any]:
    secret_key = ACCESS_SECRET_KEY if token_type == "access" else REFRESH_SECRET_KEY

    if secret_key is None:
        return {}

    try:
        return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return {}


# VERIFY TOKENS


def verify_token(token: str, token_type: typing.Literal["access", "refresh"]) -> bool:
    secret_key = ACCESS_SECRET_KEY if token_type == "access" else REFRESH_SECRET_KEY

    if secret_key is None:
        return False

    try:
        payload = jwt.decode(token, secret_key, algorithms=ALGORITHM)

        exp = payload.get("exp")
        current_time = int(datetime.datetime.now().timestamp())

        return (
            payload.get("token_type") == token_type
            and payload.get("sub") is not None
            and exp is not None
            and exp > current_time
        )

    except JWTError as e:
        return False


def verify_access_token(token: str) -> bool:
    return verify_token(token, "access")


def verify_refresh_token(token: str) -> bool:
    return verify_token(token, "refresh")


# TOKEN EXPIRATION


def is_token_expired(
    token: str, token_type: typing.Literal["access", "refresh"]
) -> bool:
    secret_key = ACCESS_SECRET_KEY if token_type == "access" else REFRESH_SECRET_KEY

    if secret_key is None:
        return True

    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        exp = payload.get("exp")

        if exp is None:
            return True

        return exp < int(datetime.datetime.now().timestamp())

    except JWTError:
        return True


def is_access_token_expired(token: str) -> bool:
    return is_token_expired(token, "access")


def is_refresh_token_expired(token: str) -> bool:
    return is_token_expired(token, "refresh")


# USER


async def find_user(
    user_id: typing.Optional[str] = None, username: typing.Optional[str] = None
) -> typing.Optional[models.User]:
    collection = database.get_collection("users")
    if user_id is not None:
        user = await collection.find_one({"_id": bson.ObjectId(user_id)})

    elif username is not None:
        user = await collection.find_one({"username": username})

    else:
        return None

    if user is None:
        return None

    return models.User(**user)


async def create_user(username: str, password: str) -> models.User:
    collection = database.get_collection("users")

    user = models.User(username=username, password=get_password_hash(password))

    result = await collection.insert_one(user.model_dump())

    user.id = result.inserted_id

    return user


async def get_current_user(
    token: str = fastapi.Depends(OAuth2PasswordBearer(tokenUrl="/auth/token")),
) -> models.User:
    if not verify_access_token(token):
        raise fastapi.HTTPException(status_code=401, detail="Invalid token")

    payload = decode_token(token, "access")
    user_id = str(payload.get("sub"))

    if (user := await find_user(user_id=user_id)) is None:
        raise fastapi.HTTPException(status_code=401, detail="User not found")

    return user


async def update_user(current_user: models.User, request_data: models.UserRequest):
    collection = database.get_collection("users")

    if request_data.username is not None:
        current_user.username = request_data.username

    if request_data.currency is not None:
        current_user.currency = request_data.currency

    await collection.update_one(
        {"_id": bson.ObjectId(current_user.id)},
        {
            "$set": {
                "username": current_user.username,
                "currency": current_user.currency,
            }
        },
    )

    return current_user
