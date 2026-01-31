/**
 * Toast Notification System
 * Lightweight, no dependencies, works everywhere
 */

// Ensure toast is defined immediately as a stub (will be replaced)
window.toast = window.toast || {
    success: (msg) => console.log('[Toast]', msg),
    error: (msg) => console.error('[Toast]', msg),
    warning: (msg) => console.warn('[Toast]', msg),
    info: (msg) => console.log('[Toast]', msg),
    loading: (msg) => { console.log('[Toast Loading]', msg); return null; },
    hideLoading: () => {}
};

class ToastManager {
    constructor() {
        this.container = null;
        this.initialized = false;
    }
    
    init() {
        if (this.initialized) return;
        this.container = this.createContainer();
        document.body.appendChild(this.container);
        this.initialized = true;
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;
        return container;
    }

    show(message, type = 'info', duration = 4000) {
        // Lazy init - wait for document.body
        if (!this.initialized) {
            if (document.body) {
                this.init();
            } else {
                // Queue for later
                document.addEventListener('DOMContentLoaded', () => {
                    this.init();
                    this.show(message, type, duration);
                });
                return null;
            }
        }
        
        const toast = this.createToast(message, type);
        this.container.appendChild(toast);

        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }

        return toast;
    }

    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const colors = {
            success: '#22c55e',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="toast.remove(this.parentElement)">×</button>
        `;

        toast.style.cssText = `
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid ${colors[type] || colors.info};
            border-left: 4px solid ${colors[type] || colors.info};
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 300px;
            max-width: 400px;
            pointer-events: all;
            transform: translateX(400px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        `;

        // Icon styles
        const iconEl = toast.querySelector('.toast-icon');
        iconEl.style.cssText = `
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: ${colors[type] || colors.info};
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        `;

        // Message styles
        const messageEl = toast.querySelector('.toast-message');
        messageEl.style.cssText = `
            flex: 1;
            font-size: 14px;
            line-height: 1.5;
        `;

        // Close button styles
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.style.cssText = `
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            cursor: pointer;
            font-size: 24px;
            line-height: 1;
            padding: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: color 0.2s;
        `;

        closeBtn.onmouseover = () => closeBtn.style.color = 'white';
        closeBtn.onmouseout = () => closeBtn.style.color = 'rgba(255, 255, 255, 0.6)';

        return toast;
    }

    remove(toast) {
        toast.style.transform = 'translateX(400px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    loading(message) {
        const toast = this.show(message, 'info', 0);
        const icon = toast.querySelector('.toast-icon');
        icon.innerHTML = '⟳';
        icon.style.animation = 'spin 1s linear infinite';
        
        // Add spin animation if not exists
        if (!document.getElementById('toast-spin-animation')) {
            const style = document.createElement('style');
            style.id = 'toast-spin-animation';
            style.textContent = `
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                .toast.show {
                    transform: translateX(0) !important;
                    opacity: 1 !important;
                }
            `;
            document.head.appendChild(style);
        }
        
        return toast;
    }

    hideLoading(toast) {
        if (toast) {
            this.remove(toast);
        }
    }
}

// Create global instance
const toast = new ToastManager();

// Expose to window for easy access
window.toast = toast;
