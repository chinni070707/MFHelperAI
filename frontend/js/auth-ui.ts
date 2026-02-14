/**
 * Authentication UI Components
 */

import { authService, LoginCredentials, RegisterData } from './services/auth.js';
import { showToast } from './toast.js';

export class AuthUI {
  /**
   * Show login modal
   */
  showLoginModal(): void {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-container">
        <div class="modal-header">
          <h2>Login to MFHelper</h2>
          <button class="btn-close" onclick="this.closest('.modal-overlay').remove()">×</button>
        </div>
        <form id="loginForm" class="modal-body">
          <div class="form-group">
            <label for="loginEmail">Email</label>
            <input 
              type="email" 
              id="loginEmail" 
              class="form-control" 
              required 
              placeholder="your@email.com"
            />
          </div>
          <div class="form-group">
            <label for="loginPassword">Password</label>
            <input 
              type="password" 
              id="loginPassword" 
              class="form-control" 
              required 
              minlength="8"
              placeholder="Enter your password"
            />
          </div>
          <button type="submit" class="btn-primary btn-full">Login</button>
          <p class="text-center mt-3">
            Don't have an account? 
            <a href="#" onclick="authUI.showRegisterModal(); this.closest('.modal-overlay').remove();">
              Register here
            </a>
          </p>
        </form>
      </div>
    `;

    document.body.appendChild(modal);

    const form = document.getElementById('loginForm') as HTMLFormElement;
    form.addEventListener('submit', (e) => this.handleLogin(e, modal));
  }

  /**
   * Show registration modal
   */
  showRegisterModal(): void {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-container">
        <div class="modal-header">
          <h2>Create Account</h2>
          <button class="btn-close" onclick="this.closest('.modal-overlay').remove()">×</button>
        </div>
        <form id="registerForm" class="modal-body">
          <div class="form-group">
            <label for="regEmail">Email *</label>
            <input 
              type="email" 
              id="regEmail" 
              class="form-control" 
              required 
              placeholder="your@email.com"
            />
          </div>
          <div class="form-group">
            <label for="regPassword">Password *</label>
            <input 
              type="password" 
              id="regPassword" 
              class="form-control" 
              required 
              minlength="8"
              placeholder="Min 8 chars, 1 uppercase, 1 digit"
            />
          </div>
          <div class="form-group">
            <label for="regFullName">Full Name</label>
            <input 
              type="text" 
              id="regFullName" 
              class="form-control" 
              placeholder="John Doe"
            />
          </div>
          <div class="form-group">
            <label for="regPAN">PAN</label>
            <input 
              type="text" 
              id="regPAN" 
              class="form-control" 
              maxlength="10"
              placeholder="ABCDE1234F"
              pattern="[A-Z]{5}[0-9]{4}[A-Z]{1}"
            />
          </div>
          <div class="form-group">
            <label for="regPhone">Phone</label>
            <input 
              type="tel" 
              id="regPhone" 
              class="form-control" 
              placeholder="+91 98765 43210"
            />
          </div>
          <button type="submit" class="btn-primary btn-full">Create Account</button>
          <p class="text-center mt-3">
            Already have an account? 
            <a href="#" onclick="authUI.showLoginModal(); this.closest('.modal-overlay').remove();">
              Login here
            </a>
          </p>
        </form>
      </div>
    `;

    document.body.appendChild(modal);

    const form = document.getElementById('registerForm') as HTMLFormElement;
    form.addEventListener('submit', (e) => this.handleRegister(e, modal));
  }

