/**
 * Authentication Service - Handle user auth with backend API
 */

export interface User {
  id: number;
  email: string;
  full_name?: string;
  pan?: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
  pan?: string;
  phone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserSettings {
  id: number;
  user_id: number;
  theme: 'light' | 'dark' | 'auto';
  language: string;
  currency: string;
  date_format: string;
  email_notifications: boolean;
  portfolio_alerts: boolean;
  market_updates: boolean;
  default_view: string;
  show_xirr: boolean;
  group_by: string;
  created_at: string;
  updated_at: string;
}

class AuthService {
  private baseUrl: string = '/api/auth';
  private tokenKey: string = 'mfhelper_token';
  private userKey: string = 'mfhelper_user';

  /**
   * Register a new user
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const authData: AuthResponse = await response.json();
    this.setAuth(authData);
    return authData;
  }

  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const authData: AuthResponse = await response.json();
    this.setAuth(authData);
    return authData;
  }

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    window.location.href = '/';
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.authenticatedFetch(`${this.baseUrl}/me`);
    
    if (!response.ok) {
      throw new Error('Failed to get user info');
    }

    const user: User = await response.json();
    localStorage.setItem(this.userKey, JSON.stringify(user));
    return user;
  }

  /**
   * Update user profile
   */
  async updateProfile(data: { full_name?: string; phone?: string }): Promise<User> {
    const params = new URLSearchParams();
    if (data.full_name) params.append('full_name', data.full_name);
    if (data.phone) params.append('phone', data.phone);

    const response = await this.authenticatedFetch(
      `${this.baseUrl}/me?${params.toString()}`,
      { method: 'PUT' }
    );

    if (!response.ok) {
      throw new Error('Failed to update profile');
    }

    const user: User = await response.json();
    localStorage.setItem(this.userKey, JSON.stringify(user));
    return user;
  }

  /**
   * Get user settings
   */
  async getSettings(): Promise<UserSettings> {
    const response = await this.authenticatedFetch(`${this.baseUrl}/settings`);
    
    if (!response.ok) {
      throw new Error('Failed to get settings');
    }

    return await response.json();
  }

  /**
   * Update user settings
   */
  async updateSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await this.authenticatedFetch(`${this.baseUrl}/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      throw new Error('Failed to update settings');
    }

    return await response.json();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Get stored token
   */
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Get stored user
   */
  getStoredUser(): User | null {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Set authentication data
   */
  private setAuth(authData: AuthResponse): void {
    localStorage.setItem(this.tokenKey, authData.access_token);
    localStorage.setItem(this.userKey, JSON.stringify(authData.user));
  }

  /**
   * Make authenticated fetch request
   */
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }

    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    };

    const response = await fetch(url, { ...options, headers });

    // If unauthorized, clear auth and redirect to login
    if (response.status === 401) {
      this.logout();
    }

    return response;
  }
}

export const authService = new AuthService();
