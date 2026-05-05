from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

TrimmedEmail = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=320),
]
TrimmedFullName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
]


class RegisterRequest(BaseModel):
    email: TrimmedEmail
    password: str = Field(min_length=8)
    full_name: TrimmedFullName


class LoginRequest(BaseModel):
    email: TrimmedEmail
    password: str = Field(min_length=1)


class SuccessResponse(BaseModel):
    success: bool