  /**
   * Show user settings modal
   */
  async showSettingsModal(): Promise<void> {
    try {
      const settings = await authService.getSettings();
      const user = authService.getStoredUser();

      const modal = document.createElement('div');
      modal.className = 'modal-overlay';
      modal.innerHTML = `
        <div class="modal-container modal-large">
          <div class="modal-header">
            <h2>Settings</h2>
            <button class="btn-close" onclick="this.closest('.modal-overlay').remove()">×</button>
          </div>
          <div class="modal-body">
            <div class="settings-tabs">
              <button class="tab-btn active" data-tab="profile">Profile</button>
              <button class="tab-btn" data-tab="preferences">Preferences</button>
              <button class="tab-btn" data-tab="notifications">Notifications</button>
            </div>

            <!-- Profile Tab -->
            <div class="tab-content active" id="profile">
              <form id="profileForm">
                <div class="form-group">
                  <label>Email</label>
                  <input type="email" class="form-control" value="${user?.email}" disabled />
                </div>
                <div class="form-group">
                  <label for="profileFullName">Full Name</label>
                  <input 
                    type="text" 
                    id="profileFullName" 
                    class="form-control" 
                    value="${user?.full_name || ''}"
                  />
                </div>
                <div class="form-group">
                  <label for="profilePhone">Phone</label>
                  <input 
                    type="tel" 
                    id="profilePhone" 
                    class="form-control" 
                    value="${user?.phone || ''}"
                  />
                </div>
                <button type="submit" class="btn-primary">Update Profile</button>
              </form>
            </div>

            <!-- Preferences Tab -->
            <div class="tab-content" id="preferences">
              <form id="preferencesForm">
                <div class="form-group">
                  <label for="theme">Theme</label>
                  <select id="theme" class="form-control">
                    <option value="light" ${settings.theme === 'light' ? 'selected' : ''}>Light</option>
                    <option value="dark" ${settings.theme === 'dark' ? 'selected' : ''}>Dark</option>
                    <option value="auto" ${settings.theme === 'auto' ? 'selected' : ''}>Auto</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="currency">Currency</label>
                  <select id="currency" class="form-control">
                    <option value="INR" ${settings.currency === 'INR' ? 'selected' : ''}>INR (₹)</option>
                    <option value="USD" ${settings.currency === 'USD' ? 'selected' : ''}>USD ($)</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="defaultView">Default View</label>
                  <select id="defaultView" class="form-control">
                    <option value="summary" ${settings.default_view === 'summary' ? 'selected' : ''}>Summary</option>
                    <option value="detailed" ${settings.default_view === 'detailed' ? 'selected' : ''}>Detailed</option>
                    <option value="charts" ${settings.default_view === 'charts' ? 'selected' : ''}>Charts</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>
                    <input type="checkbox" id="showXirr" ${settings.show_xirr ? 'checked' : ''} />
                    Show XIRR calculations
                  </label>
                </div>
                <button type="submit" class="btn-primary">Save Preferences</button>
              </form>
            </div>

            <!-- Notifications Tab -->
            <div class="tab-content" id="notifications">
              <form id="notificationsForm">
                <div class="form-group">
                  <label>
                    <input type="checkbox" id="emailNotifications" ${settings.email_notifications ? 'checked' : ''} />
                    Email notifications
                  </label>
                </div>
                <div class="form-group">
                  <label>
                    <input type="checkbox" id="portfolioAlerts" ${settings.portfolio_alerts ? 'checked' : ''} />
                    Portfolio alerts
                  </label>
                </div>
                <div class="form-group">
                  <label>
                    <input type="checkbox" id="marketUpdates" ${settings.market_updates ? 'checked' : ''} />
                    Market updates
                  </label>
                </div>
                <button type="submit" class="btn-primary">Save Notifications</button>
              </form>
            </div>
          </div>
        </div>
      `;

      document.body.appendChild(modal);

      // Tab switching
      modal.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const tab = btn.getAttribute('data-tab');
          modal.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
          modal.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
          btn.classList.add('active');
          modal.querySelector(`#${tab}`)?.classList.add('active');
        });
      });

      // Form handlers
      this.setupSettingsForms(modal);

    } catch (error) {
      console.error('Failed to load settings:', error);
      showToast('Failed to load settings', 'error');
    }
  }

  /**
   * Handle login form submission
   */
  private async handleLogin(e: Event, modal: HTMLElement): Promise<void> {
    e.preventDefault();

    const email = (document.getElementById('loginEmail') as HTMLInputElement).value;
    const password = (document.getElementById('loginPassword') as HTMLInputElement).value;

    try {
      const credentials: LoginCredentials = { email, password };
      await authService.login(credentials);
      
      showToast('Login successful!', 'success');
      modal.remove();
      
      // Reload page to update UI
      window.location.reload();
    } catch (error: any) {
      showToast(error.message || 'Login failed', 'error');
    }
  }

  /**
   * Handle registration form submission
   */
  private async handleRegister(e: Event, modal: HTMLElement): Promise<void> {
    e.preventDefault();

    const data: RegisterData = {
      email: (document.getElementById('regEmail') as HTMLInputElement).value,
      password: (document.getElementById('regPassword') as HTMLInputElement).value,
      full_name: (document.getElementById('regFullName') as HTMLInputElement).value || undefined,
      pan: (document.getElementById('regPAN') as HTMLInputElement).value || undefined,
      phone: (document.getElementById('regPhone') as HTMLInputElement).value || undefined,
    };

    try {
      const response = await authService.register(data);
      
      modal.remove();
      
      // Show appropriate message based on email verification
      if (response.email_verification_sent) {
        showToast('Registration successful! Please check your email to verify your account.', 'success', 5000);
      } else {
        showToast('Registration successful!', 'success');
      }
      
      // Reload page to update UI
      window.location.reload();
    } catch (error: any) {
      showToast(error.message || 'Registration failed', 'error');
    }
  }

  /**
   * Setup settings form handlers
   */
  private setupSettingsForms(modal: HTMLElement): void {
    // Profile form
    modal.querySelector('#profileForm')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await authService.updateProfile({
          full_name: (document.getElementById('profileFullName') as HTMLInputElement).value,
          phone: (document.getElementById('profilePhone') as HTMLInputElement).value,
        });
        showToast('Profile updated!', 'success');
      } catch (error: any) {
        showToast(error.message, 'error');
      }
    });

    // Preferences form
    modal.querySelector('#preferencesForm')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const theme = (document.getElementById('theme') as HTMLSelectElement).value as 'light' | 'dark' | 'auto';
        await authService.updateSettings({
          theme,
          currency: (document.getElementById('currency') as HTMLSelectElement).value,
          default_view: (document.getElementById('defaultView') as HTMLSelectElement).value,
          show_xirr: (document.getElementById('showXirr') as HTMLInputElement).checked,
        });
        showToast('Preferences saved!', 'success');
        
        // Apply theme immediately
        this.applyTheme(theme);
      } catch (error: any) {
        showToast(error.message, 'error');
      }
    });

    // Notifications form
    modal.querySelector('#notificationsForm')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        await authService.updateSettings({
          email_notifications: (document.getElementById('emailNotifications') as HTMLInputElement).checked,
          portfolio_alerts: (document.getElementById('portfolioAlerts') as HTMLInputElement).checked,
          market_updates: (document.getElementById('marketUpdates') as HTMLInputElement).checked,
        });
        showToast('Notification settings saved!', 'success');
      } catch (error: any) {
        showToast(error.message, 'error');
      }
    });
  }

  /**
   * Apply theme to document
   */
  applyTheme(theme: 'light' | 'dark' | 'auto'): void {
    if (theme === 'auto') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      theme = isDark ? 'dark' : 'light';
    }
    
    document.documentElement.setAttribute('data-theme', theme);
  }

  /**
   * Initialize auth UI on page load
   */
  async init(): Promise<void> {
    // Check if user is authenticated
    if (authService.isAuthenticated()) {
      try {
        const user = await authService.getCurrentUser();
        this.updateUIForAuthenticatedUser(user);
        
        // Load and apply user theme
        const settings = await authService.getSettings();
        this.applyTheme(settings.theme);
      } catch (error) {
        console.error('Failed to load user:', error);
        authService.logout();
      }
    }
  }

  /**
   * Update UI for authenticated user
   */
  private updateUIForAuthenticatedUser(user: any): void {
    // Update any "Login" buttons to show user menu
    const loginBtns = document.querySelectorAll('.btn-login');
    loginBtns.forEach(btn => {
      btn.textContent = user.full_name || user.email;
      btn.addEventListener('click', () => this.showUserMenu());
    });
  }

  /**
   * Show user menu dropdown
   */
  private showUserMenu(): void {
    // This would show a dropdown menu with Profile, Settings, Logout options
    // Implementation depends on your UI framework
  }
}

export const authUI = new AuthUI();

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => authUI.init());
} else {
  authUI.init();
}
