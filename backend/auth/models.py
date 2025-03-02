import typing

import pydantic
from bson import ObjectId


class RefreshRequest(pydantic.BaseModel):
    refresh_token: str


class TokenPair(pydantic.BaseModel):
    access_token: str
    refresh_token: str


class TokenData(pydantic.BaseModel):
    user_id: str
    username: str
    token_type: typing.Literal["access", "refresh"]
    exp: typing.Optional[int] = None  # Unix timestamp


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return str(v)
        return v


class User(pydantic.BaseModel):
    id: typing.Optional[PyObjectId] = pydantic.Field(default=None, alias="_id")
    username: str
    password: str

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True, json_encoders={ObjectId: str}
    )

    def model_dump(self, **kwargs):
        exclude = kwargs.get("exclude", set())
        exclude.add("id")
        kwargs["exclude"] = exclude
        return super().model_dump(**kwargs)
