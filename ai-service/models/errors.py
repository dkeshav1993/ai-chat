from pydantic import BaseModel
from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    NO_RESULT = "NO_RESULT"
    DOWNSTREAM_NULL = "DOWNSTREAM_NULL"
    DOWNSTREAM_ERROR = "DOWNSTREAM_ERROR"
    DOWNSTREAM_TIMEOUT = "DOWNSTREAM_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    POLL_TIMEOUT = "POLL_TIMEOUT"
    TOKEN_REFRESH_FAILED = "TOKEN_REFRESH_FAILED"
    NO_AUTOSUGGEST_RESULT = "NO_AUTOSUGGEST_RESULT"


class TraversiaError(Exception):
    """Typed internal error that carries an ErrorCode and user-safe message."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        recoverable: bool = True,
        capability: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable
        self.capability = capability

    def to_dict(self) -> dict:
        return {
            "code": self.code.value,
            "message": self.message,
            "recoverable": self.recoverable,
            "capability": self.capability,
        }
