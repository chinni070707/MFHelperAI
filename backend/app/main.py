"""
MFHelper - FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os
import logging
import time

from app.config import settings
from app.routes import portfolio, upload, analytics, auth, rebalance, errors, holdings, cas, ai, xirr, analysis, demo, funds, overlap
from app.database import engine, Base
from app.middleware.rate_limiter import limiter

# Setup centralized logging
from app.utils.logger import setup_logging, log_request
setup_logging(
    log_level=logging.DEBUG if settings.DEBUG else logging.INFO,
    enable_file_logging=True
)

logger = logging.getLogger(__name__)
logger.info(f"Starting {settings.APP_NAME} - Debug Mode: {settings.DEBUG}")

# Initialize Sentry for error tracking and monitoring
from app.utils.sentry import init_sentry
init_sentry()

# Initialize cache
from app.utils.cache import cache
if cache.is_available():
    stats = cache.get_stats()
    logger.info(f"[OK] Cache initialized: {stats}")
else:
    logger.warning("[WARN] Cache unavailable - running without Redis")

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created/verified")

app = FastAPI(
    title="MFHelper API",
    description="Mutual Fund Portfolio Analytics Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging + security headers middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing and add security headers"""
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"-> {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        # Security headers (#7)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not settings.DEBUG:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.plot.ly https://www.googletagmanager.com https://accounts.google.com https://apis.google.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://www.google-analytics.com https://accounts.google.com; "
                "frame-src https://accounts.google.com;"
            )
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"[ERROR] {request.method} {request.url.path} - Failed after {duration_ms:.2f}ms: {str(e)}")
        raise

# Security: HTTPS redirect in production (disabled for local development)
# Uncomment for production deployment with HTTPS
# if not settings.DEBUG:
#     app.add_middleware(HTTPSRedirectMiddleware)

# Security: Trusted host middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "testserver", "*.mfhelper.com"]  # Added testserver for tests
    )

# Performance: Response compression (70% size reduction)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses > 1KB
    compresslevel=6     # Balance between speed and compression (1-9)
)
logger.info("[OK] GZip compression enabled (min_size: 1KB)")

# CORS middleware - Configured for security
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

# In production, add your frontend domain
if not settings.DEBUG:
    ALLOWED_ORIGINS.extend([
        "https://mfhelper.com",
        "https://www.mfhelper.com"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(cas.router, tags=["CAS Import"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(demo.router, prefix="/api", tags=["Demo Portfolio"])
app.include_router(funds.router, prefix="/api", tags=["Funds Master"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis Tools"])
app.include_router(xirr.router)
app.include_router(rebalance.router, prefix="/api/rebalance", tags=["Rebalancing"])
app.include_router(holdings.router, tags=["Holdings & Overlap"])
app.include_router(overlap.router, tags=["Enhanced Overlap Analysis"])

# Import and register admin routes
from app.routes import admin
app.include_router(admin.router, tags=["Admin"])

# Import and register health check routes
from app.routes import health
app.include_router(health.router, tags=["Health & Monitoring"])
app.include_router(errors.router, tags=["Error Logging"])

# Register AI routes
app.include_router(ai.router, prefix="/api", tags=["AI"])

# Serve static files (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    """Serve the frontend landing page"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to MFHelper API", "docs": "/api/docs"}

# Serve CSS, JS, icons, and other static assets
@app.get("/css/{file_path:path}")
async def serve_css(file_path: str):
    """Serve CSS files"""
    css_path = os.path.join(frontend_path, "css", file_path)
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    return {"error": "CSS file not found"}

@app.get("/js/{file_path:path}")
async def serve_js(file_path: str):
    """Serve JavaScript files"""
    js_path = os.path.join(frontend_path, "js", file_path)
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    logger.warning(f"JS file not found: {file_path}")
    return {"error": "JS file not found"}

@app.get("/icons/{file_path:path}")
async def serve_icons(file_path: str):
    """Serve icon files"""
    icon_path = os.path.join(frontend_path, "icons", file_path)
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    logger.warning(f"Icon not found: {file_path}")
    return {"error": "Icon not found"}

@app.get("/sw.js")
async def serve_service_worker():
    """Serve service worker from root"""
    sw_path = os.path.join(frontend_path, "sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    return {"error": "Service worker not found"}

@app.get("/manifest.json")
async def serve_manifest():
    """Serve PWA manifest from root"""
    manifest_path = os.path.join(frontend_path, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return {"error": "Manifest not found"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# Generic catch-all for all HTML pages (#28 \u2014 replaces ~40 repetitive route handlers)
# Must be registered LAST so explicit routes above take priority
@app.get("/{page_path:path}")
async def serve_html_page(page_path: str):
    """Serve any frontend HTML page or www/ sub-page by path"""
    # Sanitize: only allow alphanumeric, hyphens, slashes, dots
    import re
    if not re.match(r'^[a-zA-Z0-9/_.-]+$', page_path):
        return {"error": "Invalid path"}

    # Prevent directory traversal
    if '..' in page_path:
        return {"error": "Invalid path"}

    # Try direct path (e.g. "dashboard.html")
    file_path = os.path.join(frontend_path, page_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # Try with .html extension (e.g. "dashboard" \u2192 "dashboard.html")
    html_path = os.path.join(frontend_path, f"{page_path}.html")
    if os.path.isfile(html_path):
        return FileResponse(html_path)

    # Try in www/ subdirectory (e.g. "overlap-analysis.html")
    www_path = os.path.join(frontend_path, "www", page_path)
    if os.path.isfile(www_path):
        return FileResponse(www_path)

    return {"error": f"Page not found: {page_path}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
