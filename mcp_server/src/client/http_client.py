from typing import Any, Dict, Optional
import httpx
from src.config import settings
from src.client.auth_manager import auth_manager

class APIError(Exception):
    """Exception raised when an API request fails."""

    def __init__(self, status_code: int, message: str, detail: Optional[Any] = None) -> None:
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(f"API Error {status_code}: {message}")

class HTTPClient:
    """Asynchronous HTTP Client for Smart Finance REST API."""

    def __init__(self) -> None:
        self.base_url = settings.api_base_url.rstrip("/")

    async def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        token = await auth_manager.get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        is_retry: bool = False,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = await self._get_headers()

        async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers,
                )
            except httpx.ConnectError:
                raise APIError(
                    status_code=503,
                    message=f"No se pudo conectar con el servidor en {self.base_url}. Asegúrate de que Docker esté activo.",
                )
            except httpx.TimeoutException:
                raise APIError(
                    status_code=504,
                    message=f"Tiempo de espera agotado al conectar con {url}.",
                )

            # Handle 401 with one retry attempt after invalidating cache
            if response.status_code == 401 and not is_retry:
                auth_manager.invalidate_token()
                return await self._request(
                    method=method,
                    path=path,
                    params=params,
                    json_data=json_data,
                    is_retry=True,
                )

            if response.status_code >= 400:
                try:
                    error_json = response.json()
                    detail = error_json.get("detail", response.text)
                except Exception:
                    detail = response.text
                raise APIError(
                    status_code=response.status_code,
                    message=f"Error en la petición a {path}: {detail}",
                    detail=detail,
                )

            if response.status_code == 204:
                return None

            return response.json()

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("POST", path, json_data=json_data)

    async def put(self, path: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("PUT", path, json_data=json_data)

    async def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("DELETE", path, params=params)

http_client = HTTPClient()
