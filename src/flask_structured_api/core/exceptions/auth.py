from .base import APIError


class AuthenticationError(APIError):
    """Base authentication error"""

    def __init__(self, message: str, code: str = "AUTH_ERROR", details: dict = None):
        super().__init__(message=message, code=code, details=details, status_code=401)


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials error"""

    def __init__(self):
        super().__init__(
            message="Invalid email or password", code="AUTH_INVALID_CREDENTIALS"
        )
