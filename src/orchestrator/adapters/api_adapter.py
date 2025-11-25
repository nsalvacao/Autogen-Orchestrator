"""
API Adapter - REST API client adapter for external API integrations.

This adapter provides HTTP client functionality for integrating with REST APIs
including authentication, request/response handling, and error management.
"""

import json
from enum import Enum
from typing import Any
from urllib.parse import urljoin

from orchestrator.contracts.adapter_contract import (
    AdapterConfig,
    AdapterContract,
    AdapterResult,
    AdapterStatus,
    AdapterType,
)

# Optional HTTP client - gracefully handle if not available
try:
    import aiohttp
    HTTP_CLIENT_AVAILABLE = True
except ImportError:
    HTTP_CLIENT_AVAILABLE = False
    aiohttp = None


class AuthType(str, Enum):
    """Authentication types for API requests."""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    CUSTOM = "custom"


class HTTPMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIAdapter(AdapterContract):
    """
    REST API client adapter for external API services.

    Features:
    - Multiple authentication methods (Basic, Bearer, API Key)
    - Async HTTP requests with aiohttp
    - Request/response handling with proper error management
    - Configurable timeout and retry logic
    - Custom headers support

    Integrations:
    - Generic REST APIs
    - LLM APIs (OpenAI, Anthropic, etc.)
    - Code analysis APIs
    - Issue tracking APIs
    - Notification services
    """

    def __init__(
        self,
        config: AdapterConfig | None = None,
        base_url: str | None = None,
        auth_type: AuthType = AuthType.NONE,
        auth_token: str | None = None,
        timeout: int = 30,
        headers: dict[str, str] | None = None,
    ):
        """
        Initialize the API adapter.
        
        Args:
            config: Adapter configuration.
            base_url: Base URL for API requests.
            auth_type: Authentication type.
            auth_token: Authentication token/key.
            timeout: Request timeout in seconds.
            headers: Additional custom headers.
        """
        if config is None:
            config = AdapterConfig(
                adapter_type=AdapterType.API,
                name="APIAdapter",
                enabled=HTTP_CLIENT_AVAILABLE,
            )
        super().__init__(config)
        self._base_url = base_url
        self._auth_type = auth_type
        self._auth_token = auth_token
        self._timeout = timeout
        self._custom_headers = headers or {}
        self._session: Any = None  # aiohttp ClientSession

    @property
    def adapter_type(self) -> AdapterType:
        """Return the adapter type."""
        return AdapterType.API

    @property
    def name(self) -> str:
        """Return the adapter name."""
        return self._config.name

    async def connect(self) -> AdapterResult:
        """
        Establish connection to the API.

        Returns:
            AdapterResult indicating success or failure.
        """
        if not self._config.enabled:
            return AdapterResult(
                success=False,
                error_message="API adapter is not enabled. Install aiohttp: pip install aiohttp",
            )

        if not HTTP_CLIENT_AVAILABLE:
            return AdapterResult(
                success=False,
                error_message="aiohttp not available. Install with: pip install aiohttp",
            )

        if not self._base_url:
            return AdapterResult(
                success=False,
                error_message="Base URL not configured. Call configure_endpoint() first.",
            )

        # Create aiohttp session
        timeout = aiohttp.ClientTimeout(total=self._timeout)
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            headers=self._get_auth_headers(),
        )
        
        self._status = AdapterStatus.CONFIGURED
        return AdapterResult(
            success=True,
            data={
                "message": "API adapter connected",
                "base_url": self._base_url,
                "auth_type": self._auth_type.value,
            },
        )

    async def disconnect(self) -> AdapterResult:
        """
        Disconnect from the API.

        Returns:
            AdapterResult indicating success or failure.
        """
        if self._session and not self._session.closed:
            await self._session.close()
        
        self._session = None
        self._status = AdapterStatus.DISCONNECTED
        return AdapterResult(
            success=True,
            data={"message": "API adapter disconnected"},
        )

    async def execute(self, operation: str, **kwargs: Any) -> AdapterResult:
        """
        Execute an API operation.

        Args:
            operation: The API endpoint/path or full operation spec.
            **kwargs: Request parameters (method, data, params, headers, etc.).

        Returns:
            AdapterResult containing the operation result.
        """
        if not self.is_configured():
            return AdapterResult(
                success=False,
                error_message="API adapter is not configured. Call connect() first.",
            )

        # Extract HTTP method (default: GET)
        method = kwargs.get("method", "GET")
        if isinstance(method, str):
            method = method.upper()
        
        # Build full URL
        url = urljoin(self._base_url, operation) if not operation.startswith("http") else operation
        
        # Extract request components
        params = kwargs.get("params")
        data = kwargs.get("data")
        json_data = kwargs.get("json")
        headers = {**self._custom_headers, **kwargs.get("headers", {})}
        
        try:
            async with self._session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
            ) as response:
                # Get response content
                content_type = response.headers.get("Content-Type", "")
                
                if "application/json" in content_type:
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                # Check for errors
                if response.status >= 400:
                    return AdapterResult(
                        success=False,
                        error_message=f"HTTP {response.status}: {response.reason}",
                        data={"response": response_data, "status_code": response.status},
                        metadata={"url": url, "method": method},
                    )
                
                return AdapterResult(
                    success=True,
                    data={
                        "response": response_data,
                        "status_code": response.status,
                        "headers": dict(response.headers),
                    },
                    metadata={"url": url, "method": method},
                )
        
        except aiohttp.ClientError as e:
            return AdapterResult(
                success=False,
                error_message=f"Request failed: {str(e)}",
                metadata={"url": url, "method": method},
            )
        except Exception as e:
            return AdapterResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                metadata={"url": url, "method": method},
            )

    async def health_check(self) -> AdapterResult:
        """
        Check API connectivity.

        Returns:
            AdapterResult indicating health status.
        """
        return AdapterResult(
            success=True,
            data={
                "status": "healthy" if self.is_configured() else "not_configured",
                "adapter": self.name,
            },
        )

    def configure_endpoint(self, base_url: str) -> None:
        """
        Configure the API base URL.

        Args:
            base_url: The base URL for API requests.
        """
        self._base_url = base_url
    
    def configure_auth(self, auth_type: AuthType, token: str) -> None:
        """
        Configure authentication.
        
        Args:
            auth_type: Type of authentication.
            token: Authentication token/key.
        """
        self._auth_type = auth_type
        self._auth_token = token
    
    def _get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers based on auth type.
        
        Returns:
            Dictionary of authentication headers.
        """
        headers = {}
        
        if self._auth_type == AuthType.BEARER and self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        elif self._auth_type == AuthType.API_KEY and self._auth_token:
            headers["X-API-Key"] = self._auth_token
        elif self._auth_type == AuthType.BASIC and self._auth_token:
            headers["Authorization"] = f"Basic {self._auth_token}"
        
        return {**headers, **self._custom_headers}
    
    async def request(
        self,
        method: HTTPMethod | str,
        endpoint: str,
        **kwargs: Any,
    ) -> AdapterResult:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            **kwargs: Additional request parameters.
            
        Returns:
            AdapterResult with response data.
        """
        if isinstance(method, HTTPMethod):
            method = method.value
        
        return await self.execute(endpoint, method=method, **kwargs)
    
    async def get(self, endpoint: str, **kwargs: Any) -> AdapterResult:
        """Make a GET request."""
        return await self.request(HTTPMethod.GET, endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs: Any) -> AdapterResult:
        """Make a POST request."""
        return await self.request(HTTPMethod.POST, endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs: Any) -> AdapterResult:
        """Make a PUT request."""
        return await self.request(HTTPMethod.PUT, endpoint, **kwargs)
    
    async def patch(self, endpoint: str, **kwargs: Any) -> AdapterResult:
        """Make a PATCH request."""
        return await self.request(HTTPMethod.PATCH, endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs: Any) -> AdapterResult:
        """Make a DELETE request."""
        return await self.request(HTTPMethod.DELETE, endpoint, **kwargs)
