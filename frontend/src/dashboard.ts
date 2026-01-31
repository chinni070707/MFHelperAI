/**
 * Dashboard Controller - Main application logic
 */
import { api } from '@services/api';
import { toast } from '@utils/toast';
import { storage } from '@utils/storage';
import { Formatter } from '@utils/formatter';
import { chartManager } from '@components/charts';
import type { Portfolio, Holding } from '@types/portfolio';

export class DashboardController {
  private portfolio: Portfolio | null = null;
  private isLoading: boolean = false;
  private currentView: string = 'home';

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    // Make functions globally available for onclick handlers
    this.exposeGlobalFunctions();
    
    // Try to load portfolio from storage or server
    await this.loadPortfolio();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Initialize view
    this.switchView('home');
  }

  private exposeGlobalFunctions(): void {
    // Expose functions that are called from HTML onclick handlers
    (window as any).switchView = this.switchView.bind(this);
    (window as any).uploadFile = this.handleFileSelect.bind(this);
    (window as any).loadDemo = this.loadDemoData.bind(this);
    (window as any).exportData = this.exportData.bind(this);
    (window as any).clearAllData = this.clearAllData.bind(this);
  }

  public switchView(viewName: string): void {
    // Hide all views
    document.querySelectorAll('.view-content').forEach(view => {
      view.classList.remove('active');
    });
    
    // Show selected view
    const targetView = document.getElementById(`${viewName}View`);
    if (targetView) {
      targetView.classList.add('active');
    }
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
    });
    
    const activeNavItem = document.querySelector(`a[href="#${viewName}"]`);
    if (activeNavItem) {
      activeNavItem.classList.add('active');
    }
    
    this.currentView = viewName;
    
    // Load specific view data
    if (viewName === 'analyze' && this.portfolio) {
      setTimeout(() => this.renderAnalytics(), 100);
    }
  }

  private setupEventListeners(): void {
    // File upload
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
    }

    // Search input
    const searchInput = document.getElementById('searchInput') as HTMLInputElement;
    if (searchInput) {
      searchInput.addEventListener('input', (e) => this.handleSearch(e));
    }
  }

  private handleFileSelect(): void {
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }

  private handleSearch(event: Event): void {
    const input = event.target as HTMLInputElement;
    const searchTerm = input.value.toLowerCase();
    
    if (!this.portfolio?.holdings) return;
    
    const filtered = searchTerm
      ? this.portfolio.holdings.filter(h => 
          h.fund_name.toLowerCase().includes(searchTerm) ||
          h.amc.toLowerCase().includes(searchTerm) ||
          h.category.toLowerCase().includes(searchTerm)
        )
      : this.portfolio.holdings;
    
    this.renderHoldingsGrid(filtered);
  }

  async loadPortfolio(): Promise<void> {
    try {
      this.setLoading(true);
      
      // Try to get from server
      const data = await api.getPortfolio();
      
      if (data.holdings && data.holdings.length > 0) {
        this.portfolio = data;
        this.renderPortfolio();
        toast.success('Portfolio loaded successfully');
      } else {
        // Show empty state
        this.showEmptyState();
      }
    } catch (error) {
      console.error('Error loading portfolio:', error);
      // Try to load from local storage
      const cachedPortfolio = storage.get<Portfolio>('portfolio');
      if (cachedPortfolio && cachedPortfolio.holdings?.length > 0) {
        this.portfolio = cachedPortfolio;
        this.renderPortfolio();
        toast.info('Loaded cached portfolio');
      } else {
        this.showEmptyState();
      }
    } finally {
      this.setLoading(false);
    }
  }

  private async handleFileUpload(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    
    if (!file) return;

    try {
      this.setLoading(true);
      toast.info('Uploading file...');

      const data = file.name.endsWith('.pdf')
        ? await api.uploadCAS(file)
        : await api.uploadExcel(file);

      this.portfolio = data;
      
      // Save to server and local storage
      await api.savePortfolio(data);
      storage.set('portfolio', data);

      this.renderPortfolio();
      toast.success(`${data.holdings.length} funds loaded successfully`);
    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(error.message || 'Failed to upload file');
    } finally {
      this.setLoading(false);
      input.value = ''; // Reset input
    }
  }

  private async loadDemoData(): Promise<void> {
    try {
      this.setLoading(true);
      toast.info('Loading demo data...');

      const data = await api.loadDemoData();
      this.portfolio = data;

      await api.savePortfolio(data);
      storage.set('portfolio', data);

      this.renderPortfolio();
      toast.success('Demo portfolio loaded');
    } catch (error: any) {
      console.error('Demo load error:', error);
      toast.error(error.message || 'Failed to load demo data');
    } finally {
      this.setLoading(false);
    }
  }

  private renderPortfolio(): void {
    if (!this.portfolio) return;

    // Render summary cards
    this.renderSummary();

    // Render holdings
    this.renderHoldingsGrid(this.portfolio.holdings);

    // Render charts on home view
    this.renderHomeCharts();

    // Hide empty state
    this.hideEmptyState();
    
    // Update holdings count
    const countBadge = document.getElementById('holdingsCount');
    if (countBadge) {
      countBadge.textContent = this.portfolio.holdings.length.toString();
    }
  }

  private renderSummary(): void {
    if (!this.portfolio?.summary) return;

    const { summary } = this.portfolio;
    const summaryDiv = document.getElementById('portfolioSummary');
    
    if (!summaryDiv) return;

    summaryDiv.innerHTML = `
      <div class="summary-cards">
        <div class="summary-card">
          <div class="summary-label">Total Invested</div>
          <div class="summary-value">${Formatter.currency(summary.total_invested)}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Current Value</div>
          <div class="summary-value">${Formatter.currency(summary.total_current)}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Total Gain</div>
          <div class="summary-value ${summary.total_gain >= 0 ? 'text-success' : 'text-danger'}">
            ${Formatter.currency(summary.total_gain)}
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-label">Returns</div>
          <div class="summary-value ${summary.return_pct >= 0 ? 'text-success' : 'text-danger'}">
            ${Formatter.percentage(summary.return_pct)}
          </div>
        </div>
      </div>
    `;
  }

  private renderHoldingsGrid(holdings: Holding[]): void {
    const grid = document.getElementById('holdingsGrid');
    if (!grid) return;

    if (holdings.length === 0) {
      grid.innerHTML = '<div class="text-center p-6">No holdings found</div>';
      return;
    }

    grid.innerHTML = holdings.map(holding => `
      <div class="holding-card">
        <div class="holding-header">
          <div class="fund-name">${holding.fund_name}</div>
          <div class="fund-category">${holding.category}</div>
        </div>
        <div class="holding-details">
          <div class="detail-row">
            <span>AMC:</span>
            <span>${holding.amc}</span>
          </div>
          <div class="detail-row">
            <span>Invested:</span>
            <span>${Formatter.currency(holding.invested)}</span>
          </div>
          <div class="detail-row">
            <span>Current:</span>
            <span>${Formatter.currency(holding.current_value)}</span>
          </div>
          <div class="detail-row">
            <span>Gain:</span>
            <span class="${holding.current_value >= holding.invested ? 'text-success' : 'text-danger'}">
              ${Formatter.currency(holding.current_value - holding.invested)}
            </span>
          </div>
          <div class="detail-row">
            <span>Return:</span>
            <span class="${holding.current_value >= holding.invested ? 'text-success' : 'text-danger'}">
              ${Formatter.percentage(((holding.current_value - holding.invested) / holding.invested) * 100)}
            </span>
          </div>
        </div>
      </div>
    `).join('');
  }

  private async renderHomeCharts(): Promise<void> {
    if (!this.portfolio?.holdings) return;

    try {
      // Get allocation data
      const allocation = await api.calculateAllocation(this.portfolio.holdings);
      
      const allocationDiv = document.getElementById('assetAllocation');
      if (allocationDiv) {
        // Create container for charts
        allocationDiv.innerHTML = `
          <div class="card">
            <h3>Asset Allocation</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
              <div>
                <h4>By Category</h4>
                <canvas id="category-chart" height="200"></canvas>
              </div>
              <div>
                <h4>By AMC</h4>
                <canvas id="amc-chart" height="200"></canvas>
              </div>
            </div>
          </div>
        `;

        // Wait for DOM update
        await new Promise(resolve => setTimeout(resolve, 50));
        
        // Render category allocation pie chart
        const categories = Object.keys(allocation.by_category);
        const categoryValues = categories.map(cat => allocation.by_category[cat].value);
        chartManager.createPieChart('category-chart', categories, categoryValues);

        // Render AMC distribution
        const amcs = Object.keys(allocation.by_amc).slice(0, 10); // Top 10
        const amcValues = amcs.map(amc => allocation.by_amc[amc].value);
        chartManager.createBarChart('amc-chart', amcs, amcValues);
      }
    } catch (error) {
      console.error('Error rendering charts:', error);
    }
  }

  private async renderAnalytics(): Promise<void> {
    if (!this.portfolio?.holdings) return;

    try {
      const performance = await api.calculatePerformance(this.portfolio.holdings);
      
      // Render performance chart
      const perfChart = document.getElementById('performanceChart');
      if (perfChart) {
        const fundNames = performance.map(p => p.fund_name.substring(0, 20));
        const returns = performance.map(p => p.return_pct);
        
        chartManager.createBarChart('performanceChart', fundNames, returns, 'Fund Returns (%)');
      }
    } catch (error) {
      console.error('Error rendering analytics:', error);
    }
  }

  private exportData(): void {
    if (!this.portfolio) {
      toast.warning('No portfolio data to export');
      return;
    }
    
    const dataStr = JSON.stringify(this.portfolio, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'mfhelper-portfolio.json';
    link.click();
    URL.revokeObjectURL(url);
    
    toast.success('Portfolio exported!');
  }

  private clearAllData(): void {
    if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
      storage.clear();
      
      toast.success('All data cleared');
      
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    }
  }

  private showEmptyState(): void {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) emptyState.style.display = 'block';

    const dashboardContent = document.getElementById('dashboard-content');
    if (dashboardContent) dashboardContent.style.display = 'none';
  }

  private hideEmptyState(): void {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) emptyState.style.display = 'none';

    const dashboardContent = document.getElementById('dashboard-content');
    if (dashboardContent) dashboardContent.style.display = 'block';
  }

  private setLoading(loading: boolean): void {
    this.isLoading = loading;
    const loader = document.getElementById('loader');
    if (loader) {
      loader.style.display = loading ? 'flex' : 'none';
    }
  }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new DashboardController());
} else {
  new DashboardController();
}

export default DashboardController;
