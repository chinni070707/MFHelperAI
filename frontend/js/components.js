/**
 * Fund Card Component - Professional Design
 * Inspired by Dezerv, INDmoney, Kuvera
 */

class FundCard {
    constructor(fund) {
        this.fund = fund;
    }

    getReturnClass(value) {
        if (value > 0) return 'positive';
        if (value < 0) return 'negative';
        return 'neutral';
    }

    formatCurrency(value) {
        if (value >= 10000000) {
            return `₹${(value / 10000000).toFixed(2)}Cr`;
        } else if (value >= 100000) {
            return `₹${(value / 100000).toFixed(2)}L`;
        } else if (value >= 1000) {
            return `₹${(value / 1000).toFixed(1)}K`;
        }
        return `₹${value.toFixed(0)}`;
    }

    formatPercentage(value) {
        const sign = value > 0 ? '+' : '';
        return `${sign}${value.toFixed(2)}%`;
    }

    getAMCLogo(amc) {
        // Placeholder - can be replaced with actual AMC logos
        const amcColors = {
            'HDFC': '#004C8F',
            'ICICI': '#F37021',
            'SBI': '#0F4C8C',
            'Axis': '#800020',
            'Parag Parikh': '#1E88E5',
            'Mirae': '#D32F2F',
            'Motilal': '#1976D2',
            'Kotak': '#ED1C24',
            'Nippon': '#E31E24',
            'Quant': '#2E7D32'
        };
        
        const color = amcColors[amc] || '#3B82F6';
        const initial = amc.charAt(0);
        
        return `<div class="fund-logo" style="background: ${color}">${initial}</div>`;
    }

    getCategoryBadge(category) {
        const categoryColors = {
            'Large Cap': 'primary',
            'Mid Cap': 'warning',
            'Small Cap': 'danger',
            'Flexi Cap': 'success',
            'Multi Cap': 'success',
            'ELSS': 'primary'
        };
        
        const badgeClass = categoryColors[category] || 'primary';
        return `<span class="badge badge-${badgeClass}">${category}</span>`;
    }

    render() {
        const { fund_name, amc, category, current_value, invested_value, absolute_return, percentage_return } = this.fund;
        
        const gain = current_value - invested_value;
        const gainClass = this.getReturnClass(gain);
        const returnIcon = gain >= 0 ? '↗' : '↘';
        const progressPercentage = Math.min((current_value / invested_value) * 100, 100);
        
        return `
            <div class="fund-card" data-fund="${fund_name}">
                <div class="fund-card-header">
                    ${this.getAMCLogo(amc)}
                    <div class="fund-details">
                        <h3 class="fund-name">${fund_name}</h3>
                        <div class="fund-meta">
                            ${this.getCategoryBadge(category)}
                            <span class="fund-amc">${amc}</span>
                        </div>
                    </div>
                    <div class="fund-return ${gainClass}">
                        <span class="return-icon">${returnIcon}</span>
                        <span class="return-value">${this.formatPercentage(percentage_return)}</span>
                    </div>
                </div>
                
                <div class="fund-card-body">
                    <div class="value-grid">
                        <div class="value-item">
                            <span class="label">Current Value</span>
                            <span class="value">${this.formatCurrency(current_value)}</span>
                        </div>
                        <div class="value-item">
                            <span class="label">Invested</span>
                            <span class="value">${this.formatCurrency(invested_value)}</span>
                        </div>
                    </div>
                    
                    <div class="progress-container">
                        <div class="progress">
                            <div class="progress-fill ${gainClass}" style="width: ${progressPercentage}%"></div>
                        </div>
                        <span class="progress-label">${progressPercentage.toFixed(0)}%</span>
                    </div>
                    
                    <div class="gain-row">
                        <span class="gain-label">Total Gain/Loss</span>
                        <span class="gain-value ${gainClass}">
                            ${this.formatCurrency(Math.abs(gain))} (${this.formatPercentage(percentage_return)})
                        </span>
                    </div>
                </div>
                
                <div class="fund-card-footer">
                    <button class="btn btn-secondary btn-sm" onclick="viewFundDetails('${fund_name}')">
                        View Details
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="investMore('${fund_name}')">
                        Invest More
                    </button>
                </div>
            </div>
        `;
    }
}

// Portfolio Summary Card
class PortfolioSummary {
    constructor(data) {
        this.data = data;
    }

