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

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    // Try to load portfolio from storage or server
    await this.loadPortfolio();
    
    // Set up event listeners
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    // File upload
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
    }

    // Load demo data
    const demoBtn = document.getElementById('load-demo-btn');
    if (demoBtn) {
      demoBtn.addEventListener('click', () => this.loadDemoData());
    }

    // Refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.refreshPortfolio());
    }
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
      if (cachedPortfolio) {
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

  private async refreshPortfolio(): Promise<void> {
    await this.loadPortfolio();
  }

  private renderPortfolio(): void {
    if (!this.portfolio) return;

    // Render summary cards
    this.renderSummary();

    // Render holdings table
    this.renderHoldingsTable();

    // Render charts
    this.renderCharts();

    // Hide empty state
    this.hideEmptyState();
  }

  private renderSummary(): void {
    if (!this.portfolio?.summary) return;

    const { summary } = this.portfolio;

    // Update summary cards
    this.updateElement('total-funds', summary.total_funds.toString());
    this.updateElement('total-invested', Formatter.currency(summary.total_invested));
    this.updateElement('total-current', Formatter.currency(summary.total_current));
    this.updateElement('total-gain', Formatter.currency(summary.total_gain));
    
    const returnElement = document.getElementById('total-return');
    if (returnElement) {
      const { text, className } = Formatter.returnWithClass(summary.return_pct);
      returnElement.textContent = text;
      returnElement.className = className;
    }
  }

  private renderHoldingsTable(): void {
    const tbody = document.getElementById('holdings-tbody');
    if (!tbody || !this.portfolio?.holdings) return;

    tbody.innerHTML = this.portfolio.holdings.map((holding, index) => `
      <tr>
        <td>${index + 1}</td>
        <td>
          <div class="fund-name">${holding.fund_name}</div>
          <div class="fund-meta">${holding.amc} • ${holding.category}</div>
        </td>
        <td class="text-right">${Formatter.currency(holding.invested)}</td>
        <td class="text-right">${Formatter.currency(holding.current_value)}</td>
        <td class="text-right">
          <span class="${holding.current_value >= holding.invested ? 'text-success' : 'text-danger'}">
            ${Formatter.currency(holding.current_value - holding.invested)}
          </span>
        </td>
        <td class="text-right">
          <span class="${holding.current_value >= holding.invested ? 'text-success' : 'text-danger'}">
            ${Formatter.percentage(((holding.current_value - holding.invested) / holding.invested) * 100)}
          </span>
        </td>
      </tr>
    `).join('');
  }

  private async renderCharts(): Promise<void> {
    if (!this.portfolio?.holdings) return;

    try {
      // Get allocation data
      const allocation = await api.calculateAllocation(this.portfolio.holdings);
      
      // Render category allocation pie chart
      const categories = Object.keys(allocation.by_category);
      const categoryValues = categories.map(cat => allocation.by_category[cat].value);
      chartManager.createPieChart('category-chart', categories, categoryValues);

      // Render AMC distribution
      const amcs = Object.keys(allocation.by_amc);
      const amcValues = amcs.map(amc => allocation.by_amc[amc].value);
      chartManager.createBarChart('amc-chart', amcs, amcValues, 'AMC Distribution');

    } catch (error) {
      console.error('Error rendering charts:', error);
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
      loader.style.display = loading ? 'block' : 'none';
    }
  }

  private updateElement(id: string, text: string): void {
    const element = document.getElementById(id);
    if (element) element.textContent = text;
  }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new DashboardController());
} else {
  new DashboardController();
}

export default DashboardController;
