/**
 * Conversion Prompts
 * Timed popups and nudges for customer acquisition
 */

class ConversionPrompts {
    constructor() {
        this.featureInteractionCount = 0;
        this.demoStartTime = null;
        this.timersSet = false;
        this.init();
    }

    init() {
        // Inject CSS
        const style = document.createElement('style');
        style.textContent = this.getStyles();
        document.head.appendChild(style);

        // Check if in demo mode
        if (localStorage.getItem('portfolioMode') === 'demo') {
            this.demoStartTime = localStorage.getItem('demoLoadedAt');
            this.setupTimers();
        }

        // Track feature interactions
        this.trackFeatureInteractions();
    }

    setupTimers() {
        if (this.timersSet) return;
        this.timersSet = true;

        // Show prompt after 5 minutes
        setTimeout(() => {
            if (!this.hasSignedUp()) {
                this.showTimedPrompt();
            }
        }, 5 * 60 * 1000); // 5 minutes

        // Show progress save prompt after 2 minutes
        setTimeout(() => {
            if (!this.hasSignedUp()) {
                this.showProgressPrompt();
            }
        }, 2 * 60 * 1000); // 2 minutes
    }

    trackFeatureInteractions() {
        // Track clicks on analysis features
        document.addEventListener('click', (e) => {
            const featureElements = e.target.closest('[data-feature]');
            if (featureElements) {
                this.featureInteractionCount++;
                
                // Show prompt after 3 feature interactions
                if (this.featureInteractionCount === 3 && !this.hasSignedUp()) {
                    setTimeout(() => this.showFeaturePrompt(), 2000);
                }
            }
        });
    }

    hasSignedUp() {
        return localStorage.getItem('authToken') !== null;
    }

    showTimedPrompt() {
        this.showPrompt(
            '⏰ Still Exploring?',
            'You\'ve been using MFHelper for 5 minutes. Sign up to save your analysis and access advanced features!',
            'timed-prompt'
        );
    }

    showProgressPrompt() {
        this.showPrompt(
            '💾 Save Your Progress',
            'Don\'t lose your work! Create a free account to save your portfolio and analysis permanently.',
            'progress-prompt'
        );
    }

    showFeaturePrompt() {
        this.showPrompt(
            '🎯 Unlock More Features',
            'Great! You\'re exploring multiple features. Sign up to unlock advanced analytics and save your data.',
            'feature-prompt'
        );
    }

    showPrompt(title, message, source) {
        // Don't show if already dismissed this session
        if (sessionStorage.getItem(`prompt_${source}_dismissed`)) {
            return;
        }

        const prompt = document.createElement('div');
        prompt.className = 'conversion-prompt';
        prompt.innerHTML = `
            <div class="conversion-prompt-content">
                <button class="conversion-prompt-close" onclick="conversionPrompts.dismissPrompt('${source}')">&times;</button>
                <h3>${title}</h3>
                <p>${message}</p>
                <div class="conversion-prompt-actions">
                    <button class="conversion-btn-primary" onclick="conversionPrompts.handleSignup('${source}')">
                        Sign Up Free
                    </button>
                    <button class="conversion-btn-secondary" onclick="conversionPrompts.dismissPrompt('${source}')">
                        Maybe Later
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(prompt);

        // Animate in
        setTimeout(() => {
            prompt.classList.add('show');
        }, 100);
    }

    dismissPrompt(source) {
        sessionStorage.setItem(`prompt_${source}_dismissed`, 'true');
        const prompts = document.querySelectorAll('.conversion-prompt');
        prompts.forEach(p => {
            p.classList.remove('show');
            setTimeout(() => p.remove(), 300);
        });
    }

    handleSignup(source) {
        this.dismissPrompt(source);
        sessionStorage.setItem('signup_source', source);
        if (typeof showSignupModal === 'function') {
            showSignupModal(source);
        }
    }

    getStyles() {
        return `
            .conversion-prompt {
                position: fixed;
                bottom: -300px;
                right: 30px;
                width: 380px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
                z-index: 9998;
                transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                border: 2px solid rgba(255, 255, 255, 0.2);
            }

            .conversion-prompt.show {
                bottom: 30px;
            }

            .conversion-prompt-content {
                color: white;
                position: relative;
            }

            .conversion-prompt-close {
                position: absolute;
                top: -15px;
                right: -15px;
                background: rgba(0, 0, 0, 0.3);
                border: none;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                font-size: 1.5rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;
            }

            .conversion-prompt-close:hover {
                background: rgba(0, 0, 0, 0.5);
                transform: rotate(90deg);
            }

            .conversion-prompt-content h3 {
                font-size: 1.4rem;
                margin-bottom: 10px;
            }

            .conversion-prompt-content p {
                font-size: 0.95rem;
                line-height: 1.5;
                margin-bottom: 20px;
                opacity: 0.95;
            }

            .conversion-prompt-actions {
                display: flex;
                gap: 10px;
            }

            .conversion-btn-primary {
                flex: 1;
                padding: 12px 20px;
                background: white;
                color: #667eea;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s;
            }

            .conversion-btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 255, 255, 0.3);
            }

            .conversion-btn-secondary {
                flex: 1;
                padding: 12px 20px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 8px;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s;
            }

            .conversion-btn-secondary:hover {
                background: rgba(255, 255, 255, 0.3);
            }

            @media (max-width: 600px) {
                .conversion-prompt {
                    right: 15px;
                    left: 15px;
                    width: auto;
                    bottom: -350px;
                }

                .conversion-prompt.show {
                    bottom: 15px;
                }

                .conversion-prompt-actions {
                    flex-direction: column;
                }
            }
        `;
    }
}

// Initialize
const conversionPrompts = new ConversionPrompts();
