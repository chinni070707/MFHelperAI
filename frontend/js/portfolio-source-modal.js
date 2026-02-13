/**
 * Portfolio Source Modal
 * Shows options for loading demo, adding portfolio, or continuing with existing data
 */

class PortfolioSourceModal {
    constructor() {
        this.modal = null;
        this.init();
    }

    init() {
        // Inject styles into <head> — safe even before <body> exists
        if (document.head) {
            const style = document.createElement('style');
            style.textContent = this.getStyles();
            document.head.appendChild(style);
        }

        // Defer modal creation until <body> is available
        if (document.body) {
            this.createModal();
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                this.createModal();
            });
        }
    }

    createModal() {
        const modal = document.createElement('div');
        modal.id = 'portfolioSourceModal';
        modal.className = 'portfolio-source-modal';
        modal.innerHTML = `
            <div class="portfolio-source-content">
                <div class="portfolio-source-header">
                    <h2>Choose Portfolio Source</h2>
                    <p>Select how you'd like to get started</p>
                </div>

                <div class="portfolio-source-options">
                    <div class="source-option" onclick="portfolioSourceModal.loadDemo()">
                        <div class="source-icon">📊</div>
                        <h3>Load Demo Portfolio</h3>
                        <p>Explore features with sample data. No signup required.</p>
                        <button class="source-btn btn-secondary">Try Demo</button>
                    </div>

                    <div class="source-option featured" onclick="portfolioSourceModal.addPortfolio()">
                        <div class="source-badge">Recommended</div>
                        <div class="source-icon">📁</div>
                        <h3>Add Your Portfolio</h3>
                        <p>Upload CAS or enter manually to analyze your investments.</p>
                        <button class="source-btn btn-primary">Get Started</button>
                    </div>

                    <div class="source-option" onclick="portfolioSourceModal.continueExisting()">
                        <div class="source-icon">📋</div>
                        <h3>Continue with Existing</h3>
                        <p>Resume with previously saved portfolio data.</p>
                        <button class="source-btn btn-secondary">Continue</button>
                    </div>
                </div>

                <div class="portfolio-source-footer">
                    <button class="link-btn" onclick="portfolioSourceModal.close()">Close</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.modal = modal;
    }

    show() {
        if (this.modal) {
            this.modal.style.display = 'flex';
        }
    }

    close() {
        if (this.modal) {
            this.modal.style.display = 'none';
        }
    }

    async loadDemo() {
        this.close();
        
        // Set demo mode
        localStorage.setItem('portfolioMode', 'demo');
        localStorage.setItem('demoLoadedAt', new Date().toISOString());
        
        // Show loading
        if (typeof showToast === 'function') {
            showToast('Loading demo portfolio...', 'info');
        }
        
        try {
            // Fetch demo data from API
            const response = await fetch('/api/demo/portfolio');
            const data = await response.json();
            
            if (data.success) {
                // Save to localStorage
                if (typeof portfolioStorage !== 'undefined') {
                    portfolioStorage.saveDemoData(data);
                }
                
                // Reload page to show demo data
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            } else {
                throw new Error('Failed to load demo portfolio');
            }
        } catch (error) {
            console.error('Demo load error:', error);
            if (typeof showToast === 'function') {
                showToast('Failed to load demo portfolio', 'error');
            }
        }
    }

    addPortfolio() {
        this.close();
        
        // Show upload modal if available
        if (typeof showUploadModal === 'function') {
            showUploadModal();
        } else {
            // Redirect to dashboard with upload parameter
            window.location.href = '/dashboard?upload=true';
        }
    }

    continueExisting() {
        this.close();
        
        // Check if there's existing data
        if (typeof portfolioStorage !== 'undefined') {
            const existing = portfolioStorage.getCurrentPortfolio();
            if (existing) {
                // Reload page with existing data
                window.location.reload();
            } else {
                if (typeof showToast === 'function') {
                    showToast('No existing portfolio found', 'error');
                }
                // Show modal again
                setTimeout(() => this.show(), 1000);
            }
        }
    }

    getStyles() {
        return `
            .portfolio-source-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.85);
                backdrop-filter: blur(10px);
                z-index: 10000;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s;
            }

            .portfolio-source-content {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 20px;
                padding: 40px;
                max-width: 900px;
                width: 90%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .portfolio-source-header {
                text-align: center;
                margin-bottom: 40px;
            }

            .portfolio-source-header h2 {
                font-size: 2rem;
                color: #fff;
                margin-bottom: 10px;
            }

            .portfolio-source-header p {
                color: rgba(255, 255, 255, 0.7);
                font-size: 1.1rem;
            }

            .portfolio-source-options {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .source-option {
                background: rgba(255, 255, 255, 0.03);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px 20px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                position: relative;
            }

            .source-option:hover {
                transform: translateY(-5px);
                border-color: #00d4ff;
                background: rgba(0, 212, 255, 0.05);
                box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
            }

            .source-option.featured {
                border-color: #00d4ff;
                background: rgba(0, 212, 255, 0.08);
            }

            .source-badge {
                position: absolute;
                top: -10px;
                right: 15px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
            }

            .source-icon {
                font-size: 3rem;
                margin-bottom: 15px;
            }

            .source-option h3 {
                color: #fff;
                font-size: 1.3rem;
                margin-bottom: 10px;
            }

            .source-option p {
                color: rgba(255, 255, 255, 0.7);
                font-size: 0.95rem;
                margin-bottom: 20px;
                line-height: 1.5;
            }

            .source-btn {
                width: 100%;
                padding: 12px 24px;
                border-radius: 10px;
                border: none;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s;
            }

            .btn-primary {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
            }

            .btn-primary:hover {
                transform: scale(1.05);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }

            .btn-secondary {
                background: rgba(255, 255, 255, 0.1);
                color: #fff;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.15);
            }

            .portfolio-source-footer {
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }

            .link-btn {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                cursor: pointer;
                font-size: 1rem;
                padding: 8px 16px;
                transition: color 0.3s;
            }

            .link-btn:hover {
                color: #fff;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @media (max-width: 768px) {
                .portfolio-source-content {
                    padding: 30px 20px;
                }

                .portfolio-source-options {
                    grid-template-columns: 1fr;
                }

                .portfolio-source-header h2 {
                    font-size: 1.5rem;
                }
            }
        `;
    }
}

// Initialize global instance
const portfolioSourceModal = new PortfolioSourceModal();

// Auto-show on pages with empty portfolio state
window.addEventListener('DOMContentLoaded', () => {
    // Check if this is a feature page and has no data
    const isFeaturePage = window.location.pathname.includes('dashboard') || 
                          window.location.pathname.includes('overlap') ||
                          window.location.pathname.includes('stock-allocation') ||
                          window.location.pathname.includes('goal-checker') ||
                          window.location.pathname.includes('fund-reallocator');
    
    if (isFeaturePage && typeof portfolioStorage !== 'undefined') {
        // Don't show modal if user is authenticated (data lives server-side)
        const authToken = localStorage.getItem('authToken');
        const mode = localStorage.getItem('portfolioMode');
        if (authToken || mode === 'authenticated') {
            return; // Authenticated users load from database, no modal needed
        }

        const hasData = portfolioStorage.getCurrentPortfolio() !== null;
        const urlParams = new URLSearchParams(window.location.search);
        const forceShow = urlParams.get('source') === 'select';
        
        if (!hasData || forceShow) {
            setTimeout(() => portfolioSourceModal.show(), 500);
        }
    }
});
