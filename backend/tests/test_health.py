"""
Unit tests for Health Check and Monitoring endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.database import Base, get_db


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_health.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestLivenessCheck:
    """Test liveness probe endpoint"""
    
    def test_liveness_returns_ok(self):
        """Test that liveness probe returns OK"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "service" in data
        assert data["service"] == "MFHelper API"
    
    def test_liveness_alternative_path(self):
        """Test liveness probe on alternative path"""
        response = client.get("/api/health/liveness")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_liveness_no_auth_required(self):
        """Test that liveness probe doesn't require authentication"""
        response = client.get("/api/health")
        assert response.status_code == 200
        # Should work without any API key or auth


class TestReadinessCheck:
    """Test readiness probe endpoint"""
    
    def test_readiness_returns_status(self, setup_database):
        """Test that readiness probe returns status"""
        response = client.get("/api/health/readiness")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "ready" in data
        assert "timestamp" in data
    
    def test_readiness_checks_database(self, setup_database):
        """Test that readiness probe checks database"""
        response = client.get("/api/health/readiness")
        data = response.json()
        
        assert "database" in data["checks"]
        assert data["checks"]["database"] is True  # Should be connected
    
    def test_readiness_checks_disk_space(self, setup_database):
        """Test that readiness probe checks disk space"""
        response = client.get("/api/health/readiness")
        data = response.json()
        
        assert "disk_space" in data["checks"]
        assert isinstance(data["checks"]["disk_space"], bool)
    
    def test_readiness_checks_memory(self, setup_database):
        """Test that readiness probe checks memory"""
        response = client.get("/api/health/readiness")
        data = response.json()
        
        assert "memory" in data["checks"]
        assert isinstance(data["checks"]["memory"], bool)
    
    def test_readiness_overall_status(self, setup_database):
        """Test overall readiness status"""
        response = client.get("/api/health/readiness")
        data = response.json()
        
        # If all checks pass, status should be ready
        if all(data["checks"].values()):
            assert data["status"] == "ready"
            assert data["ready"] is True
        else:
            assert data["status"] == "not_ready"
            assert data["ready"] is False
    
    @patch('app.routes.health.psutil.disk_usage')
    def test_readiness_fails_on_low_disk(self, mock_disk, setup_database):
        """Test readiness fails when disk space is low"""
        # Mock low disk space (less than 100MB free)
        mock_disk_info = MagicMock()
        mock_disk_info.free = 50 * 1024 * 1024  # 50MB
        mock_disk.return_value = mock_disk_info
        
        response = client.get("/api/health/readiness")
        data = response.json()
        
        assert data["checks"]["disk_space"] is False
        assert data["ready"] is False


