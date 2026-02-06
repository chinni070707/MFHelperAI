/**
 * Authentication Modals
 * Signup and Login forms for user registration
 */

class AuthModals {
    constructor() {
        this.signupModal = null;
        this.loginModal = null;
        this.init();
    }

    init() {
        const style = document.createElement('style');
        style.textContent = this.getStyles();
        document.head.appendChild(style);

        this.createSignupModal();
        this.createLoginModal();
    }

    createSignupModal() {
        const modal = document.createElement('div');
        modal.id = 'signupModal';
        modal.className = 'auth-modal';
        modal.innerHTML = `
            <div class="auth-modal-content">
                <span class="auth-modal-close" onclick="authModals.closeSignup()">&times;</span>
                <h2>Create Your Account</h2>
                <p class="auth-subtitle">Start saving and analyzing your portfolio</p>
                
                <form id="signupForm" onsubmit="authModals.handleSignup(event)">
                    <div class="form-group">
                        <label>Full Name*</label>
                        <input type="text" name="full_name" required placeholder="John Doe">
                    </div>
                    
                    <div class="form-group">
                        <label>Email*</label>
                        <input type="email" name="email" required placeholder="john@example.com">
                    </div>
                    
                    <div class="form-group">
                        <label>Phone (Optional)</label>
                        <input type="tel" name="phone" placeholder="+91 9876543210">
                    </div>
                    
                    <div class="form-group">
                        <label>Password*</label>
                        <input type="password" name="password" required placeholder="Min. 8 characters" minlength="8">
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="newsletter" checked>
                            Subscribe to investment tips and updates
                        </label>
                    </div>
                    
                    <button type="submit" class="auth-btn-primary" id="signupBtn">
                        Create Account
                    </button>
                    
                    <div class="auth-footer">
                        Already have an account? 
                        <a href="#" onclick="authModals.switchToLogin(); return false;">Login</a>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        this.signupModal = modal;
    }

    createLoginModal() {
        const modal = document.createElement('div');
        modal.id = 'loginModal';
        modal.className = 'auth-modal';
        modal.innerHTML = `
            <div class="auth-modal-content">
                <span class="auth-modal-close" onclick="authModals.closeLogin()">&times;</span>
                <h2>Welcome Back</h2>
                <p class="auth-subtitle">Login to access your portfolio</p>
                
                <form id="loginForm" onsubmit="authModals.handleLogin(event)">
                    <div class="form-group">
                        <label>Email*</label>
                        <input type="email" name="email" required placeholder="john@example.com">
                    </div>
                    
                    <div class="form-group">
                        <label>Password*</label>
                        <input type="password" name="password" required placeholder="Enter your password">
                    </div>
                    
                    <button type="submit" class="auth-btn-primary" id="loginBtn">
                        Login
                    </button>
                    
                    <div class="auth-footer">
                        Don't have an account? 
                        <a href="#" onclick="authModals.switchToSignup(); return false;">Sign Up</a>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        this.loginModal = modal;
    }

    showSignup() {
        this.signupModal.style.display = 'flex';
    }

    closeSignup() {
        this.signupModal.style.display = 'none';
    }

    showLogin() {
        this.loginModal.style.display = 'flex';
    }

    closeLogin() {
        this.loginModal.style.display = 'none';
    }

    switchToLogin() {
        this.closeSignup();
        this.showLogin();
    }

    switchToSignup() {
        this.closeLogin();
        this.showSignup();
    }

