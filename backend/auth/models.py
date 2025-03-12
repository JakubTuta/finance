import typing

import bson
import pydantic


class RefreshRequest(pydantic.BaseModel):
    refresh: str


class TokenPair(pydantic.BaseModel):
    access: str
    refresh: str


class TokenData(pydantic.BaseModel):
    sub: str
    token_type: typing.Literal["access", "refresh"]
    exp: typing.Optional[int] = None  # Unix timestamp


class UserRequest(pydantic.BaseModel):
    username: str
    currency: str = "USD"


class User(pydantic.BaseModel):
    id: typing.Optional[bson.ObjectId] = pydantic.Field(default=None, alias="_id")
    username: str
    password: str
    currency: str = "USD"

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={bson.ObjectId: str},
        populate_by_name=True,
    )

    def model_dump(self, **kwargs):
        exclude = kwargs.get("exclude", set())
        exclude.add("id")
        kwargs["exclude"] = exclude
        return super().model_dump(**kwargs)
