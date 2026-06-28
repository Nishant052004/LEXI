import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from config.config import settings
from database.connection import engine, Base
from api import auth, chat, profile, history, entities, ops
from utils.logger import setup_logger
from utils.metrics import metrics_collector

logger = setup_logger("main_app")

# Ensure all database schemas are created on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-Ready Multi-Agent AI Chatbot API Layer",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Set up CORS middleware for integration with external dashboards/frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for metrics and execution logging
@app.middleware("http")
async def log_requests_and_metrics(request: Request, call_next):
    start_time = time.perf_counter()
    endpoint = request.url.path
    
    # Record request metrics
    metrics_collector.record_request(endpoint)
    
    logger.info(f"Incoming Request: {request.method} {endpoint}")
    
    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Completed Request: {request.method} {endpoint} - Status {response.status_code} in {process_time*1000:.2f}ms")
        return response
    except Exception as e:
        metrics_collector.record_error(endpoint)
        logger.error(f"Failed Request: {request.method} {endpoint} - Error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal Application Error: {str(e)}"}
        )

# Health check and Metrics API
@app.get("/health", tags=["Health & Monitoring"])
def health_check():
    """Simple API health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/api/monitoring/metrics", tags=["Health & Monitoring"])
def get_metrics_endpoint():
    """Retrieves operational metrics (latency, requests, execution times)."""
    return metrics_collector.get_metrics()

# Include Feature Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(history.router)
app.include_router(entities.router)
app.include_router(ops.router)

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} in debug mode...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