class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    def test_metrics_returns_data(self, setup_database):
        """Test that metrics endpoint returns data"""
        response = client.get("/api/health/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "process" in data
        assert "database" in data
        assert "runtime" in data
    
    def test_metrics_cpu_data(self, setup_database):
        """Test CPU metrics structure"""
        response = client.get("/api/health/metrics")
        data = response.json()
        
        assert "percent" in data["cpu"]
        assert "count" in data["cpu"]
        assert isinstance(data["cpu"]["percent"], (int, float))
        assert isinstance(data["cpu"]["count"], int)
        assert data["cpu"]["count"] > 0
    
    def test_metrics_memory_data(self, setup_database):
        """Test memory metrics structure"""
        response = client.get("/api/health/metrics")
        data = response.json()
        
        memory = data["memory"]
        assert "total_mb" in memory
        assert "available_mb" in memory
        assert "used_mb" in memory
        assert "percent" in memory
        
        # Sanity checks
        assert memory["total_mb"] > 0
        assert memory["available_mb"] >= 0
        assert memory["percent"] >= 0
        assert memory["percent"] <= 100
    
    def test_metrics_disk_data(self, setup_database):
        """Test disk metrics structure"""
        response = client.get("/api/health/metrics")
        data = response.json()
        
        disk = data["disk"]
        assert "total_gb" in disk
        assert "used_gb" in disk
        assert "free_gb" in disk
        assert "percent" in disk
        
        # Sanity checks
        assert disk["total_gb"] > 0
        assert disk["free_gb"] >= 0
        assert disk["percent"] >= 0
        assert disk["percent"] <= 100
    
    def test_metrics_process_data(self, setup_database):
        """Test process metrics structure"""
        response = client.get("/api/health/metrics")
        data = response.json()
        
        process = data["process"]
        assert "pid" in process
        assert "memory_rss_mb" in process
        assert "cpu_percent" in process
        assert "num_threads" in process
        assert "create_time" in process
        
        # Sanity checks
        assert process["pid"] > 0
        assert process["num_threads"] > 0
    
    def test_metrics_database_data(self, setup_database):
        """Test database metrics structure"""
        response = client.get("/api/health/metrics")
        data = response.json()
        
        db = data["database"]
        assert "connected" in db
        
        if db["connected"]:
            assert "users_count" in db
            assert "portfolios_count" in db
            assert "holdings_count" in db
    
    def test_metrics_runtime_data(self, setup_database):
        """Test runtime metrics structure"""
        response = client.get("/api/health/metrics")
        data = response.json()
        
        runtime = data["runtime"]
        assert "python_version" in runtime
        assert "platform" in runtime
        assert "executable" in runtime


class TestStatusEndpoint:
    """Test comprehensive status endpoint"""
    
    def test_status_returns_data(self, setup_database):
        """Test that status endpoint returns data"""
        response = client.get("/api/health/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "ready" in data
        assert "checks" in data
        assert "metrics" in data
    
    def test_status_service_info(self, setup_database):
        """Test service information"""
        response = client.get("/api/health/status")
        data = response.json()
        
        assert data["service"] == "MFHelper API"
        assert data["version"] is not None
    
    def test_status_health_determination(self, setup_database):
        """Test health status determination"""
        response = client.get("/api/health/status")
        data = response.json()
        
        # Status should be healthy if ready
        if data["ready"]:
            assert data["status"] == "healthy"
        else:
            assert data["status"] == "unhealthy"
    
    def test_status_includes_metrics(self, setup_database):
        """Test that status includes basic metrics"""
        response = client.get("/api/health/status")
        data = response.json()
        
        metrics = data["metrics"]
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "disk_percent" in metrics
        assert "database" in metrics
    
    def test_status_database_check(self, setup_database):
        """Test database status check"""
        response = client.get("/api/health/status")
        data = response.json()
        
        assert data["metrics"]["database"] == "connected"


class TestPingEndpoint:
    """Test simple ping endpoint"""
    
    def test_ping_returns_pong(self):
        """Test that ping returns pong"""
        response = client.get("/api/health/ping")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ping"] == "pong"
        assert "timestamp" in data
    
    def test_ping_fast_response(self):
        """Test that ping responds quickly"""
        import time
        start = time.time()
        response = client.get("/api/health/ping")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 0.5  # Should respond in less than 500ms
    
    def test_ping_no_database_dependency(self):
        """Test that ping works even if database is down"""
        # This test doesn't need database setup
        response = client.get("/api/health/ping")
        assert response.status_code == 200


class TestHealthEndpointsPerformance:
    """Test performance of health check endpoints"""
    
    def test_liveness_performance(self):
        """Test liveness endpoint performance"""
        import time
        
        times = []
        for _ in range(5):
            start = time.time()
            client.get("/api/health")
            duration = time.time() - start
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        assert avg_time < 0.1  # Should be very fast (< 100ms)
    
    def test_readiness_performance(self, setup_database):
        """Test readiness endpoint performance"""
        import time
        
        times = []
        for _ in range(5):
            start = time.time()
            client.get("/api/health/readiness")
            duration = time.time() - start
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        assert avg_time < 1.0  # Should respond in < 1 second


class TestHealthEndpointsErrorHandling:
    """Test error handling in health endpoints"""
    
    @patch('app.routes.health.psutil.cpu_percent')
    def test_metrics_handles_cpu_error(self, mock_cpu, setup_database):
        """Test metrics endpoint handles CPU error gracefully"""
        mock_cpu.side_effect = Exception("CPU error")
        
        response = client.get("/api/health/metrics")
        # Should still return 200, but may have error in data
        assert response.status_code == 200
    
    @patch('app.routes.health.psutil.virtual_memory')
    def test_readiness_handles_memory_error(self, mock_memory, setup_database):
        """Test readiness handles memory check error"""
        mock_memory.side_effect = Exception("Memory error")
        
        response = client.get("/api/health/readiness")
        data = response.json()
        
        # Should still return response
        assert response.status_code == 200
        # Memory check should fail
        assert data["checks"]["memory"] is False