    async handleSignup(event) {
        event.preventDefault();
        
        const form = event.target;
        const btn = document.getElementById('signupBtn');
        const originalText = btn.textContent;
        
        btn.disabled = true;
        btn.textContent = 'Creating Account...';
        
        try {
            const formData = new FormData(form);
            const data = {
                email: formData.get('email'),
                password: formData.get('password'),
                full_name: formData.get('full_name'),
                phone: formData.get('phone') || null,
                source: sessionStorage.getItem('signup_source') || 'direct'
            };
            
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Signup failed');
            }
            
            // Save token
            localStorage.setItem('authToken', result.access_token);
            localStorage.setItem('portfolioMode', 'authenticated');
            
            // Migrate guest data if exists
            if (typeof portfolioStorage !== 'undefined') {
                portfolioStorage.migrateToAuthenticated(result.access_token);
            }
            
            if (typeof showToast === 'function') {
                showToast('Account created successfully!', 'success');
            }
            
            this.closeSignup();
            
            // Reload to show authenticated state
            setTimeout(() => window.location.reload(), 1000);
            
        } catch (error) {
            if (typeof showToast === 'function') {
                showToast(error.message, 'error');
            } else {
                alert(error.message);
            }
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }

    async handleLogin(event) {
        event.preventDefault();
        
        const form = event.target;
        const btn = document.getElementById('loginBtn');
        const originalText = btn.textContent;
        
        btn.disabled = true;
        btn.textContent = 'Logging in...';
        
        try {
            const formData = new FormData(form);
            const data = {
                email: formData.get('email'),
                password: formData.get('password')
            };
            
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Login failed');
            }
            
            // Save token
            localStorage.setItem('authToken', result.access_token);
            localStorage.setItem('portfolioMode', 'authenticated');
            
            if (typeof showToast === 'function') {
                showToast('Login successful!', 'success');
            }
            
            this.closeLogin();
            
            // Reload to fetch user's portfolio
            setTimeout(() => window.location.reload(), 1000);
            
        } catch (error) {
            if (typeof showToast === 'function') {
                showToast(error.message, 'error');
            } else {
                alert(error.message);
            }
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }

    getStyles() {
        return `
            .auth-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.85);
                backdrop-filter: blur(10px);
                z-index: 10001;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s;
            }

            .auth-modal-content {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 20px;
                padding: 40px;
                max-width: 450px;
                width: 90%;
                position: relative;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .auth-modal-close {
                position: absolute;
                top: 15px;
                right: 20px;
                font-size: 2rem;
                color: rgba(255, 255, 255, 0.7);
                cursor: pointer;
                transition: color 0.3s;
            }

            .auth-modal-close:hover {
                color: #fff;
            }

            .auth-modal-content h2 {
                color: #fff;
                font-size: 2rem;
                margin-bottom: 10px;
            }

            .auth-subtitle {
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 30px;
            }

            .form-group {
                margin-bottom: 20px;
            }

            .form-group label {
                display: block;
                color: rgba(255, 255, 255, 0.9);
                margin-bottom: 8px;
                font-weight: 500;
            }

            .form-group input[type="text"],
            .form-group input[type="email"],
            .form-group input[type="tel"],
            .form-group input[type="password"] {
                width: 100%;
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #fff;
                font-size: 1rem;
                transition: all 0.3s;
            }

            .form-group input:focus {
                outline: none;
                border-color: #667eea;
                background: rgba(255, 255, 255, 0.08);
            }

            .form-group input[type="checkbox"] {
                margin-right: 8px;
            }

            .auth-btn-primary {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                margin-top: 10px;
            }

            .auth-btn-primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            }

            .auth-btn-primary:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .auth-footer {
                text-align: center;
                margin-top: 25px;
                color: rgba(255, 255, 255, 0.7);
            }

            .auth-footer a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.3s;
            }

            .auth-footer a:hover {
                color: #7b8cff;
            }

            @media (max-width: 600px) {
                .auth-modal-content {
                    padding: 30px 20px;
                }

                .auth-modal-content h2 {
                    font-size: 1.5rem;
                }
            }
        `;
    }
}

// Initialize global instance
const authModals = new AuthModals();

// Make showSignupModal available globally
function showSignupModal(source = 'direct') {
    sessionStorage.setItem('signup_source', source);
    authModals.showSignup();
}

function showLoginModal() {
    authModals.showLogin();
}
