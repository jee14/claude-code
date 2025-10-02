# filename: create_final_enhancements.py
import os

# Create enhanced health module with uptime tracking
enhanced_health = '''from fastapi import APIRouter
from datetime import datetime
import sys
import os
import time

router = APIRouter()

# Track startup time
_startup_time = time.time()

def get_uptime() -> float:
    """Get service uptime in seconds"""
    return time.time() - _startup_time

@router.get("/health")
async def health_check():
    """
    Health check endpoint for Docker health checks and monitoring
    Returns basic service health status
    """
    return {
        "status": "healthy",
        "service": "korean-text-corrector-backend",
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "uptime_seconds": round(get_uptime(), 2),
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }

@router.get("/ready")
async def readiness_check():
    """
    Readiness check to verify all dependencies are loaded
    Returns detailed readiness status with dependency verification
    """
    try:
        # Test if spaCy model is loaded
        import spacy
        nlp = spacy.load("ko_core_news_sm")
        
        return {
            "status": "ready",
            "spacy_model": "ko_core_news_sm",
            "spacy_version": spacy.__version__,
            "model_loaded": True,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(get_uptime(), 2)
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
            "model_loaded": False,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/metrics")
async def metrics():
    """
    Basic metrics endpoint for monitoring
    Can be extended with prometheus_client for detailed metrics
    """
    return {
        "uptime_seconds": round(get_uptime(), 2),
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }
'''

os.makedirs('../korean-text-corrector/backend', exist_ok=True)
with open('../korean-text-corrector/backend/health.py', 'w') as f:
    f.write(enhanced_health)
print('Updated: ../korean-text-corrector/backend/health.py (with uptime tracking)')

# Create startup validation module
startup_validation = '''"""
Startup validation and configuration verification module
Import and use in main.py to ensure all required configurations are present
"""
import os
import sys
from typing import List, Dict

def validate_environment() -> Dict[str, any]:
    """
    Validate required environment variables and configuration
    Returns validation results
    """
    required_vars = {
        "ENVIRONMENT": "production",  # default value
    }
    
    optional_vars = {
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    
    results = {
        "valid": True,
        "missing_required": [],
        "present_required": {},
        "present_optional": {},
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    # Check required variables
    for var, default in required_vars.items():
        value = os.getenv(var, default)
        if not value:
            results["valid"] = False
            results["missing_required"].append(var)
        else:
            results["present_required"][var] = value
    
    # Check optional variables
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        if value:
            results["present_optional"][var] = value
    
    return results

def validate_dependencies() -> Dict[str, any]:
    """
    Validate that all required dependencies are available
    """
    results = {
        "valid": True,
        "dependencies": {},
        "errors": []
    }
    
    # Check spaCy
    try:
        import spacy
        results["dependencies"]["spacy"] = spacy.__version__
        
        # Try to load Korean model
        try:
            nlp = spacy.load("ko_core_news_sm")
            results["dependencies"]["ko_core_news_sm"] = "loaded"
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"SpaCy Korean model not found: {str(e)}")
    except ImportError as e:
        results["valid"] = False
        results["errors"].append(f"SpaCy not installed: {str(e)}")
    
    # Check FastAPI
    try:
        import fastapi
        results["dependencies"]["fastapi"] = fastapi.__version__
    except ImportError as e:
        results["valid"] = False
        results["errors"].append(f"FastAPI not installed: {str(e)}")
    
    return results

def startup_checks() -> bool:
    """
    Run all startup checks
    Returns True if all checks pass, raises RuntimeError otherwise
    """
    print("🔍 Running startup validation...")
    
    # Environment validation
    env_results = validate_environment()
    print(f"   Environment variables: {'✅' if env_results['valid'] else '❌'}")
    
    if not env_results['valid']:
        raise RuntimeError(
            f"Missing required environment variables: {env_results['missing_required']}"
        )
    
    # Dependency validation
    dep_results = validate_dependencies()
    print(f"   Dependencies: {'✅' if dep_results['valid'] else '❌'}")
    
    if not dep_results['valid']:
        raise RuntimeError(
            f"Dependency errors: {', '.join(dep_results['errors'])}"
        )
    
    print("✅ All startup checks passed!")
    return True

# Example usage in main.py:
"""
from startup_validation import startup_checks

@app.on_event("startup")
async def startup_event():
    startup_checks()
"""
'''

