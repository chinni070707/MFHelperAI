"""
Unit tests for Sentry integration utilities
"""
import pytest
from unittest.mock import patch, MagicMock, call
import os

from app.utils.sentry import (
    init_sentry,
    before_send_event,
    before_breadcrumb,
    capture_exception,
    capture_message,
    set_user_context,
    set_transaction_name,
    add_breadcrumb
)


class TestSentryInitialization:
    """Test Sentry initialization"""
    
    @patch('app.utils.sentry.sentry_sdk.init')
    @patch.dict(os.environ, {'SENTRY_DSN': 'https://test@sentry.io/123', 'ENVIRONMENT': 'test'})
    def test_init_sentry_with_dsn(self, mock_init):
        """Test Sentry initializes with valid DSN"""
        init_sentry()
        
        assert mock_init.called
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs['dsn'] == 'https://test@sentry.io/123'
        assert call_kwargs['environment'] == 'test'
    
    @patch('app.utils.sentry.sentry_sdk.init')
    @patch.dict(os.environ, {'SENTRY_DSN': '', 'ENVIRONMENT': 'development'}, clear=True)
    def test_init_sentry_without_dsn(self, mock_init):
        """Test Sentry doesn't initialize without DSN"""
        init_sentry()
        
        assert not mock_init.called
    
    @patch('app.utils.sentry.sentry_sdk.init')
    @patch.dict(os.environ, {'SENTRY_DSN': 'https://test@sentry.io/123', 'ENVIRONMENT': 'development', 'DEBUG': 'true'})
    def test_init_sentry_development_mode(self, mock_init):
        """Test Sentry configuration in development"""
        init_sentry()
        
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs['environment'] == 'development'
        assert call_kwargs['debug'] is True
        assert call_kwargs['traces_sample_rate'] == 1.0  # 100% in dev
    
    @patch('app.utils.sentry.sentry_sdk.init')
    @patch.dict(os.environ, {'SENTRY_DSN': 'https://test@sentry.io/123', 'ENVIRONMENT': 'production', 'DEBUG': 'false'})
    def test_init_sentry_production_mode(self, mock_init):
        """Test Sentry configuration in production"""
        init_sentry()
        
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs['environment'] == 'production'
        assert call_kwargs['debug'] is False
        assert call_kwargs['traces_sample_rate'] == 0.2  # 20% in production
    
    @patch('app.utils.sentry.sentry_sdk.init')
    @patch.dict(os.environ, {'SENTRY_DSN': 'https://test@sentry.io/123', 'RELEASE_VERSION': '2.0.0'})
    def test_init_sentry_with_release_version(self, mock_init):
        """Test Sentry uses release version"""
        init_sentry()
        
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs['release'] == '2.0.0'
    
    @patch('app.utils.sentry.sentry_sdk.init')
    @patch.dict(os.environ, {'SENTRY_DSN': 'https://test@sentry.io/123'})
    def test_init_sentry_integrations(self, mock_init):
        """Test Sentry integrations are configured"""
        init_sentry()
        
        call_kwargs = mock_init.call_args[1]
        integrations = call_kwargs['integrations']
        
        assert len(integrations) > 0
        # Check that FastAPI, SQLAlchemy, and Logging integrations are present
        integration_types = [type(i).__name__ for i in integrations]
        assert 'FastApiIntegration' in integration_types
        assert 'SqlalchemyIntegration' in integration_types
        assert 'LoggingIntegration' in integration_types


class TestBeforeSendEvent:
    """Test before_send event filtering"""
    
    def test_before_send_filters_health_checks(self):
        """Test that health check errors are filtered out"""
        event = {
            'transaction': '/api/health/readiness',
            'exception': {'values': [{'type': 'TestError'}]}
        }
        
        result = before_send_event(event, {})
        assert result is None  # Should be filtered out
    
    def test_before_send_allows_regular_errors(self):
        """Test that regular errors are not filtered"""
        event = {
            'transaction': '/api/portfolio/upload',
            'exception': {'values': [{'type': 'ValueError'}]}
        }
        
        result = before_send_event(event, {})
        assert result is not None
        assert result == event
    
    @patch.dict(os.environ, {'RELEASE_VERSION': '1.5.0'})
    def test_before_send_adds_version_tag(self):
        """Test that app version is added to events"""
        event = {
            'transaction': '/api/test',
            'exception': {'values': [{'type': 'TestError'}]}
        }
        
        result = before_send_event(event, {})
        assert 'tags' in result
        assert result['tags']['app_version'] == '1.5.0'
    
    def test_before_send_preserves_existing_tags(self):
        """Test that existing tags are preserved"""
        event = {
            'transaction': '/api/test',
            'exception': {'values': [{'type': 'TestError'}]},
            'tags': {'custom_tag': 'custom_value'}
        }
        
        result = before_send_event(event, {})
        assert result['tags']['custom_tag'] == 'custom_value'


class TestBeforeBreadcrumb:
    """Test breadcrumb filtering"""
    
    def test_before_breadcrumb_filters_health_checks(self):
        """Test that health check breadcrumbs are filtered"""
        crumb = {
            'category': 'httplib',
            'data': {'url': 'http://localhost:8000/health'}
        }
        
        result = before_breadcrumb(crumb, {})
        assert result is None
    
    def test_before_breadcrumb_allows_regular_requests(self):
        """Test that regular breadcrumbs are not filtered"""
        crumb = {
            'category': 'httplib',
            'data': {'url': 'http://localhost:8000/api/portfolio'}
        }
        
        result = before_breadcrumb(crumb, {})
        assert result is not None
        assert result == crumb
    
    def test_before_breadcrumb_allows_non_http_breadcrumbs(self):
        """Test that non-HTTP breadcrumbs are not filtered"""
        crumb = {
            'category': 'navigation',
            'message': 'User navigated to dashboard'
        }
        
        result = before_breadcrumb(crumb, {})
        assert result is not None


