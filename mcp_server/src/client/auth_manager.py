import time
import httpx
from typing import Optional
from src.config import settings

class AuthManager:
    """Manages JWT Bearer token authentication against FastAPI backend."""

    def __init__(self) -> None:
        self._cached_token: Optional[str] = settings.access_token
        self._expires_at: float = float("inf") if settings.access_token else 0.0

    async def get_token(self) -> Optional[str]:
        """Returns a valid access token, performing login if needed."""
        # 1. If static token is configured, use it
        if settings.access_token:
            return settings.access_token

        # 2. Check if cached token is still valid (with 60-second safety margin)
        if self._cached_token and time.time() < (self._expires_at - 60):
            return self._cached_token

        # 3. If credentials are provided, perform login
        if settings.email and settings.password:
            return await self._login()

        return None

    async def _login(self) -> str:
        """Executes login request against the backend."""
        login_url = f"{settings.api_base_url.rstrip('/')}/auth/login"
        payload = {
            "email": settings.email,
            "password": settings.password,
        }

        async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
            response = await client.post(login_url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Authentication failed ({response.status_code}): {response.text}"
                )

            data = response.json()
            token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)

            self._cached_token = token
            self._expires_at = time.time() + float(expires_in)
            return token

    def invalidate_token(self) -> None:
        """Clears cached token upon 401 Unauthorized errors."""
        if not settings.access_token:
            self._cached_token = None
            self._expires_at = 0.0

auth_manager = AuthManager()
