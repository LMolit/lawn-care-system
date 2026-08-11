from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer" 

class UserResponse(BaseModel):
    id: int
    email: str
    active: bool

    class Config:
        from_attributes = True
