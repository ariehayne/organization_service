import os
import sys
import uvicorn

from fastapi import FastAPI, Request

from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from dotenv import load_dotenv

from site_routes import router as site_router

load_dotenv()
sys.path.append("/app")

# Template engine

# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI()

app.include_router(site_router)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Handles HTTP exceptions and returns JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail or "An error occurred"},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handles generic exceptions and returns a JSON response."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host=os.getenv('SERVER_HOST', '127.0.0.1'), port=int(os.getenv('SERVER_PORT', 8080)), reload=True)