    render() {
        const { total_value, invested_value, total_return, percentage_return, day_change, day_change_percent } = this.data;
        
        const gainClass = total_return >= 0 ? 'positive' : 'negative';
        const dayChangeClass = day_change >= 0 ? 'positive' : 'negative';
        const dayChangeIcon = day_change >= 0 ? '↗' : '↘';
        
        return `
            <div class="portfolio-hero">
                <div class="portfolio-value-card card">
                    <p class="label text-secondary text-sm">Total Portfolio Value</p>
                    <h1 class="portfolio-value">${this.formatCurrency(total_value)}</h1>
                    <div class="day-change ${dayChangeClass}">
                        <span class="change-icon">${dayChangeIcon}</span>
                        <span>${this.formatCurrency(Math.abs(day_change))} (${this.formatPercentage(day_change_percent)}) today</span>
                    </div>
                    <div class="mini-sparkline">
                        <canvas id="miniSparkline"></canvas>
                    </div>
                </div>
                
                <div class="quick-stats">
                    <div class="stat-card card">
                        <div class="stat-icon">💰</div>
                        <p class="stat-label">Invested</p>
                        <p class="stat-value">${this.formatCurrency(invested_value)}</p>
                    </div>
                    <div class="stat-card card">
                        <div class="stat-icon ${gainClass}">📈</div>
                        <p class="stat-label">Returns</p>
                        <p class="stat-value ${gainClass}">${this.formatCurrency(Math.abs(total_return))}</p>
                        <p class="stat-percentage ${gainClass}">${this.formatPercentage(percentage_return)}</p>
                    </div>
                    <div class="stat-card card">
                        <div class="stat-icon">🎯</div>
                        <p class="stat-label">XIRR</p>
                        <p class="stat-value">18.5%</p>
                        <p class="stat-note text-xs text-tertiary">Annualized</p>
                    </div>
                </div>
            </div>
        `;
    }

    formatCurrency(value) {
        if (value >= 10000000) {
            return `₹${(value / 10000000).toFixed(2)}Cr`;
        } else if (value >= 100000) {
            return `₹${(value / 100000).toFixed(2)}L`;
        } else if (value >= 1000) {
            return `₹${(value / 1000).toFixed(1)}K`;
        }
        return `₹${value.toFixed(0)}`;
    }

    formatPercentage(value) {
        const sign = value > 0 ? '+' : '';
        return `${sign}${value.toFixed(2)}%`;
    }
}

// Asset Allocation Component
class AssetAllocation {
    constructor(data) {
        this.data = data;
    }

    render() {
        return `
            <section class="asset-allocation-section">
                <div class="section-header">
                    <h2>Asset Allocation</h2>
                    <button class="btn btn-secondary btn-sm" onclick="rebalancePortfolio()">
                        Rebalance
                    </button>
                </div>
                
                <div class="allocation-container card">
                    <div class="allocation-chart">
                        <canvas id="allocationDonut"></canvas>
                        <div class="chart-center-label">
                            <p class="text-3xl font-bold">${this.data.total_funds}</p>
                            <p class="text-sm text-secondary">Funds</p>
                        </div>
                    </div>
                    
                    <div class="allocation-legend">
                        ${this.renderLegend()}
                    </div>
                </div>
                
                <div class="allocation-insights">
                    ${this.renderInsights()}
                </div>
            </section>
        `;
    }

    renderLegend() {
        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
        
        return this.data.categories.map((cat, index) => `
            <div class="legend-item">
                <span class="legend-dot" style="background: ${colors[index]}"></span>
                <span class="legend-name">${cat.name}</span>
                <span class="legend-value">${cat.percentage}%</span>
                <span class="legend-amount text-secondary">${this.formatCurrency(cat.amount)}</span>
            </div>
        `).join('');
    }

    renderInsights() {
        return `
            <div class="insight-cards">
                <div class="insight-card card-compact">
                    <div class="insight-icon">⚖️</div>
                    <div class="insight-content">
                        <p class="insight-title">Well Balanced</p>
                        <p class="insight-desc text-sm text-secondary">Your portfolio has good diversification</p>
                    </div>
                </div>
            </div>
        `;
    }

    formatCurrency(value) {
        if (value >= 100000) {
            return `₹${(value / 100000).toFixed(1)}L`;
        }
        return `₹${(value / 1000).toFixed(0)}K`;
    }
}

// Export for use
window.FundCard = FundCard;
window.PortfolioSummary = PortfolioSummary;
window.AssetAllocation = AssetAllocation;

// ===========================================
// SKELETON LOADING COMPONENTS
// ===========================================

class SkeletonLoader {
    
    // Portfolio Summary Skeleton
    static portfolioSummary() {
        return `
            <div class="skeleton-portfolio-hero">
                <div class="skeleton skeleton-text short" style="margin: 0 auto var(--space-2);"></div>
                <div class="skeleton skeleton-text large" style="width: 200px; margin: 0 auto var(--space-3);"></div>
                <div class="skeleton skeleton-text" style="width: 150px; margin: 0 auto;"></div>
            </div>
            
            <div class="quick-stats" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4);">
                ${SkeletonLoader.statCard()}
                ${SkeletonLoader.statCard()}
                ${SkeletonLoader.statCard()}
            </div>
        `;
    }
    
