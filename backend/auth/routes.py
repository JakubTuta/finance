import typing

import fastapi
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import functions, models

router = fastapi.APIRouter(prefix="/auth")


@router.post(
    "/login",
    response_model=typing.Dict[str, typing.Union[models.User, models.TokenPair]],
)
async def login(
    form_data: OAuth2PasswordRequestForm = fastapi.Depends(),
) -> typing.Dict[str, typing.Union[models.User, models.TokenPair]]:
    username = form_data.username
    password = form_data.password

    if (user := await functions.find_user(username=username)) is None:
        raise fastapi.HTTPException(status_code=400, detail="Invalid username")

    if not functions.verify_password(password, user.password):
        raise fastapi.HTTPException(status_code=400, detail="Invalid password")

    token_pair = functions.generate_tokens(user=user)

    if token_pair is None:
        raise fastapi.HTTPException(status_code=500, detail="Failed to generate tokens")

    return {
        "tokens": token_pair,
    }


@router.post(
    "/register",
    response_model=typing.Dict[str, typing.Union[models.User, models.TokenPair]],
)
async def register(
    form_data: OAuth2PasswordRequestForm = fastapi.Depends(),
) -> typing.Dict[str, typing.Union[models.User, models.TokenPair]]:
    username = form_data.username
    password = form_data.password

    if (user := await functions.find_user(username=username)) is not None:
        raise fastapi.HTTPException(status_code=400, detail="Username already taken")

    user = await functions.create_user(username=username, password=password)

    token_pair = functions.generate_tokens(user=user)

    if token_pair is None:
        raise fastapi.HTTPException(status_code=500, detail="Failed to generate tokens")

    return {
        "tokens": token_pair,
    }


@router.post("/token/refresh", response_model=models.TokenPair)
async def refresh_token(
    refresh_data: models.RefreshRequest,
) -> models.TokenPair:
    refresh_token = refresh_data.refresh_token

    if functions.is_refresh_token_expired(refresh_token):
        raise fastapi.HTTPException(status_code=400, detail="Refresh token expired")

    payload = functions.decode_token(refresh_token, "refresh")
    user = await functions.find_user(user_id=payload["sub"]["user_id"])

    if user is None:
        raise fastapi.HTTPException(status_code=400, detail="User not found")

    token_pair = functions.generate_tokens(user=user)

    if token_pair is None:
        raise fastapi.HTTPException(status_code=500, detail="Failed to generate tokens")

    return token_pair
