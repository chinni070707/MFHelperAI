/**
 * Guest Mode Banner
 * Shows limitations banner for guest users with localStorage-only data
 */

class GuestBanner {
    constructor() {
        this.banner = null;
        this.isGuest = this.checkGuestMode();
    }

    checkGuestMode() {
        return localStorage.getItem('portfolioMode') === 'guest';
    }

    create() {
        if (!this.isGuest) return null;

        const daysLeft = this.getDaysUntilExpiry();
        const banner = document.createElement('div');
        banner.id = 'guestBanner';
        banner.className = 'guest-banner';
        banner.innerHTML = `
            <div class="guest-banner-content">
                <div class="guest-banner-icon">⚠️</div>
                <div class="guest-banner-text">
                    <strong>Guest Mode - Data stored locally</strong>
                    <span>Your portfolio expires in ${daysLeft} days. Sign up to save permanently and access from any device.</span>
                </div>
                <button class="guest-banner-btn" onclick="guestBanner.showSignup()">
                    Sign Up to Save
                </button>
                <button class="guest-banner-close" onclick="guestBanner.dismiss()" title="Dismiss">
                    ×
                </button>
            </div>
        `;

        this.banner = banner;
        return banner;
    }

    getDaysUntilExpiry() {
        if (typeof portfolioStorage !== 'undefined') {
            return portfolioStorage.getDaysUntilExpiry();
        }
        return 30;
    }

    show() {
        if (!this.isGuest) return;

        // Check if banner already exists
        if (document.getElementById('guestBanner')) return;

        const banner = this.create();
        if (banner) {
            const body = document.body;
            if (body.firstChild) {
                body.insertBefore(banner, body.firstChild);
            } else {
                body.appendChild(banner);
            }

            document.body.style.paddingTop = '70px';
        }
    }

    dismiss() {
        if (this.banner) {
            this.banner.style.display = 'none';
            document.body.style.paddingTop = '0';
            sessionStorage.setItem('guestBannerDismissed', 'true');
        }
    }

    showSignup() {
        if (typeof showSignupModal === 'function') {
            showSignupModal();
        } else {
            window.location.href = '/signup?source=guest-banner';
        }
    }

    static getStyles() {
        return `
            .guest-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, rgba(255, 152, 0, 0.95) 0%, rgba(255, 87, 34, 0.95) 100%);
                backdrop-filter: blur(10px);
                border-bottom: 2px solid rgba(255, 255, 255, 0.2);
                z-index: 9999;
                animation: slideDown 0.3s ease-out;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }

            .guest-banner-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 12px 20px;
                display: flex;
                align-items: center;
                gap: 15px;
                color: white;
            }

            .guest-banner-icon {
                font-size: 1.8rem;
                animation: pulse 2s infinite;
            }

            .guest-banner-text {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 2px;
            }

            .guest-banner-text strong {
                font-size: 1rem;
                font-weight: 600;
            }

            .guest-banner-text span {
                font-size: 0.85rem;
                opacity: 0.95;
            }

            .guest-banner-btn {
                padding: 10px 24px;
                background: white;
                color: #ff5722;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.3s;
                white-space: nowrap;
            }

            .guest-banner-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
            }

            .guest-banner-close {
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

            .guest-banner-close:hover {
                opacity: 1;
            }

            @media (max-width: 768px) {
                .guest-banner-content {
                    flex-wrap: wrap;
                    padding: 10px 15px;
                    gap: 10px;
                }

                .guest-banner-text span {
                    font-size: 0.8rem;
                }

                .guest-banner-btn {
                    padding: 8px 16px;
                    font-size: 0.85rem;
                }
            }
        `;
    }
}

// Initialize global instance
const guestBanner = new GuestBanner();

// Auto-show on page load if guest mode and not dismissed
window.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('guestBannerDismissed')) {
        guestBanner.show();
    }
});

// Inject styles
const style = document.createElement('style');
style.textContent = GuestBanner.getStyles();
document.head.appendChild(style);
