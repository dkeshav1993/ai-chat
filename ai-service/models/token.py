from pydantic import BaseModel
from typing import Optional


class TokenRequest(BaseModel):
    moduleID: str
    userName: str
    password: str


class TokenResponse(BaseModel):
    token: str
    correleationId: str  # Note: sic — double-e, matches Spring Boot exactly
    message: str
    tokenClaims: Optional[None] = None
    tokenValid: bool
