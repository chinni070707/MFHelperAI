/**
 * Portfolio Overlap Analysis Module
 * Visualizes stock and sector overlap between funds
 */

class OverlapAnalyzer {
    constructor() {
        this.overlapData = null;
    }

    async analyzePortfolio(fundNames) {
        const loadingId = loading.show('Analyzing portfolio overlap...');
        
        try {
            const response = await fetch('/api/holdings/portfolio-overlap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fund_names: fundNames })
            });
            
            if (!response.ok) {
                throw new Error('Failed to analyze overlap');
            }
            
            this.overlapData = await response.json();
            loading.hide(loadingId);
            
            toast.success('Overlap analysis complete!');
            this.displayResults();
            
        } catch (error) {
            loading.hide(loadingId);
            errorHandler.handleAPIError(error, { feature: 'overlap_analysis' });
        }
    }

    displayResults() {
        if (!this.overlapData) return;
        
        const container = document.getElementById('overlap-container');
        if (!container) {
            console.error('Overlap container not found');
            return;
        }
        
        const { summary, top_overlaps, alerts } = this.overlapData;
        
        let html = `
            <div class="overlap-results">
                <!-- Summary Cards -->
                <div class="overlap-summary">
                    <div class="overlap-card ${this.getOverlapClass(summary.overlap_percentage)}">
                        <div class="overlap-icon">📊</div>
                        <div class="overlap-value">${summary.overlap_percentage.toFixed(1)}%</div>
                        <div class="overlap-label">Portfolio Overlap</div>
                        <div class="overlap-desc">${this.getOverlapDescription(summary.overlap_percentage)}</div>
                    </div>
                    
                    <div class="overlap-card">
                        <div class="overlap-icon">🎯</div>
                        <div class="overlap-value">${summary.overlapping_stocks_count}</div>
                        <div class="overlap-label">Overlapping Stocks</div>
                        <div class="overlap-desc">Out of ${summary.total_stocks} unique</div>
                    </div>
                    
                    <div class="overlap-card ${summary.alerts_count > 0 ? 'warning' : ''}">
                        <div class="overlap-icon">${summary.alerts_count > 0 ? '⚠️' : '✅'}</div>
                        <div class="overlap-value">${summary.alerts_count}</div>
                        <div class="overlap-label">Concentration Alerts</div>
                        <div class="overlap-desc">${summary.alerts_count === 0 ? 'Well diversified!' : 'Review needed'}</div>
                    </div>
                </div>

                <!-- Alerts -->
                ${alerts.length > 0 ? this.renderAlerts(alerts) : ''}

                <!-- Top Overlapping Stocks -->
                <div class="overlap-section">
                    <h3>🔍 Top Overlapping Holdings</h3>
                    <div class="overlap-stocks">
                        ${top_overlaps.map(overlap => this.renderOverlapStock(overlap)).join('')}
                    </div>
                </div>

                <!-- Visualization -->
                <div class="overlap-section">
                    <h3>📈 Overlap Heatmap</h3>
                    <div id="overlap-heatmap"></div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // Render heatmap
        this.renderHeatmap(top_overlaps);
    }

    getOverlapClass(percentage) {
        if (percentage < 30) return 'good';
        if (percentage < 50) return 'moderate';
        return 'high';
    }

    getOverlapDescription(percentage) {
        if (percentage < 30) return 'Low overlap - Good diversification';
        if (percentage < 50) return 'Moderate overlap - Acceptable';
        return 'High overlap - Consider diversifying';
    }

    renderAlerts(alerts) {
        return `
            <div class="overlap-alerts">
                <h3>⚠️ Concentration Alerts</h3>
                <ul class="alert-list">
                    ${alerts.map(alert => `<li class="alert-item">${alert}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    renderOverlapStock(overlap) {
        const barWidth = (overlap.total_exposure / 30) * 100; // Max 30% exposure
        
        return `
            <div class="overlap-stock-item">
                <div class="stock-header">
                    <span class="stock-name">${overlap.stock}</span>
                    <span class="stock-badge">${overlap.appears_in} funds</span>
                    <span class="stock-exposure">${overlap.total_exposure.toFixed(1)}%</span>
                </div>
                <div class="stock-bar-container">
                    <div class="stock-bar" style="width: ${Math.min(barWidth, 100)}%"></div>
                </div>
                <div class="stock-funds">
                    ${overlap.funds.map(f => 
                        `<span class="fund-pill">${f.name}: ${f.weight.toFixed(1)}%</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }

    renderHeatmap(overlaps) {
        if (overlaps.length === 0) return;
        
        // Prepare data for Plotly heatmap
        const stocks = overlaps.map(o => o.stock);
        const fundNames = [...new Set(overlaps.flatMap(o => o.funds.map(f => f.name)))];
        
        // Create matrix
        const matrix = [];
        for (const fundName of fundNames) {
            const row = [];
            for (const overlap of overlaps) {
                const fund = overlap.funds.find(f => f.name === fundName);
                row.push(fund ? fund.weight : 0);
            }
            matrix.push(row);
        }
        
        const data = [{
            z: matrix,
            x: stocks,
            y: fundNames,
            type: 'heatmap',
            colorscale: [
                [0, '#0f172a'],
                [0.5, '#3b82f6'],
                [1, '#ef4444']
            ],
            hovertemplate: '<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
        }];
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#fff', family: 'Inter' },
            xaxis: {
                tickangle: -45,
                tickfont: { size: 10 }
            },
            yaxis: {
                tickfont: { size: 11 }
            },
            margin: { l: 150, r: 50, t: 50, b: 100 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        Plotly.newPlot('overlap-heatmap', data, layout, config);
    }
}

// Add CSS styles
const overlapStyles = document.createElement('style');
overlapStyles.textContent = `
    .overlap-results {
        padding: 20px;
    }

    .overlap-summary {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }

    .overlap-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s;
    }

    .overlap-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .overlap-card.good {
        border-color: #22c55e;
        background: rgba(34, 197, 94, 0.1);
    }

    .overlap-card.moderate {
        border-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }

    .overlap-card.high {
        border-color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }

    .overlap-card.warning {
        border-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }

    .overlap-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }

    .overlap-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00d4ff;
        margin-bottom: 8px;
    }

    .overlap-label {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .overlap-desc {
        font-size: 0.85rem;
        color: #8892b0;
    }

    .overlap-alerts {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 30px;
    }

    .overlap-alerts h3 {
        margin-bottom: 15px;
        color: #ef4444;
    }

    .alert-list {
        list-style: none;
        padding: 0;
    }

    .alert-item {
        padding: 10px;
        margin-bottom: 8px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
        font-size: 0.9rem;
    }

    .overlap-section {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
    }

    .overlap-section h3 {
        margin-bottom: 20px;
        font-size: 1.3rem;
        color: #00d4ff;
    }

    .overlap-stocks {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    .overlap-stock-item {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stock-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 10px;
    }

    .stock-name {
        font-weight: 600;
        font-size: 1.1rem;
        flex: 1;
    }

    .stock-badge {
        background: #3b82f6;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .stock-exposure {
        font-size: 1.2rem;
        font-weight: bold;
        color: #00d4ff;
    }

    .stock-bar-container {
        background: rgba(255, 255, 255, 0.05);
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 10px;
    }

    .stock-bar {
        background: linear-gradient(90deg, #3b82f6, #ef4444);
        height: 100%;
        transition: width 0.5s ease;
    }

    .stock-funds {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .fund-pill {
        background: rgba(255, 255, 255, 0.1);
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    #overlap-heatmap {
        min-height: 400px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
        padding: 10px;
    }

    @media (max-width: 768px) {
        .overlap-summary {
            grid-template-columns: 1fr;
        }

        .stock-header {
            flex-wrap: wrap;
        }

        .overlap-section {
            padding: 15px;
        }
    }
`;

document.head.appendChild(overlapStyles);

// Create global instance
window.overlapAnalyzer = new OverlapAnalyzer();
