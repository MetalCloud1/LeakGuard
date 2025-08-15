from pydantic import BaseModel, EmailStr, field_validator, Field, ValidationInfo
import re


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, v, info: ValidationInfo):
        username = info.data.get("username", "").lower()
        if username == v.lower():
            raise ValueError("The password cannot "
                             "be the same as username")
        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "The password must contain at "
                "least one uppercase letter"
            )
        if not re.search(r"[a-z]", v):
            raise ValueError(
                "The password must contain "
                "at least one lowercase letter"
            )
        if not re.search(r"\d", v):
            raise ValueError("The password must contain"
                              "at least one number"
            )
        if not re.search(r"[@#$%^&*!?]", v):
            raise ValueError(
                "The password must contain at least one"
                "special character (@#$%^&*!?)"
            )
        return v


class UserOut(UserBase):
    pass