    // Stat Card Skeleton
    static statCard() {
        return `
            <div class="skeleton-stat-card card">
                <div class="skeleton skeleton-circle" style="width: 40px; height: 40px; margin: 0 auto var(--space-2);"></div>
                <div class="skeleton skeleton-text small" style="width: 60%; margin: 0 auto var(--space-2);"></div>
                <div class="skeleton skeleton-text medium" style="width: 80%; margin: 0 auto;"></div>
            </div>
        `;
    }
    
    // Fund Card Skeleton
    static fundCard() {
        return `
            <div class="skeleton-card">
                <div class="skeleton-fund-card">
                    <div class="skeleton-fund-header">
                        <div class="skeleton skeleton-circle"></div>
                        <div style="flex: 1;">
                            <div class="skeleton skeleton-text" style="width: 80%;"></div>
                            <div class="skeleton skeleton-text small short"></div>
                        </div>
                        <div class="skeleton skeleton-text" style="width: 60px;"></div>
                    </div>
                    <div class="skeleton-fund-body">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4);">
                            <div>
                                <div class="skeleton skeleton-text small short"></div>
                                <div class="skeleton skeleton-text medium"></div>
                            </div>
                            <div>
                                <div class="skeleton skeleton-text small short"></div>
                                <div class="skeleton skeleton-text medium"></div>
                            </div>
                        </div>
                        <div class="skeleton skeleton-progress"></div>
                        <div style="display: flex; justify-content: space-between;">
                            <div class="skeleton skeleton-text short"></div>
                            <div class="skeleton skeleton-text shorter"></div>
                        </div>
                    </div>
                    <div class="skeleton-fund-footer">
                        <div class="skeleton skeleton-btn"></div>
                        <div class="skeleton skeleton-btn"></div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Multiple Fund Cards Skeleton
    static fundCards(count = 3) {
        return Array(count).fill(SkeletonLoader.fundCard()).join('');
    }
    
    // Asset Allocation Skeleton
    static assetAllocation() {
        return `
            <section class="asset-allocation-section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4);">
                    <div class="skeleton skeleton-text" style="width: 150px;"></div>
                    <div class="skeleton skeleton-btn" style="width: 100px;"></div>
                </div>
                
                <div class="card" style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-6); padding: var(--space-6);">
                    <div style="display: flex; justify-content: center; align-items: center;">
                        <div class="skeleton skeleton-donut"></div>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: var(--space-3);">
                        ${SkeletonLoader.legendItem()}
                        ${SkeletonLoader.legendItem()}
                        ${SkeletonLoader.legendItem()}
                        ${SkeletonLoader.legendItem()}
                    </div>
                </div>
            </section>
        `;
    }
    
    // Legend Item Skeleton
    static legendItem() {
        return `
            <div style="display: flex; align-items: center; gap: var(--space-3);">
                <div class="skeleton" style="width: 12px; height: 12px; border-radius: 50%;"></div>
                <div class="skeleton skeleton-text" style="flex: 1;"></div>
                <div class="skeleton skeleton-text" style="width: 50px;"></div>
            </div>
        `;
    }
    
    // Quick Actions Skeleton
    static quickActions() {
        return `
            <section class="quick-actions mb-6">
                <div class="grid grid-cols-3 gap-4">
                    <div class="card card-compact" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px;">
                        <div class="skeleton" style="width: 40px; height: 40px; border-radius: 8px; margin-bottom: var(--space-2);"></div>
                        <div class="skeleton skeleton-text small" style="width: 60px;"></div>
                    </div>
                    <div class="card card-compact" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px;">
                        <div class="skeleton" style="width: 40px; height: 40px; border-radius: 8px; margin-bottom: var(--space-2);"></div>
                        <div class="skeleton skeleton-text small" style="width: 60px;"></div>
                    </div>
                    <div class="card card-compact" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px;">
                        <div class="skeleton" style="width: 40px; height: 40px; border-radius: 8px; margin-bottom: var(--space-2);"></div>
                        <div class="skeleton skeleton-text small" style="width: 60px;"></div>
                    </div>
                </div>
            </section>
        `;
    }
    
    // Full Home View Skeleton
    static homeView() {
        return `
            ${SkeletonLoader.portfolioSummary()}
            ${SkeletonLoader.assetAllocation()}
            ${SkeletonLoader.quickActions()}
        `;
    }
    
    // Full Portfolio View Skeleton
    static portfolioView() {
        return `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-5);">
                <div class="skeleton skeleton-text" style="width: 120px;"></div>
                <div style="display: flex; gap: var(--space-2);">
                    <div class="skeleton skeleton-btn" style="width: 120px;"></div>
                    <div class="skeleton skeleton-btn" style="width: 120px;"></div>
                </div>
            </div>
            ${SkeletonLoader.fundCards(4)}
        `;
    }
}

// Export skeleton loader
window.SkeletonLoader = SkeletonLoader;
