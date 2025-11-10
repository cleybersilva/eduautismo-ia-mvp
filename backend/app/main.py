"""
EduAutismo IA - FastAPI Main Application

This is the main entry point for the EduAutismo IA API.
It configures the FastAPI application with middleware, exception handlers, and routes.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

# Try different import paths for development flexibility
try:
    from backend.app.core.config import settings
    from backend.app.core.database import engine, Base
    from backend.app.api import api_router
except ImportError:
    from app.core.config import settings
    from app.core.database import engine, Base
    from app.api import api_router


# ============================================================================
# Lifecycle Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle (startup and shutdown).

    Startup:
    - Initialize database tables
    - Log application start
    - Perform health checks

    Shutdown:
    - Close database connections
    - Log application shutdown
    """
    # Startup
    print("🚀 Starting EduAutismo IA API")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")

    yield

    # Shutdown
    print("🛑 Shutting down EduAutismo IA API")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    **EduAutismo IA** - Plataforma Inteligente de Apoio Pedagógico para TEA

    Esta API fornece funcionalidades para:
    - Gestão de alunos com TEA
    - Geração de atividades personalizadas com IA
    - Avaliações comportamentais
    - Recomendações pedagógicas
    - Analytics e relatórios

    Desenvolvido como TCC do MBA em IA e Big Data - USP
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    # Additional metadata
    contact={
        "name": "Cleyber Ferreira",
        "email": "cleyber@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# ============================================================================
# Middleware Configuration
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# GZIP Compression Middleware
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000  # Only compress responses larger than 1KB
)


# ============================================================================
# Custom Middleware
# ============================================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add X-Process-Time header to all responses.

    This helps with performance monitoring.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to all responses.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests.
    """
    print(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"📤 Status: {response.status_code}")
    return response


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    print(f"❌ Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_server_error",
            "path": str(request.url.path)
        }
    )


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - API information.

    Returns basic API information and useful links.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "links": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
            "api_v1": "/api/v1"
        }
    }


# ============================================================================
# Include API Routes
# ============================================================================

# Include all API v1 routes
app.include_router(
    api_router,
    prefix="/api/v1"
)


# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
