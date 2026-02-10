/**
 * Demo Portfolio Banner Component
 * Shows a banner when user is viewing demo data
 * Prompts user to sign up to save their portfolio
 */

class DemoBanner {
    constructor() {
        this.banner = null;
        this.isDemo = this.checkDemoMode();
    }

    checkDemoMode() {
        return localStorage.getItem('portfolioMode') === 'demo';
    }

    create() {
        if (!this.isDemo) return null;

        const banner = document.createElement('div');
        banner.id = 'demoBanner';
        banner.className = 'demo-banner';
        banner.innerHTML = `
            <div class="demo-banner-content">
                <div class="demo-banner-icon">📊</div>
                <div class="demo-banner-text">
                    <strong>You're viewing demo data</strong>
                    <span>Sign up to save your own portfolio and access all features</span>
                </div>
                <button class="demo-banner-btn" onclick="demoBanner.showSignup()">
                    Sign Up Free
                </button>
                <button class="demo-banner-close" onclick="demoBanner.dismiss()" title="Dismiss">
                    ×
                </button>
            </div>
        `;

        this.banner = banner;
        return banner;
    }

    show() {
        if (!this.isDemo) return;

        // Check if banner already exists
        if (document.getElementById('demoBanner')) return;

        const banner = this.create();
        if (banner) {
            // Insert at the top of the page content
            const body = document.body;
            if (body.firstChild) {
                body.insertBefore(banner, body.firstChild);
            } else {
                body.appendChild(banner);
            }

            // Add to page top margin to prevent content overlap
            document.body.style.paddingTop = '70px';
        }
    }

    dismiss() {
        if (this.banner) {
            this.banner.style.display = 'none';
            document.body.style.paddingTop = '0';
            
            // Remember dismissal for this session
            sessionStorage.setItem('demoBannerDismissed', 'true');
        }
    }

    showSignup() {
        // Trigger signup modal (will be implemented in auth module)
        if (typeof showSignupModal === 'function') {
            showSignupModal();
        } else {
            // Fallback: redirect to signup page
            window.location.href = '/signup?source=demo-banner';
        }
    }

    static getStyles() {
        return `
            .demo-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
                backdrop-filter: blur(10px);
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
                z-index: 9999;
                animation: slideDown 0.3s ease-out;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }

            .demo-banner-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 12px 20px;
                display: flex;
                align-items: center;
                gap: 15px;
                color: white;
            }

            .demo-banner-icon {
                font-size: 1.8rem;
                animation: pulse 2s infinite;
            }

            .demo-banner-text {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 2px;
            }

            .demo-banner-text strong {
                font-size: 1rem;
                font-weight: 600;
            }

            .demo-banner-text span {
                font-size: 0.85rem;
                opacity: 0.9;
            }

            .demo-banner-btn {
                padding: 10px 24px;
                background: white;
                color: #667eea;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.3s;
                white-space: nowrap;
            }

            .demo-banner-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
            }

            .demo-banner-close {
                background: transparent;
                border: none;
                color: white;
                font-size: 2rem;
                line-height: 1;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.3s;
                padding: 0 8px;
            }

            .demo-banner-close:hover {
                opacity: 1;
            }

            @keyframes slideDown {
                from {
                    transform: translateY(-100%);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }

            @keyframes pulse {
                0%, 100% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.1);
                }
            }

            @media (max-width: 768px) {
                .demo-banner-content {
                    flex-wrap: wrap;
                    padding: 10px 15px;
                    gap: 10px;
                }

                .demo-banner-text span {
                    display: none;
                }

                .demo-banner-btn {
                    padding: 8px 16px;
                    font-size: 0.85rem;
                }
            }
        `;
    }
}

// Initialize global instance
const demoBanner = new DemoBanner();

// Auto-show on page load if demo mode and not dismissed
window.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('demoBannerDismissed')) {
        demoBanner.show();
    }
});

// Inject styles
// Inject styles (use IIFE to avoid const redeclaration collisions with other scripts)
(function() {
    const demoBannerStyle = document.createElement('style');
    demoBannerStyle.textContent = DemoBanner.getStyles();
    document.head.appendChild(demoBannerStyle);
})();
