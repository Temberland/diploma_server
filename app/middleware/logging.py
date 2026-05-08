import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.logging import get_logger

logger = get_logger("requests")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        response = await call_next(request)

        duration = round((time.time() - start) * 1000, 2)
        ip = request.client.host if request.client else "unknown"

        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration}ms "
            f"ip={ip}"
        )

        return response
