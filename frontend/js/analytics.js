/**
 * Google Analytics Tracking Utility for MFHelper
 * Provides consistent event tracking across the application
 */

// Configuration - Replace with your actual GA4 Measurement ID
const GA_MEASUREMENT_ID = 'G-XXXXXXXXXX'; // TODO: Replace with actual ID from Google Analytics

/**
 * Initialize Google Analytics
 * Call this once when the page loads
 */
function initGoogleAnalytics() {
    // Check if already initialized
    if (window.GA_INITIALIZED) {
        return;
    }

    // Load GA4 script
    const script1 = document.createElement('script');
    script1.async = true;
    script1.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
    document.head.appendChild(script1);

    // Initialize gtag
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', GA_MEASUREMENT_ID, {
        send_page_view: true,
        page_path: window.location.pathname
    });

    window.gtag = gtag;
    window.GA_INITIALIZED = true;
    
    console.log('✓ Google Analytics initialized');
}

/**
 * Track custom events
 * @param {string} eventName - Name of the event
 * @param {object} params - Event parameters
 */
function trackEvent(eventName, params = {}) {
    if (typeof gtag === 'undefined') {
        console.warn('Google Analytics not loaded');
        return;
    }

    gtag('event', eventName, params);
    console.log(`📊 Event tracked: ${eventName}`, params);
}

/**
 * Track page views (for SPA navigation)
 * @param {string} pagePath - Path of the page
 * @param {string} pageTitle - Title of the page
 */
function trackPageView(pagePath, pageTitle) {
    if (typeof gtag === 'undefined') {
        console.warn('Google Analytics not loaded');
        return;
    }

    gtag('config', GA_MEASUREMENT_ID, {
        page_path: pagePath,
        page_title: pageTitle
    });
    
    console.log(`📄 Page view tracked: ${pageTitle} (${pagePath})`);
}

// ============================================================================
// Pre-defined Event Tracking Functions
// ============================================================================

/**
 * Track portfolio upload
 * @param {string} source - Upload source (excel, cas_pdf, manual)
 * @param {number} fundCount - Number of funds in portfolio
 * @param {number} totalValue - Total portfolio value
 */
function trackPortfolioUpload(source, fundCount, totalValue) {
    trackEvent('portfolio_upload', {
        upload_source: source,
        fund_count: fundCount,
        portfolio_value: totalValue,
        portfolio_value_bucket: getValueBucket(totalValue)
    });
}

/**
 * Track user sign up
 * @param {string} method - Sign up method (email, google, etc.)
 */
function trackSignUp(method = 'email') {
    trackEvent('sign_up', {
        method: method
    });
}

/**
 * Track user login
 * @param {string} method - Login method
 */
function trackLogin(method = 'email') {
    trackEvent('login', {
        method: method
    });
}

/**
 * Track feature usage
 * @param {string} featureName - Name of the feature
 * @param {object} additionalParams - Additional parameters
 */
function trackFeatureUsage(featureName, additionalParams = {}) {
    trackEvent('feature_used', {
        feature_name: featureName,
        ...additionalParams
    });
}

/**
 * Track analysis tool usage
 * @param {string} toolName - Name of the analysis tool (overlap, rebalance, xirr, etc.)
 */
function trackAnalysisTool(toolName) {
    trackEvent('analysis_tool_used', {
        tool_name: toolName
    });
}

/**
 * Track export action
 * @param {string} format - Export format (pdf, excel, csv)
 */
function trackExport(format) {
    trackEvent('export', {
        format: format
    });
}

/**
 * Track error
 * @param {string} errorType - Type of error
 * @param {string} errorMessage - Error message
 */
function trackError(errorType, errorMessage) {
    trackEvent('error', {
        error_type: errorType,
        error_message: errorMessage
    });
}

/**
 * Track search
 * @param {string} searchTerm - What user searched for
 * @param {string} searchContext - Where the search happened
 */
function trackSearch(searchTerm, searchContext = 'general') {
    trackEvent('search', {
        search_term: searchTerm,
        search_context: searchContext
    });
}

/**
 * Track CTA click
 * @param {string} ctaName - Name/ID of the CTA button
 * @param {string} location - Where the CTA is located
 */
function trackCTAClick(ctaName, location) {
    trackEvent('cta_click', {
        cta_name: ctaName,
        cta_location: location
    });
}

/**
 * Track time on page
 * Call this when user leaves the page
 * @param {number} seconds - Time spent on page in seconds
 */
function trackTimeOnPage(seconds) {
    trackEvent('time_on_page', {
        duration_seconds: seconds,
        duration_minutes: Math.round(seconds / 60)
    });
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get value bucket for portfolio value
 * @param {number} value - Portfolio value
 * @returns {string} - Value bucket
 */
function getValueBucket(value) {
    if (value < 100000) return '0-1L';
    if (value < 500000) return '1-5L';
    if (value < 1000000) return '5-10L';
    if (value < 2500000) return '10-25L';
    if (value < 5000000) return '25-50L';
    if (value < 10000000) return '50L-1Cr';
    return '1Cr+';
}

/**
 * Track time on page automatically
 * Call this once when page loads
 */
function setupTimeTracking() {
    const startTime = Date.now();
    
    // Track time when user leaves
    window.addEventListener('beforeunload', () => {
        const timeSpent = Math.round((Date.now() - startTime) / 1000);
        trackTimeOnPage(timeSpent);
    });
    
    // Track time when page is hidden (mobile/tab switch)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            const timeSpent = Math.round((Date.now() - startTime) / 1000);
            trackTimeOnPage(timeSpent);
        }
    });
}

// ============================================================================
// Auto-initialization
// ============================================================================

// Initialize on DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initGoogleAnalytics();
        setupTimeTracking();
    });
} else {
    // DOM already loaded
    initGoogleAnalytics();
    setupTimeTracking();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initGoogleAnalytics,
        trackEvent,
        trackPageView,
        trackPortfolioUpload,
        trackSignUp,
        trackLogin,
        trackFeatureUsage,
        trackAnalysisTool,
        trackExport,
        trackError,
        trackSearch,
        trackCTAClick,
        trackTimeOnPage
    };
}
