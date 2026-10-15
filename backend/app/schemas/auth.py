from pydantic import BaseModel, field_validator, model_validator

from app.core.security import MAX_PASSWORD_BYTES

MIN_PASSWORD_LENGTH = 12


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    active: bool

    class Config:
        from_attributes = True


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_is_acceptable(cls, value: str) -> str:
        if len(value) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
            )
        # bcrypt limit, counted in bytes: accented letters and emoji use more than one
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError("Password is too long")
        return value

    @model_validator(mode="after")
    def new_password_differs_from_current(self):
        if self.new_password == self.current_password:
            raise ValueError("New password must be different from the current one")
        return self
