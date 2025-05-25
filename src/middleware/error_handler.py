from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("uvicorn.error")

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            logger.error(f"HTTPException: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        except Exception as exc:
            logger.exception("Unhandled exception occurred")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )

# Usage in FastAPI app:
# from fastapi import FastAPI
# from .middleware.error_handler import ErrorHandlerMiddleware
#
# app = FastAPI()
# app.add_middleware(ErrorHandlerMiddleware)