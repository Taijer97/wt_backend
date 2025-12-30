from pydantic import BaseModel


class LoginRequest(BaseModel):
    doc_number: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str | None = None
    user_id: int | None = None
    role: str | None = None
