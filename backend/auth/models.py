import typing

import pydantic
from bson import ObjectId


class RefreshRequest(pydantic.BaseModel):
    refresh: str


class TokenPair(pydantic.BaseModel):
    access: str
    refresh: str


class TokenData(pydantic.BaseModel):
    sub: str
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
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
    )

    def model_dump(self, **kwargs):
        exclude = kwargs.get("exclude", set())
        exclude.add("id")
        kwargs["exclude"] = exclude
        return super().model_dump(**kwargs)
