/**
 * Type definitions for MFHelper Portfolio Data
 */

export interface Holding {
  fund_name: string;
  amc: string;
  category: string;
  style: string;
  invested: number;
  current_value: number;
  units: number;
  nav: number;
  return_1y: string;
  return_3y: string;
  alpha: string;
  folio?: string;
}

export interface PortfolioSummary {
  total_funds: number;
  total_invested: number;
  total_current: number;
  total_gain: number;
  return_pct: number;
}

export interface Portfolio {
  holdings: Holding[];
  summary: PortfolioSummary;
  source?: string;
  filename?: string;
  parsed_at?: string;
  saved_at?: string;
}

export interface AllocationData {
  by_category: Record<string, { value: number; pct: number }>;
  by_amc: Record<string, { value: number; pct: number }>;
  by_style: Record<string, { value: number; pct: number }>;
  total_value: number;
}

export interface MarketCapAllocation {
  allocation: Record<string, { value: number; pct: number }>;
  total: number;
}

export interface PerformanceMetric {
  fund_name: string;
  invested: number;
  current: number;
  gain: number;
  return_pct: number;
  return_1y: string;
  return_3y: string;
  alpha: string;
}

export interface RebalanceRequest {
  holdings: Holding[];
  target_large: number;
  target_mid: number;
  target_small: number;
  mode: 'fresh' | 'rebalance';
}

export interface RebalanceRecommendation {
  category: string;
  action: string;
  amount?: number;
  details?: string;
}

export interface RebalanceResponse {
  mode: string;
  current_allocation: Record<string, { value: number; pct: number }>;
  target_allocation: Record<string, { value: number; pct: number }>;
  recommendations: RebalanceRecommendation[];
}

export interface OverlapRequest {
  fund_names: string[];
}

export interface OverlapResponse {
  overlapping_stocks: Record<string, any>;
  overlap_percentage: number;
  total_unique_stocks: number;
  sector_overlap: Record<string, any>;
  concentration_alerts: string[];
}

export interface ToastOptions {
  type?: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  position?: 'top-right' | 'top-center' | 'bottom-right' | 'bottom-center';
}

export interface ChartConfig {
  type: string;
  data: any;
  options?: any;
}

export interface APIError {
  detail: string;
  status?: number;
}
