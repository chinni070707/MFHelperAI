"""
Sentry Integration for Error Tracking and Performance Monitoring
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
import os


def init_sentry():
    """
    Initialize Sentry for error tracking and performance monitoring
    
    Features:
    - Automatic error capturing
    - Performance transaction tracking
    - Breadcrumbs for debugging
    - User context tracking
    - SQL query tracking
    """
    sentry_dsn = os.getenv("SENTRY_DSN", "")
    environment = os.getenv("ENVIRONMENT", "development")
    debug_mode = os.getenv("DEBUG", "true").lower() == "true"
    
    # Only initialize Sentry if DSN is provided
    if not sentry_dsn or sentry_dsn == "":
        logging.info("Sentry DSN not configured. Skipping Sentry initialization.")
        logging.info("To enable Sentry: Set SENTRY_DSN environment variable")
        return
    
    # Initialize Sentry
    sentry_sdk.init(
        dsn=sentry_dsn,
        
        # Set environment (production, staging, development)
        environment=environment,
        
        # Enable debug mode in development
        debug=debug_mode and environment == "development",
        
        # Sample rate for performance monitoring
        # 1.0 = 100% of transactions, 0.1 = 10% of transactions
        traces_sample_rate=1.0 if environment == "development" else 0.2,
        
        # Sample rate for error events
        # 1.0 = capture all errors
        sample_rate=1.0,
        
        # Integrations
        integrations=[
            # FastAPI integration - automatic request tracking
            FastApiIntegration(
                transaction_style="endpoint",  # Group by endpoint
                failed_request_status_codes=[500, 501, 502, 503, 504]
            ),
            
            # SQLAlchemy integration - track database queries
            SqlalchemyIntegration(),
            
            # Logging integration - capture log messages
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above
                event_level=logging.ERROR  # Send errors as events
            ),
        ],
        
        # Release tracking (use git commit or version)
        release=os.getenv("RELEASE_VERSION", "1.0.0"),
        
        # Maximum breadcrumbs to store
        max_breadcrumbs=50,
        
        # Attach stack traces to messages
        attach_stacktrace=True,
        
        # Send default PII (Personally Identifiable Information)
        # Set to False in production if you don't want to send user IPs, cookies, etc.
        send_default_pii=False,
        
        # Before send callback - filter or modify events
        before_send=before_send_event,
        
        # Before breadcrumb callback - filter breadcrumbs
        before_breadcrumb=before_breadcrumb,
    )
    
    logging.info(f"✅ Sentry initialized - Environment: {environment}, DSN: {sentry_dsn[:20]}...")


def before_send_event(event, hint):
    """
    Filter or modify events before sending to Sentry
    
    Use cases:
    - Remove sensitive data
    - Skip certain errors
    - Add custom tags or context
    """
    # Skip health check errors
    if event.get('transaction', '').startswith('/api/health'):
        return None
    
    # Add custom tags
    event.setdefault('tags', {})
    event['tags']['app_version'] = os.getenv("RELEASE_VERSION", "1.0.0")
    
    # Log what we're sending
    error_type = event.get('exception', {}).get('values', [{}])[0].get('type', 'Unknown')
    logging.debug(f"Sending error to Sentry: {error_type}")
    
    return event


def before_breadcrumb(crumb, hint):
    """
    Filter or modify breadcrumbs before adding to Sentry
    
    Breadcrumbs help trace user actions leading to an error
    """
    # Skip health check breadcrumbs
    if crumb.get('category') == 'httplib' and '/health' in crumb.get('data', {}).get('url', ''):
        return None
    
    return crumb


def capture_exception(error: Exception, context: dict = None):
    """
    Manually capture an exception with additional context
    
    Args:
        error: The exception to capture
        context: Additional context dict
    
    Example:
        try:
            process_portfolio(data)
        except Exception as e:
            capture_exception(e, {"portfolio_id": portfolio.id, "user_id": user.id})
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None):
    """
    Manually capture a message (not an error)
    
    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context dict
    
    Example:
        capture_message("Portfolio uploaded successfully", "info", {"user_id": 123})
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: int = None, email: str = None, username: str = None):
    """
    Set user context for error tracking
    
    This helps identify which users are experiencing errors
    
    Args:
        user_id: User's ID
        email: User's email
        username: User's username
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username
    })


def set_transaction_name(name: str):
    """
    Set custom transaction name for performance monitoring
    
    Args:
        name: Transaction name (e.g., "portfolio.upload", "analytics.calculate")
    """
    with sentry_sdk.configure_scope() as scope:
        scope.transaction = name


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", data: dict = None):
    """
    Add a breadcrumb to help debug issues
    
    Args:
        message: Breadcrumb message
        category: Category (http, navigation, ui, etc.)
        level: Severity level
        data: Additional data dict
    
    Example:
        add_breadcrumb("User uploaded portfolio", "action", "info", {"file_size": 1024})
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
