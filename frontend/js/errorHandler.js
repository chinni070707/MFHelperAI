/**
 * Error Handler & Logger
 * Catches and logs all errors with context
 */

class ErrorHandler {
    constructor() {
        this.errors = [];
        this.maxErrors = 100;
        this.setupGlobalHandlers();
    }

    setupGlobalHandlers() {
        // Catch unhandled errors
        window.addEventListener('error', (event) => {
            this.log({
                type: 'ERROR',
                message: event.message,
                source: event.filename,
                line: event.lineno,
                column: event.colno,
                error: event.error?.stack
            });
        });

        // Catch unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.log({
                type: 'PROMISE_REJECTION',
                message: event.reason?.message || event.reason,
                error: event.reason?.stack
            });
        });
    }

    log(errorData) {
        const entry = {
            ...errorData,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };

        // Add to local history
        this.errors.push(entry);
        if (this.errors.length > this.maxErrors) {
            this.errors.shift();
        }

        // Log to console
        console.error('[ErrorHandler]', entry);

        // Store in localStorage for debugging
        try {
            localStorage.setItem('mfhelper_last_error', JSON.stringify(entry));
            localStorage.setItem('mfhelper_error_count', 
                (parseInt(localStorage.getItem('mfhelper_error_count') || '0') + 1).toString()
            );
        } catch (e) {
            // Ignore localStorage errors
        }

        // Send to backend (if implemented)
        this.sendToBackend(entry);

        return entry;
    }

    async sendToBackend(errorData) {
        // Send to backend error logging endpoint
        try {
            await fetch('/api/errors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(errorData)
            });
        } catch (e) {
            // Fail silently - don't break app if logging fails
            console.warn('Failed to send error to backend:', e);
        }
    }

    handleAPIError(error, context = {}) {
        const errorData = {
            type: 'API_ERROR',
            message: error.message || 'API request failed',
            context: context,
            error: error.stack
        };

        this.log(errorData);

        // Show user-friendly toast
        if (error.response?.status === 413) {
            toast.error('File is too large. Please upload a smaller file.');
        } else if (error.response?.status === 400) {
            toast.error('Invalid file format. Please check your Excel file.');
        } else if (error.response?.status >= 500) {
            toast.error('Server error. Please try again later.');
        } else if (!navigator.onLine) {
            toast.error('No internet connection. Please check your network.');
        } else {
            toast.error('Something went wrong. Please try again.');
        }

        return errorData;
    }

    handleFileError(error, fileName) {
        const errorData = {
            type: 'FILE_ERROR',
            message: error.message || 'File processing failed',
            fileName: fileName,
            error: error.stack
        };

        this.log(errorData);

        // User-friendly messages
        if (error.message.includes('format')) {
            toast.error(`Invalid file format: ${fileName}`);
        } else if (error.message.includes('size')) {
            toast.error('File is too large. Maximum size is 10MB.');
        } else if (error.message.includes('parse')) {
            toast.error('Could not read file. Please check the file format.');
        } else {
            toast.error(`Error processing file: ${fileName}`);
        }

        return errorData;
    }

    getErrorHistory() {
        return this.errors;
    }

    clearHistory() {
        this.errors = [];
        localStorage.removeItem('mfhelper_last_error');
        localStorage.removeItem('mfhelper_error_count');
    }

    getStats() {
        const errorCount = parseInt(localStorage.getItem('mfhelper_error_count') || '0');
        return {
            totalErrors: errorCount,
            sessionErrors: this.errors.length,
            lastError: this.errors[this.errors.length - 1]
        };
    }
}

// Create global instance
const errorHandler = new ErrorHandler();
window.errorHandler = errorHandler;

/**
 * Utility function for safe async operations
 */
async function safeAsync(fn, errorMessage = 'Operation failed') {
    try {
        return await fn();
    } catch (error) {
        errorHandler.log({
            type: 'SAFE_ASYNC_ERROR',
            message: errorMessage,
            error: error.stack
        });
        toast.error(errorMessage);
        return null;
    }
}

window.safeAsync = safeAsync;

/**
 * Loading state manager
 */
class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
    }

    show(message = 'Loading...', id = 'default') {
        const loadingToast = toast.loading(message);
        this.activeLoaders.set(id, loadingToast);
        return id;
    }

    hide(id = 'default') {
        const loadingToast = this.activeLoaders.get(id);
        if (loadingToast) {
            toast.hideLoading(loadingToast);
            this.activeLoaders.delete(id);
        }
    }

    hideAll() {
        this.activeLoaders.forEach((loadingToast) => {
            toast.hideLoading(loadingToast);
        });
        this.activeLoaders.clear();
    }
}

const loading = new LoadingManager();
window.loading = loading;