with open('../korean-text-corrector/backend/startup_validation.py', 'w') as f:
    f.write(startup_validation)
print('Created: ../korean-text-corrector/backend/startup_validation.py')

# Create updated docker-compose with explicit network naming
docker_compose_final = '''version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: korean-corrector-backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
      - ENVIRONMENT=production
    # Remove volume mount for production, uncomment for development
    # volumes:
    #   - ./backend:/app
    volumes:
      - backend-cache:/root/.cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - korean-corrector-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=http://backend:8000
    container_name: korean-corrector-frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      # Use service name for internal communication
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - korean-corrector-network

volumes:
  backend-cache:
    driver: local
    name: korean-corrector-backend-cache

networks:
  korean-corrector-network:
    name: korean-corrector-net
    driver: bridge
'''

with open('../korean-text-corrector/docker-compose.yml', 'w') as f:
    f.write(docker_compose_final)
print('Updated: ../korean-text-corrector/docker-compose.yml (with explicit naming)')

# Create integration guide for main.py
main_integration = '''"""
Complete integration guide for backend/main.py

This file shows how to integrate all the Docker-ready components
into your FastAPI application.
"""

# ============================================
# COMPLETE EXAMPLE OF main.py
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from health import router as health_router
from startup_validation import startup_checks
import os

# Create FastAPI app
app = FastAPI(
    title="Korean Text Corrector API",
    description="API for correcting Korean text grammar and spelling",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# CORS Configuration
# ============================================
# For production, specify exact origins:
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Configure for production: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Health Check Endpoints (for Docker)
# ============================================
app.include_router(health_router, tags=["health"])

# ============================================
# Startup Event Handler
# ============================================
@app.on_event("startup")
async def startup_event():
    """Run validation checks on startup"""
    print("🚀 Starting Korean Text Corrector API...")
    startup_checks()
    print("✅ Server is ready to accept requests")

# ============================================
# Shutdown Event Handler
# ============================================
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down Korean Text Corrector API...")

# ============================================
# Your Existing Routes
# ============================================

# Example correction endpoint (add your actual implementation)
from pydantic import BaseModel

class CorrectionRequest(BaseModel):
    text: str

class CorrectionResponse(BaseModel):
    success: bool
    data: dict = None
    error: str = None

@app.post("/api/correct", response_model=CorrectionResponse)
async def correct_text(request: CorrectionRequest):
    """
    Correct Korean text
    
    This is a placeholder - replace with your actual correction logic
    """
    try:
        # TODO: Implement your correction logic here
        # Example:
        # corrected = korean_corrector.correct(request.text)
        
        return CorrectionResponse(
            success=True,
            data={
                "original": request.text,
                "corrected": request.text,  # Placeholder
                "corrections": []
            }
        )
    except Exception as e:
        return CorrectionResponse(
            success=False,
            error=str(e)
        )

# ============================================
# Root Endpoint
# ============================================
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Korean Text Corrector API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============================================
# Environment Configuration for Production
# ============================================

# Example .env file for production:
"""
# Backend
ENVIRONMENT=production
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional: Add your API keys or secrets here
# OPENAI_API_KEY=your-key-here
"""
'''

with open('../korean-text-corrector/backend/INTEGRATION_GUIDE.py', 'w') as f:
    f.write(main_integration)
print('Created: ../korean-text-corrector/backend/INTEGRATION_GUIDE.py')

# Create deployment checklist
deployment_checklist = '''# 🚀 Deployment Checklist

## Pre-Deployment Validation

### Code Integration
- [ ] Health router added to `main.py`: