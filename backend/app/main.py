"""
MFHelper - FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import os
import logging
import time

from app.config import settings
from app.routes import portfolio, upload, analytics, auth, rebalance, errors, holdings, cas, ai, xirr
from app.database import engine, Base

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

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing"""
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"→ {request.method} {request.url.path}")
    
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
        
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"✗ {request.method} {request.url.path} - Failed after {duration_ms:.2f}ms: {str(e)}")
        raise

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(cas.router, tags=["CAS Import"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(xirr.router)
app.include_router(rebalance.router, prefix="/api/rebalance", tags=["Rebalancing"])
app.include_router(holdings.router, tags=["Holdings & Overlap"])

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

@app.get("/dashboard")
async def dashboard():
    """Serve the original dashboard page"""
    logger.info("Serving dashboard.html")
    dashboard_path = os.path.join(frontend_path, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"error": "Dashboard not found"}

@app.get("/dashboard-pro")
async def dashboard_pro():
    """Serve the professional dashboard page"""
    logger.info("Serving dashboard-pro.html")
    dashboard_path = os.path.join(frontend_path, "dashboard-pro.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"error": "Professional dashboard not found"}

@app.get("/dashboard-old")
async def dashboard_old():
    """Serve the old dashboard page (for reference)"""
    dashboard_path = os.path.join(frontend_path, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"error": "Dashboard not found"}

@app.get("/admin")
async def admin_panel():
    """Serve the admin dashboard"""
    admin_path = os.path.join(frontend_path, "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path)
    return {"error": "Admin panel not found"}

@app.get("/how-it-works")
async def how_it_works():
    """Serve the How It Works page"""
    page_path = os.path.join(frontend_path, "how-it-works.html")
    if os.path.exists(page_path):
        return FileResponse(page_path)
    return {"error": "How It Works page not found"}

# Serve CSS and JS files
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

@app.get("/sw.js")
async def serve_service_worker():
    """Serve service worker"""
    sw_path = os.path.join(frontend_path, "sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    logger.warning("Service worker not found")
    return {"error": "Service worker not found"}

@app.get("/manifest.json")
async def serve_manifest():
    """Serve PWA manifest"""
    manifest_path = os.path.join(frontend_path, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return {"error": "Manifest not found"}

@app.get("/index.html")
async def serve_index_html():
    """Serve index.html for service worker"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return RedirectResponse(url="/")

@app.get("/offline.html")
async def serve_offline():
    """Serve offline page for PWA"""
    offline_path = os.path.join(frontend_path, "offline.html")
    if os.path.exists(offline_path):
        return FileResponse(offline_path)
    return {"message": "You are offline"}

@app.get("/icons/{file_path:path}")
async def serve_icons(file_path: str):
    """Serve icon files"""
    icon_path = os.path.join(frontend_path, "icons", file_path)
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    logger.warning(f"Icon not found: {file_path}")
    return {"error": "Icon not found"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