class TestCaptureException:
    """Test manual exception capturing"""
    
    @patch('app.utils.sentry.sentry_sdk.capture_exception')
    @patch('app.utils.sentry.sentry_sdk.push_scope')
    def test_capture_exception_basic(self, mock_push_scope, mock_capture):
        """Test basic exception capturing"""
        error = ValueError("Test error")
        
        # Mock the context manager
        mock_scope = MagicMock()
        mock_push_scope.return_value.__enter__.return_value = mock_scope
        
        capture_exception(error)
        
        assert mock_capture.called
        mock_capture.assert_called_once_with(error)
    
    @patch('app.utils.sentry.sentry_sdk.capture_exception')
    @patch('app.utils.sentry.sentry_sdk.push_scope')
    def test_capture_exception_with_context(self, mock_push_scope, mock_capture):
        """Test exception capturing with context"""
        error = ValueError("Test error")
        context = {"user_id": 123, "portfolio_id": 456}
        
        mock_scope = MagicMock()
        mock_push_scope.return_value.__enter__.return_value = mock_scope
        
        capture_exception(error, context)
        
        # Verify context was set
        assert mock_scope.set_context.call_count == len(context)
        mock_capture.assert_called_once_with(error)


class TestCaptureMessage:
    """Test manual message capturing"""
    
    @patch('app.utils.sentry.sentry_sdk.capture_message')
    @patch('app.utils.sentry.sentry_sdk.push_scope')
    def test_capture_message_basic(self, mock_push_scope, mock_capture):
        """Test basic message capturing"""
        message = "Test message"
        
        mock_scope = MagicMock()
        mock_push_scope.return_value.__enter__.return_value = mock_scope
        
        capture_message(message)
        
        mock_capture.assert_called_once_with(message, level="info")
    
    @patch('app.utils.sentry.sentry_sdk.capture_message')
    @patch('app.utils.sentry.sentry_sdk.push_scope')
    def test_capture_message_with_level(self, mock_push_scope, mock_capture):
        """Test message capturing with custom level"""
        message = "Warning message"
        
        mock_scope = MagicMock()
        mock_push_scope.return_value.__enter__.return_value = mock_scope
        
        capture_message(message, level="warning")
        
        mock_capture.assert_called_once_with(message, level="warning")
    
    @patch('app.utils.sentry.sentry_sdk.capture_message')
    @patch('app.utils.sentry.sentry_sdk.push_scope')
    def test_capture_message_with_context(self, mock_push_scope, mock_capture):
        """Test message capturing with context"""
        message = "Portfolio uploaded"
        context = {"user_id": 123, "file_size": 1024}
        
        mock_scope = MagicMock()
        mock_push_scope.return_value.__enter__.return_value = mock_scope
        
        capture_message(message, context=context)
        
        assert mock_scope.set_context.call_count == len(context)


class TestSetUserContext:
    """Test user context setting"""
    
    @patch('app.utils.sentry.sentry_sdk.set_user')
    def test_set_user_context_all_fields(self, mock_set_user):
        """Test setting user context with all fields"""
        set_user_context(user_id=123, email="test@example.com", username="testuser")
        
        mock_set_user.assert_called_once_with({
            "id": 123,
            "email": "test@example.com",
            "username": "testuser"
        })
    
    @patch('app.utils.sentry.sentry_sdk.set_user')
    def test_set_user_context_partial_fields(self, mock_set_user):
        """Test setting user context with partial fields"""
        set_user_context(user_id=123)
        
        mock_set_user.assert_called_once_with({
            "id": 123,
            "email": None,
            "username": None
        })


class TestSetTransactionName:
    """Test transaction name setting"""
    
    @patch('app.utils.sentry.sentry_sdk.configure_scope')
    def test_set_transaction_name(self, mock_configure_scope):
        """Test setting custom transaction name"""
        mock_scope = MagicMock()
        mock_configure_scope.return_value.__enter__.return_value = mock_scope
        
        set_transaction_name("portfolio.upload")
        
        assert mock_scope.transaction == "portfolio.upload"


class TestAddBreadcrumb:
    """Test manual breadcrumb adding"""
    
    @patch('app.utils.sentry.sentry_sdk.add_breadcrumb')
    def test_add_breadcrumb_basic(self, mock_add):
        """Test adding basic breadcrumb"""
        add_breadcrumb("User clicked button")
        
        mock_add.assert_called_once()
        call_kwargs = mock_add.call_args[1]
        assert call_kwargs['message'] == "User clicked button"
        assert call_kwargs['category'] == "custom"
        assert call_kwargs['level'] == "info"
    
    @patch('app.utils.sentry.sentry_sdk.add_breadcrumb')
    def test_add_breadcrumb_with_data(self, mock_add):
        """Test adding breadcrumb with data"""
        add_breadcrumb(
            "Portfolio uploaded",
            category="action",
            level="info",
            data={"file_size": 1024, "user_id": 123}
        )
        
        call_kwargs = mock_add.call_args[1]
        assert call_kwargs['message'] == "Portfolio uploaded"
        assert call_kwargs['category'] == "action"
        assert call_kwargs['data']['file_size'] == 1024
        assert call_kwargs['data']['user_id'] == 123
