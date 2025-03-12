import typing

import fastapi
from fastapi.security import OAuth2PasswordRequestForm

from . import functions, models

router = fastapi.APIRouter(prefix="/auth")


@router.post(
    "/login/",
    response_model=typing.Dict[str, typing.Union[models.User, models.TokenPair]],
    response_model_exclude={"user": {"password"}},
    response_model_by_alias=False,
)
async def login(
    form_data: OAuth2PasswordRequestForm = fastapi.Depends(),
) -> typing.Dict[str, typing.Union[models.User, models.TokenPair]]:
    username = form_data.username
    password = form_data.password

    if (user := await functions.find_user(username=username)) is None:
        raise fastapi.HTTPException(status_code=400, detail="Invalid username")

    if not functions.verify_password(password, user.password):
        raise fastapi.HTTPException(status_code=401, detail="Invalid password")

    token_pair = functions.generate_tokens(user=user)

    if token_pair is None:
        raise fastapi.HTTPException(status_code=500, detail="Failed to generate tokens")

    return {
        "user": user,
        "tokens": token_pair,
    }


@router.post(
    "/register/",
    response_model=typing.Dict[str, typing.Union[models.User, models.TokenPair]],
    response_model_exclude={"user": {"password"}},
    response_model_by_alias=False,
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
        "user": user,
        "tokens": token_pair,
    }


@router.put(
    "/update-user-data/",
    response_model=models.User,
    response_model_exclude={"password"},
    response_model_by_alias=False,
)
async def update_user(
    user_data: models.UserRequest,
    current_user: models.User = fastapi.Depends(functions.get_current_user),
) -> models.User:
    user = await functions.update_user(current_user, user_data)

    return user


@router.post("/token/refresh/", response_model=models.TokenPair)
async def refresh_token(
    refresh_data: models.RefreshRequest,
) -> models.TokenPair:
    refresh_token = refresh_data.refresh
    if functions.is_refresh_token_expired(refresh_token):
        raise fastapi.HTTPException(status_code=400, detail="Refresh token expired")

    payload = functions.decode_token(refresh_token, "refresh")
    user = await functions.find_user(user_id=payload["sub"])

    if user is None:
        raise fastapi.HTTPException(status_code=400, detail="User not found")

    token_pair = functions.generate_tokens(user=user)

    if token_pair is None:
        raise fastapi.HTTPException(status_code=500, detail="Failed to generate tokens")

    return token_pair


@router.get(
    "/me/",
    response_model=models.User,
    response_model_exclude={"password"},
    response_model_by_alias=False,
)
async def get_current_user(
    user: models.User = fastapi.Depends(functions.get_current_user),
) -> models.User:
    return user
