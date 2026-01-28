import { authApi } from '@/lib/api';
import { LoginCredentials, SignupData, AuthResponse } from '@/lib/types';

class AuthService {
  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await authApi.login(credentials);
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Register a new user
   */
  async signup(userData: SignupData): Promise<AuthResponse> {
    try {
      const response = await authApi.signup(userData);
      return response;
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  }

  /**
   * Logout the current user
   */
  async logout(): Promise<{ success: boolean }> {
    try {
      // The actual token removal happens in the auth utility functions
      // Here we can make a server-side logout call if needed
      const response = await authApi.logout();
      return response;
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }

  /**
   * Check if the user is authenticated
   */
  isAuthenticated(): boolean {
    // This would check for a valid JWT token in local storage
    const token = localStorage.getItem('jwtToken');
    if (!token) {
      return false;
    }

    // Additional check could be done here to validate token expiration
    // For now, just check if token exists
    try {
      // Decode token to check expiration
      const parts = token.split('.');
      if (parts.length !== 3) {
        return false;
      }

      const payload = parts[1];
      const decodedPayload = atob(payload);
      const parsedPayload = JSON.parse(decodedPayload);

      const currentTime = Math.floor(Date.now() / 1000);
      return parsedPayload.exp > currentTime;
    } catch (error) {
      console.error('Error checking authentication:', error);
      return false;
    }
  }

  /**
   * Get the current user's token
   */
  getToken(): string | null {
    return localStorage.getItem('jwtToken');
  }

  /**
   * Set the user's token
   */
  setToken(token: string): void {
    localStorage.setItem('jwtToken', token);
  }

  /**
   * Remove the user's token (logout)
   */
  removeToken(): void {
    localStorage.removeItem('jwtToken');
  }

  /**
   * Get user info from token
   */
  getUserInfo(): any {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        return null;
      }

      const payload = parts[1];
      const decodedPayload = atob(payload);
      return JSON.parse(decodedPayload);
    } catch (error) {
      console.error('Error getting user info from token:', error);
      return null;
    }
  }
}

export default new AuthService();