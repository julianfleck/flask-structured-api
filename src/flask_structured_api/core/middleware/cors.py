from flask import request, make_response, current_app
from typing import List
import inspect


class CORSMiddleware:
    def __init__(
        self,
        allowed_origins: List[str] = None,
        allowed_methods: List[str] = None,
        max_age: int = 86400
    ):
        self.allowed_origins = allowed_origins or [
            "http://localhost:3000"
        ]
        self.allowed_methods = allowed_methods or [
            "GET", "POST", "PUT", "DELETE", "OPTIONS"
        ]
        self.max_age = max_age
        self.allowed_headers = [
            'Authorization',
            'Content-Type',
            'X-API-Version',
            'X-Response-Time',
            'X-Request-ID',
            'X-API-Key',
            'x-api-key',
            'Origin',
            'Accept',
            'Access-Control-Request-Method',
            'Access-Control-Request-Headers'
        ]
        self.exposed_headers = [
            'Authorization',
            'Content-Type',
            'X-API-Version',
            'X-Response-Time',
            'X-Request-ID'
        ]

    async def handle_cors(self, response=None):
        if response is None:
            response = make_response()

        # Skip CORS handling and logging for Google health checks
        if request.headers.get('User-Agent', '').startswith('GoogleHC'):
            return response

        origin = request.headers.get('Origin')

        if inspect.iscoroutine(response):
            response = await response  # Await the coroutine to get the actual response object

        if origin in self.allowed_origins:
            headers = {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': ', '.join(self.allowed_methods),
                'Access-Control-Allow-Headers': ', '.join(self.allowed_headers),
                'Access-Control-Expose-Headers': ', '.join(self.exposed_headers),
                'Access-Control-Max-Age': str(self.max_age),
                'Vary': 'Origin, Accept-Encoding',
                'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Content-Encoding': response.headers.get('Content-Encoding', 'identity'),
            }
            response.headers.update(headers)

            # For preflight requests, ensure we return 200
            if request.method == 'OPTIONS':
                response.status_code = 200

            current_app.logger.debug(
                "CORS: Modified response headers",
                extra={
                    "origin": origin,
                    "headers": dict(response.headers),
                    "response_type": type(response).__name__,
                    "status_code": getattr(response, 'status_code', None),
                }
            )
        elif origin is not None:  # Only log non-health-check CORS failures
            current_app.logger.warning(
                f"CORS: Origin not allowed: {origin}",
                extra={"allowed_origins": self.allowed_origins}
            )

        return response


def setup_cors(app):
    """Setup CORS handling for the application"""
    cors = CORSMiddleware()

    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            return cors.handle_cors()

    @app.after_request
    def handle_response(response):
        try:
            return cors.handle_cors(response)
        except Exception as e:
            current_app.logger.error(
                f"CORS handling error: {str(e)}",
                extra={
                    "error": str(e),
                    "method": request.method,
                    "origin": request.headers.get('Origin'),
                    "response_type": type(response).__name__
                },
                exc_info=True
            )
            return response
