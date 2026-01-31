/**
 * API Service - Centralized API communication
 */
import type { 
  Portfolio, 
  AllocationData, 
  MarketCapAllocation, 
  PerformanceMetric,
  RebalanceRequest,
  RebalanceResponse,
  OverlapRequest,
  OverlapResponse,
  APIError 
} from '@types/portfolio';

const API_BASE = '/api';

class APIService {
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: APIError = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`
      }));
      throw new Error(error.detail || 'API request failed');
    }
    return response.json();
  }

  // Portfolio APIs
  async getPortfolio(userId: string = 'default'): Promise<Portfolio> {
    const response = await fetch(`${API_BASE}/portfolio/?user_id=${userId}`);
    return this.handleResponse<Portfolio>(response);
  }

  async savePortfolio(data: Portfolio, userId: string = 'default'): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/portfolio/save?user_id=${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async deletePortfolio(userId: string = 'default'): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/portfolio/?user_id=${userId}`, {
      method: 'DELETE'
    });
    return this.handleResponse(response);
  }

  // Upload APIs
  async uploadExcel(file: File): Promise<Portfolio> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload/excel`, {
      method: 'POST',
      body: formData
    });
    return this.handleResponse<Portfolio>(response);
  }

  async uploadCAS(file: File, password?: string): Promise<Portfolio> {
    const formData = new FormData();
    formData.append('file', file);
    if (password) {
      formData.append('password', password);
    }

    const response = await fetch(`${API_BASE}/upload/cas`, {
      method: 'POST',
      body: formData
    });
    return this.handleResponse<Portfolio>(response);
  }

  async loadDemoData(): Promise<Portfolio> {
    const response = await fetch(`${API_BASE}/upload/demo`);
    return this.handleResponse<Portfolio>(response);
  }

  // Analytics APIs
  async calculateAllocation(holdings: any[]): Promise<AllocationData> {
    const response = await fetch(`${API_BASE}/analytics/allocation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(holdings)
    });
    return this.handleResponse<AllocationData>(response);
  }

  async calculateMarketCap(holdings: any[]): Promise<MarketCapAllocation> {
    const response = await fetch(`${API_BASE}/analytics/market-cap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(holdings)
    });
    return this.handleResponse<MarketCapAllocation>(response);
  }

  async calculatePerformance(holdings: any[]): Promise<PerformanceMetric[]> {
    const response = await fetch(`${API_BASE}/analytics/performance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(holdings)
    });
    return this.handleResponse<PerformanceMetric[]>(response);
  }

  // Rebalance API
  async calculateRebalance(request: RebalanceRequest): Promise<RebalanceResponse> {
    const response = await fetch(`${API_BASE}/rebalance/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return this.handleResponse<RebalanceResponse>(response);
  }

  // Holdings & Overlap APIs
  async getFundsList(): Promise<any> {
    const response = await fetch(`${API_BASE}/holdings/`);
    return this.handleResponse(response);
  }

  async calculateOverlap(request: OverlapRequest): Promise<OverlapResponse> {
    const response = await fetch(`${API_BASE}/holdings/overlap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return this.handleResponse<OverlapResponse>(response);
  }
}

export const api = new APIService();
export default api;
