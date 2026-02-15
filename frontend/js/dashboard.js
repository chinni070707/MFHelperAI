/**
 * Dashboard JavaScript - Extracted from inline JS for performance
 */

// HTML escape helper to prevent XSS when rendering user data
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

// Chart accessibility helper (#35) \u2014 add ARIA labels to Plotly chart containers
function setChartA11y(chartId, description) {
    const el = document.getElementById(chartId);
    if (el) {
        el.setAttribute('role', 'img');
        el.setAttribute('aria-label', description);
    }
}

// Mobile Menu Toggle
function toggleMenu() {
    const menu = document.querySelector('.nav-menu');
    menu.classList.toggle('active');
}

// Navbar Scroll Effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

let portfolioData = null;
let currentMode = 'rebalance';
let marketCapAllocation = { large: 0, mid: 0, small: 0, other: 0 };

// Check email verification status
async function checkVerificationStatus() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    try {
        const response = await fetch('/api/auth/verification-status', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const banner = document.getElementById('verificationBanner');
            
            // Only show banner if:
            // 1. User is not verified AND
            // 2. Email service is configured (so they can actually verify)
            if (!data.is_verified && data.email_service_configured && banner) {
                banner.style.display = 'flex';
            }
        }
    } catch (error) {
        console.log('Verification status check failed (normal for OAuth users)');
    }
}

// Resend verification email
async function resendVerificationEmail() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    const btn = document.getElementById('resendVerifyBtn');
    const originalText = btn.textContent;
    btn.textContent = 'Sending...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/auth/resend-verification', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.showToast?.('Verification email sent! Check your inbox.', 'success');
            btn.textContent = 'Email Sent ✓';
            // Hide banner after a moment
            setTimeout(() => {
                document.getElementById('verificationBanner').style.display = 'none';
            }, 3000);
        } else if (data.already_verified) {
            window.showToast?.('Your email is already verified!', 'success');
            document.getElementById('verificationBanner').style.display = 'none';
        } else {
            window.showToast?.(data.detail || 'Failed to send. Please try again.', 'error');
            btn.textContent = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Resend verification error:', error);
        window.showToast?.('Network error. Please try again.', 'error');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    // Check email verification status for authenticated users
    await checkVerificationStatus();
    
    // Check for demo mode in URL
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode');
    
    if (mode === 'demo') {
        // Load demo portfolio from API
        await loadDemoPortfolio();
    } else {
        // Check if user is authenticated
        const token = localStorage.getItem('authToken');
        
        if (token) {
            // Try to load from database first for authenticated users
            const loadedFromDB = await loadPortfolioFromDatabase();
            if (loadedFromDB) {
                return; // Successfully loaded from database
            }
        }
        
        // Fallback: Try to load from portfolio storage
        const portfolioStorage = new PortfolioStorage();
        const storedData = portfolioStorage.load();
        
        if (storedData && storedData.holdings && storedData.holdings.length > 0) {
            portfolioData = storedData;
            renderDashboard();
        } else {
            // Fallback to old localStorage
            const stored = localStorage.getItem('portfolioData');
            if (stored) {
                portfolioData = JSON.parse(stored);
                renderDashboard();
            } else {
                document.getElementById('dashboardContent').style.display = 'none';
                document.getElementById('noData').style.display = 'block';
            }
        }
    }
});

async function loadDemoPortfolio() {
    try {
        const response = await fetch('/api/demo/portfolio');
        if (!response.ok) {
            throw new Error('Failed to load demo portfolio');
        }
        
        const data = await response.json();
        if (data.success && data.holdings && data.holdings.length > 0) {
            // Transform demo data to portfolio format
            portfolioData = {
                mode: 'demo',
                holdings: data.holdings.map(h => ({
                    scheme_name: h.scheme_name,
                    fund_name: h.scheme_name,
                    scheme_code: h.scheme_code,
                    category: h.category || 'Others',
                    amc: h.amc || 'Unknown',
                    invested: h.invested_amount,
                    current_value: h.current_value,
                    gain: h.gain_loss,
                    return_pct: h.gain_loss_percent,
                    units: h.units,
                    avg_cost: h.avg_cost,
                    current_nav: h.current_nav
                })),
                summary: data.totals,
                uploadedAt: new Date().toISOString(),
                uploadedFileName: 'Demo Portfolio'
            };
            
            renderDashboard();
        } else {
            throw new Error('No demo holdings found');
        }
    } catch (error) {
        console.error('Error loading demo portfolio:', error);
        document.getElementById('dashboardContent').style.display = 'none';
        document.getElementById('noData').style.display = 'block';
        window.showToast?.('Failed to load demo portfolio', 'error');
    }
}

async function loadPortfolioFromDatabase() {
    try {
        const token = localStorage.getItem('authToken');
        if (!token) {
            return false;
        }
        
        const response = await fetch('/api/portfolio/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('authToken');
                localStorage.removeItem('userInfo');
                return false;
            }
            throw new Error('Failed to load portfolio from database');
        }
        
        const data = await response.json();
        
        // Check if portfolio exists
        if (!data.holdings || data.holdings.length === 0) {
            return false;
        }
        
        // Transform API data to portfolio format
        portfolioData = {
            mode: 'database',
            portfolio_id: data.portfolio_id,
            portfolio_name: data.portfolio_name || 'My Portfolio',
            source: data.source || 'upload',
            holdings: data.holdings.map(h => ({
                scheme_name: h.fund_name,
                fund_name: h.fund_name,
                category: h.category || 'Others',
                amc: h.amc || 'Unknown',
                invested: h.invested,
                current_value: h.current_value,
                gain: h.gain,
                return_pct: h.return_pct,
                units: h.units,
                avg_cost: h.invested / h.units || 0,
                current_nav: h.nav
            })),
            summary: {
                total_invested: data.summary.total_invested,
                total_current: data.summary.total_current,
                total_gain: data.summary.total_gain,
                return_pct: data.summary.return_pct
            },
            uploadedAt: data.summary.last_updated,
            uploadedFileName: data.source || 'CAS Upload'
        };
        
        renderDashboard();
        return true;
        
    } catch (error) {
        console.error('Error loading portfolio from database:', error);
        return false;
    }
}

function renderDashboard() {
    if (!portfolioData || !portfolioData.holdings || portfolioData.holdings.length === 0) {
        document.getElementById('dashboardContent').style.display = 'none';
        document.getElementById('noData').style.display = 'block';
        return;
    }
    
    const holdings = portfolioData.holdings;
    const summary = portfolioData.summary || calculateSummary(holdings);
    
    // Show last updated timestamp
    const uploadedAt = portfolioData.uploadedAt ? new Date(portfolioData.uploadedAt) : new Date();
    const uploadedFileName = portfolioData.uploadedFileName || 'portfolio.xlsx';
    const timeAgo = getTimeAgo(uploadedAt);
    
    document.getElementById('alertText').textContent = 
        `Loaded ${holdings.length} funds • Total Invested: ₹${(summary.total_invested/100000).toFixed(2)}L • Last Updated: ${timeAgo}`;
    
    document.getElementById('totalInvested').textContent = `₹${(summary.total_invested/100000).toFixed(2)}L`;
    document.getElementById('fundCountSub').textContent = `Across ${holdings.length} schemes`;
    document.getElementById('totalCurrent').textContent = `₹${(summary.total_current/100000).toFixed(2)}L`;
    document.getElementById('dateSubtitle').textContent = `Uploaded: ${uploadedAt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}`;
    
    const gain = summary.total_gain;
    const gainEl = document.getElementById('totalGain');
    gainEl.textContent = `${gain >= 0 ? '+' : ''}₹${(Math.abs(gain)/100000).toFixed(2)}L`;
    gainEl.className = `card-value ${gain >= 0 ? 'positive' : 'negative'}`;
    
    const returnEl = document.getElementById('totalReturn');
    returnEl.textContent = `${gain >= 0 ? '+' : ''}${summary.return_pct.toFixed(2)}%`;
    returnEl.className = `card-value ${gain >= 0 ? 'positive' : 'negative'}`;
    
    const liquidFunds = holdings.filter(h => (h.category || '').toLowerCase().includes('liquid'));
    if (liquidFunds.length > 0) {
        const liquidTotal = liquidFunds.reduce((sum, h) => sum + parseFloat(h.current_value || 0), 0);
        document.getElementById('liquidCard').style.display = 'block';
        document.getElementById('liquidValue').textContent = `₹${(liquidTotal/100000).toFixed(2)}L`;
    }
    
    renderAllocationChart(holdings);
    renderFundDistChart(holdings);
    renderAMCChart(holdings);
    renderStyleChart(holdings);
    renderPerformanceChart(holdings);
    renderRiskChart(holdings);
    renderMetrics(holdings);
    renderRiskTable(holdings);
    renderHoldingsTable(holdings);
    updateRebalance();

    // Async: enrich with fund metrics then re-render risk sections
    enrichWithFundMetrics(holdings).then(() => {
        renderRiskChart(holdings);
        renderMetrics(holdings);
        renderRiskTable(holdings);
    });
}

async function enrichWithFundMetrics(holdings) {
    try {
        const fundNames = holdings.map(h => h.fund_name).filter(Boolean);
        if (fundNames.length === 0) return;
        const response = await fetch('/api/funds/metrics/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(fundNames)
        });
        if (!response.ok) return;
        const data = await response.json();
        if (!data.success || !data.results) return;
        holdings.forEach(h => {
            const metrics = data.results[h.fund_name];
            if (!metrics) return;
            const risk1y = metrics.risk && metrics.risk['1y'] || {};
            const bench = metrics.benchmark || {};
            const ret = metrics.returns || {};
            h._sharpe = risk1y.sharpe;
            h._sortino = risk1y.sortino;
            h._std_dev = risk1y.std_dev;
            h._max_drawdown = risk1y.max_drawdown;
            h._beta = bench.beta;
            h._alpha_computed = bench.alpha;
            if (!h.return_1y && ret['1y']) h.return_1y = ret['1y'].absolute;
            if (!h.return_3y && ret['3y']) h.return_3y = ret['3y'].cagr || ret['3y'].absolute;
            if ((!h.alpha || h.alpha === '-') && bench.alpha != null) h.alpha = bench.alpha;
        });
        console.log(`Dashboard: Fund metrics enriched ${data.matched}/${fundNames.length}`);
    } catch (err) {
        console.warn('Fund metrics API unavailable:', err.message);
    }
}

function calculateSummary(holdings) {
    let totalInvested = 0, totalCurrent = 0;
    holdings.forEach(h => {
        totalInvested += parseFloat(h.invested || 0);
        totalCurrent += parseFloat(h.current_value || 0);
    });
    return {
        total_invested: totalInvested,
        total_current: totalCurrent,
        total_gain: totalCurrent - totalInvested,
        return_pct: totalInvested > 0 ? (totalCurrent - totalInvested) / totalInvested * 100 : 0,
        total_funds: holdings.length
    };
}

const marketCapMap = {
    'Large Cap': 'large', 'Flexi Cap': 'large', 'Multi Cap': 'large',
    'Large & Mid': 'large', 'ELSS': 'large', 'Focused': 'large', 'Contra': 'large',
    'Mid Cap': 'mid', 'Small Cap': 'small',
    'International': 'other', 'Sectoral': 'other', 'Liquid': 'other', 'Debt': 'other', 'Hybrid': 'other'
};

function renderAllocationChart(holdings) {
    const totals = { 'Large Cap': 0, 'Mid Cap': 0, 'Small Cap': 0, 'International': 0, 'Other': 0 };
    marketCapAllocation = { large: 0, mid: 0, small: 0, other: 0 };
    
    holdings.forEach(h => {
        const cat = h.category || 'Other';
        const current = parseFloat(h.current_value || 0);
        const mcType = marketCapMap[cat] || 'other';
        
        if (mcType === 'large') { totals['Large Cap'] += current; marketCapAllocation.large += current; }
        else if (mcType === 'mid') { totals['Mid Cap'] += current; marketCapAllocation.mid += current; }
        else if (mcType === 'small') { totals['Small Cap'] += current; marketCapAllocation.small += current; }
        else if (cat === 'International') { totals['International'] += current; marketCapAllocation.other += current; }
        else { totals['Other'] += current; marketCapAllocation.other += current; }
    });
    
    const labels = Object.keys(totals).filter(k => totals[k] > 0);
    const values = labels.map(k => totals[k]);
    const colorMap = { 'Large Cap': 'var(--primary-green)', 'Mid Cap': '#ffc107', 'Small Cap': '#ff4757', 'International': '#9c27b0', 'Other': 'var(--text-secondary)' };
    
    Plotly.newPlot('allocationChart', [{
        values: values, labels: labels, type: 'pie', hole: 0.5,
        marker: { colors: labels.map(k => colorMap[k]) },
        textinfo: 'label+percent', textfont: { color: '#fff', size: 11 }
    }], {
        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false, margin: { t: 10, b: 10, l: 10, r: 10 },
        annotations: [{ text: 'Market Cap', x: 0.5, y: 0.5, font: { size: 14, color: '#fff' }, showarrow: false }]
    }, { responsive: true });
    setChartA11y('allocationChart', `Market cap allocation: ${labels.map((l,i) => l + ' ' + ((values[i]/values.reduce((a,b)=>a+b,0))*100).toFixed(0) + '%').join(', ')}`);
}

function renderFundDistChart(holdings) {
    const sorted = [...holdings].sort((a, b) => parseFloat(b.current_value || 0) - parseFloat(a.current_value || 0));
    const top10 = sorted.slice(0, 10);
    const othersValue = sorted.slice(10).reduce((sum, h) => sum + parseFloat(h.current_value || 0), 0);
    
    const labels = top10.map(h => h.fund_name ? h.fund_name.substring(0, 20) : 'Unknown');
    const values = top10.map(h => parseFloat(h.current_value || 0));
    if (othersValue > 0) { labels.push('Others'); values.push(othersValue); }
    
    Plotly.newPlot('fundDistChart', [{
        type: 'treemap',
        labels: ['Portfolio', ...labels],
        parents: ['', ...labels.map(() => 'Portfolio')],
        values: [0, ...values],
        textinfo: 'label+percent entry',
        textfont: { size: 11 },
        marker: { colors: ['', 'var(--primary-green)', 'var(--primary-green)', 'var(--dark-green)', 'var(--light-green)', '#ff4757', '#ff6b81', '#ffc107', '#00bcd4', '#e91e63', '#9c27b0', 'var(--text-secondary)'] }
    }], { paper_bgcolor: 'rgba(0,0,0,0)', margin: { t: 10, b: 10, l: 10, r: 10 } }, { responsive: true });
    setChartA11y('fundDistChart', `Fund category distribution: ${labels.join(', ')}`);
}

function renderAMCChart(holdings) {
    const totals = {}, amcFunds = {};
    holdings.forEach(h => {
        const amc = h.amc || 'Other';
        const current = parseFloat(h.current_value || 0);
        totals[amc] = (totals[amc] || 0) + current;
        if (!amcFunds[amc]) amcFunds[amc] = [];
        amcFunds[amc].push(h);
    });
    
    const colors = ['var(--primary-green)', 'var(--primary-green)', 'var(--dark-green)', '#ff4757', '#ff6b81', '#ffc107', 'var(--light-green)', '#00bcd4', '#e91e63', '#9c27b0', '#3f51b5', '#009688', '#ff9800', '#4caf50'];
    
    Plotly.newPlot('amcChart', [{
        values: Object.values(totals), labels: Object.keys(totals), type: 'pie', hole: 0.4,
        marker: { colors: colors }, textinfo: 'label+percent', textfont: { color: '#fff', size: 10 },
        hovertemplate: '<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<br><i>Click to see funds</i><extra></extra>'
    }], {
        paper_bgcolor: 'rgba(0,0,0,0)', showlegend: false, margin: { t: 10, b: 10, l: 10, r: 10 },
        annotations: [{ text: 'AMC', x: 0.5, y: 0.5, font: { size: 14, color: '#fff' }, showarrow: false }]
    }, { responsive: true });
    setChartA11y('amcChart', `AMC distribution: ${Object.keys(totals).join(', ')}`);
    
    document.getElementById('amcChart').on('plotly_click', function(data) {
        const amc = data.points[0].label, color = data.points[0].color, funds = amcFunds[amc];
        if (funds) {
            const display = document.getElementById('amcFundsDisplay');
            display.classList.add('visible');
            display.style.borderLeft = `4px solid ${color}`;
            let html = `<h5 style="color: ${color}; margin-bottom: 10px;">🏢 ${escapeHtml(amc)}</h5><div style="display: grid; gap: 8px;">`;
            funds.forEach(f => {
                const val = (parseFloat(f.current_value || 0) / 100000).toFixed(2);
                const gain = parseFloat(f.current_value || 0) - parseFloat(f.invested || 0);
                const gainColor = gain >= 0 ? 'var(--primary-green)' : '#ff4757';
                html += `<div style="display: flex; justify-content: space-between; padding: 8px 12px; background: var(--white); border-radius: 6px;"><div><span style="color: #fff;">${escapeHtml(f.fund_name)}</span><br><span style="color: var(--text-secondary); font-size: 0.8rem;">${escapeHtml(f.category || '-')}</span></div><div style="text-align: right;"><span style="color: ${color}; font-weight: 600;">₹${val}L</span><br><span style="color: ${gainColor}; font-size: 0.85rem;">${gain >= 0 ? '+' : ''}${((gain/parseFloat(f.invested||1))*100).toFixed(1)}%</span></div></div>`;
            });
            html += '</div>';
            display.innerHTML = html;
        }
    });
}

function renderStyleChart(holdings) {
    const totals = {}, styleFunds = {};
    holdings.forEach(h => {
        const style = h.style || 'Blend';
        const current = parseFloat(h.current_value || 0);
        totals[style] = (totals[style] || 0) + current;
        if (!styleFunds[style]) styleFunds[style] = [];
        styleFunds[style].push(h);
    });
    
    const styleColors = { 'GARP': 'var(--primary-green)', 'Momentum': '#ff4757', 'Quality': 'var(--primary-green)', 'Value': '#ffc107', 'Passive': '#9c27b0', 'Blend': 'var(--text-secondary)', 'Sectoral': '#e91e63', 'Liquid': '#4caf50' };
    
    Plotly.newPlot('styleChart', [{
        values: Object.values(totals), labels: Object.keys(totals), type: 'pie', hole: 0.4,
        marker: { colors: Object.keys(totals).map(k => styleColors[k] || 'var(--text-secondary)') },
        textinfo: 'label+percent', textfont: { color: '#fff', size: 10 },
        hovertemplate: '<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<br><i>Click to see funds</i><extra></extra>'
    }], {
        paper_bgcolor: 'rgba(0,0,0,0)', showlegend: false, margin: { t: 10, b: 10, l: 10, r: 10 },
        annotations: [{ text: 'Style', x: 0.5, y: 0.5, font: { size: 14, color: '#fff' }, showarrow: false }]
    }, { responsive: true });
    setChartA11y('styleChart', `Investment style distribution: ${Object.keys(totals).join(', ')}`);
    
    document.getElementById('styleChart').on('plotly_click', function(data) {
        const style = data.points[0].label, color = data.points[0].color, funds = styleFunds[style];
        if (funds) {
            const display = document.getElementById('styleFundsDisplay');
            display.classList.add('visible');
            display.style.borderLeft = `4px solid ${color}`;
            let html = `<h5 style="color: ${color}; margin-bottom: 10px;">🎨 ${escapeHtml(style)} Style</h5><div style="display: grid; gap: 8px;">`;
            funds.forEach(f => {
                const val = (parseFloat(f.current_value || 0) / 100000).toFixed(2);
                html += `<div style="display: flex; justify-content: space-between; padding: 8px 12px; background: var(--white); border-radius: 6px;"><span>${escapeHtml(f.fund_name)}</span><span style="color: ${color};">₹${val}L</span></div>`;
            });
            html += '</div>';
            display.innerHTML = html;
        }
    });
}

function renderPerformanceChart(holdings) {
    const perf = holdings.map(h => {
        const invested = parseFloat(h.invested || 0);
        const current = parseFloat(h.current_value || 0);
        const returnPct = invested > 0 ? (current - invested) / invested * 100 : 0;
        return { name: h.fund_name ? h.fund_name.substring(0, 25) : 'Unknown', returns: returnPct, current: current };
    }).sort((a, b) => b.returns - a.returns);
    
    Plotly.newPlot('performanceChart', [{
        y: perf.map(p => p.name), x: perf.map(p => p.returns), type: 'bar', orientation: 'h',
        marker: { color: perf.map(p => p.returns >= 0 ? 'var(--primary-green)' : '#ff4757') },
        text: perf.map(p => `${p.returns.toFixed(1)}%`), textposition: 'outside', textfont: { color: '#fff', size: 10 },
        hovertemplate: '<b>%{y}</b><br>Return: %{x:.1f}%<extra></extra>'
    }], {
        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: { title: 'Returns %', gridcolor: 'var(--gray-100)', zeroline: true, zerolinecolor: '#ffc107', tickfont: { color: 'var(--text-secondary)' } },
        yaxis: { tickfont: { color: 'var(--text-secondary)', size: 9 } },
        margin: { t: 10, b: 50, l: 180, r: 60 }
    }, { responsive: true });
    setChartA11y('performanceChart', 'Horizontal bar chart showing fund returns by percentage');
}

function renderRiskChart(holdings) {
    const data = holdings.filter(h => h.alpha && h.alpha !== '-').map(h => ({
        name: h.fund_name ? h.fund_name.substring(0, 15) : 'Unknown',
        alpha: parseFloat(h.alpha) || 0, category: h.category || 'Other',
        current: parseFloat(h.current_value || 0)
    }));
    
    if (data.length === 0) {
        document.getElementById('riskChart').innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 50px;">No alpha data available</p>';
        return;
    }
    
    const categoryColors = { 'Large Cap': 'var(--primary-green)', 'Mid Cap': '#ffc107', 'Small Cap': '#ff4757', 'Flexi Cap': 'var(--primary-green)', 'International': '#9c27b0' };
    
    Plotly.newPlot('riskChart', [{
        x: data.map(d => d.category), y: data.map(d => d.alpha), mode: 'markers+text', type: 'scatter',
        marker: { size: data.map(d => Math.sqrt(d.current / 10000) + 10), color: data.map(d => categoryColors[d.category] || 'var(--text-secondary)'), opacity: 0.8 },
        text: data.map(d => d.name), textposition: 'top center', textfont: { size: 9, color: '#fff' },
        hovertemplate: '<b>%{text}</b><br>Category: %{x}<br>Alpha: %{y:.2f}<extra></extra>'
    }], {
        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: { title: 'Category', tickfont: { color: 'var(--text-secondary)' }, gridcolor: 'var(--gray-100)' },
        yaxis: { title: 'Alpha', tickfont: { color: 'var(--text-secondary)' }, gridcolor: 'var(--gray-100)', zeroline: true, zerolinecolor: '#ffc107' },
        margin: { t: 30, b: 50, l: 60, r: 20 }
    }, { responsive: true });
    setChartA11y('riskChart', 'Fund risk analysis scatter plot showing alpha values by category');
}

function renderMetrics(holdings) {
    const summary = calculateSummary(holdings);
    const profitableCount = holdings.filter(h => parseFloat(h.current_value || 0) > parseFloat(h.invested || 0)).length;
    const alphaValues = holdings.filter(h => h.alpha && h.alpha !== '-').map(h => parseFloat(h.alpha));
    const avgAlpha = alphaValues.length > 0 ? alphaValues.reduce((a, b) => a + b, 0) / alphaValues.length : 0;

    // Weighted-average risk metrics
    let wSharpe = 0, wBeta = 0, wSum = 0;
    holdings.forEach(h => {
        const w = parseFloat(h.current_value || 0);
        if (h._sharpe != null) { wSharpe += h._sharpe * w; wSum += w; }
        if (h._beta != null) wBeta += h._beta * w;
    });
    const avgSharpe = wSum > 0 ? wSharpe / wSum : null;
    const avgBeta = wSum > 0 ? wBeta / wSum : null;
    const fmtM = v => v != null ? v.toFixed(2) : '-';
    const mClr = (v, g = 0) => v != null ? (v >= g ? 'var(--primary-green)' : '#ff4757') : 'var(--text-secondary)';
    
    document.getElementById('metricsGrid').innerHTML = `
        <div class="metric-box"><div class="metric-value" style="color: var(--primary-green);">${holdings.length}</div><div class="metric-label">Total Funds</div></div>
        <div class="metric-box"><div class="metric-value" style="color: var(--primary-green);">${profitableCount}</div><div class="metric-label">Profitable<br>(${((profitableCount/holdings.length)*100).toFixed(0)}%)</div></div>
        <div class="metric-box"><div class="metric-value" style="color: ${avgAlpha >= 0 ? 'var(--primary-green)' : '#ff4757'};">${avgAlpha.toFixed(2)}</div><div class="metric-label">Avg Alpha</div></div>
        <div class="metric-box"><div class="metric-value" style="color: ${mClr(avgSharpe)};">${fmtM(avgSharpe)}</div><div class="metric-label">Sharpe Ratio</div></div>
        <div class="metric-box"><div class="metric-value" style="color: ${mClr(avgBeta, 0.5)};">${fmtM(avgBeta)}</div><div class="metric-label">Avg Beta</div></div>
        <div class="metric-box"><div class="metric-value" style="color: var(--primary-green);">₹${(summary.total_current/100000).toFixed(1)}L</div><div class="metric-label">Total Value</div></div>
        <div class="metric-box"><div class="metric-value" style="color: ${summary.return_pct >= 0 ? 'var(--primary-green)' : '#ff4757'};">${summary.return_pct.toFixed(1)}%</div><div class="metric-label">Total Return</div></div>
    `;
}

function renderRiskTable(holdings) {
    const sorted = [...holdings].sort((a, b) => parseFloat(b.current_value || 0) - parseFloat(a.current_value || 0));
    const fmt = (v, s = '') => v != null ? parseFloat(v).toFixed(2) + s : '-';
    const cls = (v, g = 0) => v != null ? (parseFloat(v) >= g ? 'gain' : 'loss') : '';
    let html = '';
    sorted.forEach(h => {
        const invested = parseFloat(h.invested || 0), current = parseFloat(h.current_value || 0);
        const returnPct = invested > 0 ? ((current - invested) / invested * 100).toFixed(1) : '0.0';
        const returnClass = current >= invested ? 'gain' : 'loss';
        html += `<tr><td>${escapeHtml(h.fund_name || '-')}</td><td>${escapeHtml(h.category || '-')}</td><td>₹${(invested/100000).toFixed(2)}L</td><td>₹${(current/100000).toFixed(2)}L</td><td class="${returnClass}">${current >= invested ? '+' : ''}${returnPct}%</td><td class="${cls(h.alpha)}">${fmt(h.alpha)}</td><td class="${cls(h._beta, 0.5)}">${fmt(h._beta)}</td><td class="${cls(h._sharpe)}">${fmt(h._sharpe)}</td><td>${h.return_1y != null ? parseFloat(h.return_1y).toFixed(1) + '%' : '-'}</td><td>${h.return_3y != null ? parseFloat(h.return_3y).toFixed(1) + '%' : '-'}</td></tr>`;
    });
    document.getElementById('riskTableBody').innerHTML = html;
}

function renderHoldingsTable(holdings) {
    const styleClasses = { 'GARP': 'style-garp', 'Momentum': 'style-momentum', 'Quality': 'style-quality', 'Value': 'style-value', 'Passive': 'style-passive', 'Blend': 'style-blend', 'Sectoral': 'style-sectoral', 'Liquid': 'style-liquid' };
    let html = '';
    holdings.forEach(h => {
        const invested = parseFloat(h.invested || 0), current = parseFloat(h.current_value || 0);
        const gain = current - invested;
        const returnPct = invested > 0 ? (gain / invested * 100).toFixed(1) : '0.0';
        const gainClass = gain >= 0 ? 'gain' : 'loss';
        const styleClass = styleClasses[h.style] || 'style-blend';
        
        let actionBadge = '<span class="badge badge-hold">HOLD</span>';
        const alpha = parseFloat(h.alpha) || 0;
        if (gain < 0 && alpha < 0) actionBadge = '<span class="badge badge-review">REVIEW</span>';
        else if (alpha < -3) actionBadge = '<span class="badge badge-exit">EXIT</span>';
        else if (invested === current) actionBadge = '<span class="badge badge-new">NEW</span>';
        
        html += `<tr><td class="fund-name">${escapeHtml(h.fund_name || '-')}</td><td><span class="category-badge">${escapeHtml(h.category || '-')}</span></td><td>₹${(invested/100000).toFixed(2)}L</td><td>₹${(current/100000).toFixed(2)}L</td><td class="${gainClass}">${gain >= 0 ? '+' : ''}₹${(Math.abs(gain)/100000).toFixed(2)}L</td><td class="${gainClass}">${gain >= 0 ? '+' : ''}${returnPct}%</td><td><span class="${styleClass}">${escapeHtml(h.style || '-')}</span></td><td>${h.return_1y || h['1Y Return'] || '-'}</td><td>${h.return_3y || h['3Y Return'] || '-'}</td><td class="${parseFloat(h.alpha) >= 0 ? 'gain' : 'loss'}">${h.alpha || '-'}</td><td>${actionBadge}</td></tr>`;
    });
    document.getElementById('holdingsTable').innerHTML = html;
}

function setMode(mode) {
    currentMode = mode;
    document.getElementById('modeRebalance').classList.toggle('active', mode === 'rebalance');
    document.getElementById('modeFresh').classList.toggle('active', mode === 'fresh');
    document.getElementById('modeDescription').textContent = mode === 'rebalance' 
        ? 'Sell from overweight categories, buy in underweight (may have tax implications)'
        : 'Calculate how much fresh money to add to each category';
    updateRebalance();
}

function setPreset(large, mid, small) {
    document.getElementById('largeSlider').value = large;
    document.getElementById('midSlider').value = mid;
    document.getElementById('smallSlider').value = small;
    updateRebalance();
}

function updateRebalance() {
    const totalEquity = marketCapAllocation.large + marketCapAllocation.mid + marketCapAllocation.small;
    if (totalEquity === 0) return;
    
    const currentLargePct = (marketCapAllocation.large / totalEquity * 100).toFixed(1);
    const currentMidPct = (marketCapAllocation.mid / totalEquity * 100).toFixed(1);
    const currentSmallPct = (marketCapAllocation.small / totalEquity * 100).toFixed(1);
    
    const targetLarge = parseInt(document.getElementById('largeSlider').value);
    const targetMid = parseInt(document.getElementById('midSlider').value);
    const targetSmall = parseInt(document.getElementById('smallSlider').value);
    
    document.getElementById('largeTarget').textContent = targetLarge + '%';
    document.getElementById('midTarget').textContent = targetMid + '%';
    document.getElementById('smallTarget').textContent = targetSmall + '%';
    
    document.getElementById('largeCurrent').textContent = `Current: ${currentLargePct}%`;
    document.getElementById('midCurrent').textContent = `Current: ${currentMidPct}%`;
    document.getElementById('smallCurrent').textContent = `Current: ${currentSmallPct}%`;
    
    const largeDiff = (targetLarge - currentLargePct).toFixed(1);
    const midDiff = (targetMid - currentMidPct).toFixed(1);
    const smallDiff = (targetSmall - currentSmallPct).toFixed(1);
    
    document.getElementById('largeDiff').textContent = (largeDiff >= 0 ? '+' : '') + largeDiff + '%';
    document.getElementById('largeDiff').style.color = largeDiff >= 0 ? 'var(--primary-green)' : '#ff4757';
    document.getElementById('midDiff').textContent = (midDiff >= 0 ? '+' : '') + midDiff + '%';
    document.getElementById('midDiff').style.color = midDiff >= 0 ? 'var(--primary-green)' : '#ff4757';
    document.getElementById('smallDiff').textContent = (smallDiff >= 0 ? '+' : '') + smallDiff + '%';
    document.getElementById('smallDiff').style.color = smallDiff >= 0 ? 'var(--primary-green)' : '#ff4757';
    
    let html = currentMode === 'rebalance' 
        ? generateRebalanceActions(totalEquity, targetLarge, targetMid, targetSmall, currentLargePct, currentMidPct, currentSmallPct)
        : generateFreshInvestmentActions(totalEquity, targetLarge, targetMid, targetSmall, currentLargePct, currentMidPct, currentSmallPct);
    document.getElementById('rebalanceActions').innerHTML = html;
}

function generateRebalanceActions(total, tgtL, tgtM, tgtS, curL, curM, curS) {
    const targetLargeAmt = total * tgtL / 100, targetMidAmt = total * tgtM / 100, targetSmallAmt = total * tgtS / 100;
    const sellLarge = Math.max(0, marketCapAllocation.large - targetLargeAmt);
    const sellMid = Math.max(0, marketCapAllocation.mid - targetMidAmt);
    const sellSmall = Math.max(0, marketCapAllocation.small - targetSmallAmt);
    const buyLarge = Math.max(0, targetLargeAmt - marketCapAllocation.large);
    const buyMid = Math.max(0, targetMidAmt - marketCapAllocation.mid);
    const buySmall = Math.max(0, targetSmallAmt - marketCapAllocation.small);
    
    let html = '<div style="display: grid; gap: 15px;">';
    if (sellLarge > 0) html += `<div style="padding: 15px; background: rgba(255,71,87,0.2); border-radius: 8px; border-left: 3px solid #ff4757;"><strong style="color: #ff4757;">📉 SELL Large Cap:</strong> ₹${(sellLarge/100000).toFixed(2)}L</div>`;
    if (sellMid > 0) html += `<div style="padding: 15px; background: rgba(255,193,7,0.2); border-radius: 8px; border-left: 3px solid #ffc107;"><strong style="color: #ffc107;">📉 SELL Mid Cap:</strong> ₹${(sellMid/100000).toFixed(2)}L</div>`;
    if (sellSmall > 0) html += `<div style="padding: 15px; background: rgba(255,71,87,0.2); border-radius: 8px; border-left: 3px solid #ff4757;"><strong style="color: #ff4757;">📉 SELL Small Cap:</strong> ₹${(sellSmall/100000).toFixed(2)}L</div>`;
    if (buyLarge > 0) html += `<div style="padding: 15px; background: rgba(0,212,255,0.2); border-radius: 8px; border-left: 3px solid var(--primary-green);"><strong style="color: var(--primary-green);">📈 BUY Large Cap:</strong> ₹${(buyLarge/100000).toFixed(2)}L</div>`;
    if (buyMid > 0) html += `<div style="padding: 15px; background: rgba(255,193,7,0.2); border-radius: 8px; border-left: 3px solid #ffc107;"><strong style="color: #ffc107;">📈 BUY Mid Cap:</strong> ₹${(buyMid/100000).toFixed(2)}L</div>`;
    if (buySmall > 0) html += `<div style="padding: 15px; background: rgba(0,255,136,0.2); border-radius: 8px; border-left: 3px solid var(--primary-green);"><strong style="color: var(--primary-green);">📈 BUY Small Cap:</strong> ₹${(buySmall/100000).toFixed(2)}L</div>`;
    if (sellLarge === 0 && sellMid === 0 && sellSmall === 0 && buyLarge === 0 && buyMid === 0 && buySmall === 0) {
        html += '<div style="padding: 15px; background: rgba(0,255,136,0.2); border-radius: 8px;"><strong style="color: var(--primary-green);">✅ Portfolio is already balanced!</strong></div>';
    }
    html += '</div>';
    if (sellLarge > 0 || sellMid > 0 || sellSmall > 0) {
        html += `<div style="margin-top: 15px; padding: 15px; background: rgba(255,193,7,0.1); border-radius: 8px;"><strong style="color: #ffc107;">⚠️ Tax Note:</strong><p style="color: var(--text-secondary); margin-top: 5px; font-size: 0.85rem;">Selling may attract LTCG tax (12.5% on gains above ₹1.25L). Consider using "Add Fresh Money" mode to avoid taxes.</p></div>`;
    }
    return html;
}

function generateFreshInvestmentActions(total, tgtL, tgtM, tgtS, curL, curM, curS) {
    const targetTotal = total / (Math.max(curL, curM, curS) / Math.max(tgtL, tgtM, tgtS));
    const freshTotal = Math.max(0, targetTotal - total);
    const freshLarge = Math.max(0, (targetTotal * tgtL / 100) - marketCapAllocation.large);
    const freshMid = Math.max(0, (targetTotal * tgtM / 100) - marketCapAllocation.mid);
    const freshSmall = Math.max(0, (targetTotal * tgtS / 100) - marketCapAllocation.small);
    
    let html = '<div style="display: grid; gap: 15px;">';
    html += `<div style="padding: 15px; background: rgba(123,44,191,0.2); border-radius: 8px; border-left: 3px solid var(--dark-green);"><strong style="color: var(--light-green);">💰 Total Fresh Investment Needed:</strong> ₹${(freshTotal/100000).toFixed(2)}L</div>`;
    if (freshLarge > 0) html += `<div style="padding: 15px; background: rgba(0,212,255,0.1); border-radius: 8px;"><strong style="color: var(--primary-green);">Large Cap:</strong> Add ₹${(freshLarge/100000).toFixed(2)}L<br><span style="color: var(--text-secondary); font-size: 0.85rem;">Suggested: Parag Parikh Flexi Cap, HDFC Flexicap</span></div>`;
    if (freshMid > 0) html += `<div style="padding: 15px; background: rgba(255,193,7,0.1); border-radius: 8px;"><strong style="color: #ffc107;">Mid Cap:</strong> Add ₹${(freshMid/100000).toFixed(2)}L<br><span style="color: var(--text-secondary); font-size: 0.85rem;">Suggested: Motilal Oswal Midcap, Kotak Emerging Equity</span></div>`;
    if (freshSmall > 0) html += `<div style="padding: 15px; background: rgba(255,71,87,0.1); border-radius: 8px;"><strong style="color: #ff4757;">Small Cap:</strong> Add ₹${(freshSmall/100000).toFixed(2)}L<br><span style="color: var(--text-secondary); font-size: 0.85rem;">Suggested: Nippon Small Cap, Axis Small Cap</span></div>`;
    html += '</div>';
    if (freshTotal > 100000) {
        html += `<div style="margin-top: 15px; padding: 15px; background: rgba(0,212,255,0.1); border-radius: 8px;"><strong style="color: var(--primary-green);">💡 SIP Alternative:</strong><p style="color: var(--text-secondary); margin-top: 5px; font-size: 0.9rem;">Instead of lumpsum, start SIP of ₹${((freshTotal/12)/1000).toFixed(0)}K/month for 12 months to average out market volatility.</p></div>`;
    }
    return html;
}

// Overlap Analysis
async function analyzeCurrentPortfolio() {
    const btn = document.getElementById('analyze-overlap-btn');
    const spinner = document.getElementById('analyze-overlap-spinner');
    try {
        if (btn) { btn.disabled = true; }
        if (spinner) { spinner.style.display = 'inline-block'; }

        if (!portfolioData || !portfolioData.holdings) {
            toast && toast.error && toast.error('No portfolio data available');
            return;
        }

        // Extract unique fund names from holdings and sanitize
        const fundNames = [...new Set(portfolioData.holdings.map(h => (h.fund_name || '').trim()).filter(Boolean))];

        if (fundNames.length < 2) {
            toast && toast.warning && toast.warning('Need at least 2 funds for overlap analysis');
            return;
        }

        // Lazy-check for overlap analyzer (in case script not loaded)
        if (!window.overlapAnalyzer) {
            // Try to dynamically load script
            await new Promise((resolve, reject) => {
                const s = document.createElement('script');
                s.src = '/js/overlap.js';
                s.onload = resolve;
                s.onerror = () => reject(new Error('Failed to load overlap module'));
                document.head.appendChild(s);
            });
        }

        // Call analyzer and await completion (it shows its own loading/toast)
        await window.overlapAnalyzer.analyzePortfolio(fundNames);
    } catch (err) {
        console.error('Overlap analysis failed', err);
        if (typeof errorHandler !== 'undefined') {
            errorHandler.handleAPIError(err, { feature: 'overlap_analysis' });
        } else if (toast && toast.error) {
            toast.error('Overlap analysis failed: ' + (err.message || err));
        }
    } finally {
        if (btn) { btn.disabled = false; }
        if (spinner) { spinner.style.display = 'none'; }
    }
}

function exportData() {
    if (!portfolioData) return;
    const dataStr = JSON.stringify(portfolioData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'portfolio_export.json';
    a.click();
    URL.revokeObjectURL(url);
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} min${minutes > 1 ? 's' : ''} ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;
    
    const weeks = Math.floor(days / 7);
    if (weeks < 4) return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    
    const months = Math.floor(days / 30);
    return `${months} month${months > 1 ? 's' : ''} ago`;
}

// Set AI as unavailable (not using AI features)
window.AI_AVAILABLE = false;

// Dashboard chat functions
function appendDashboardMessage(role, text) {
    const messages = document.getElementById('dashboardChatMessages');
    if (!messages) return;
    const el = document.createElement('div');
    el.className = 'chat-message ' + (role === 'user' ? 'user' : 'ai');
    el.style.margin = '6px 0';
    el.style.padding = '8px';
    el.style.borderRadius = '8px';
    el.style.background = role === 'user' ? 'rgba(123,44,191,0.7)' : 'rgba(255,255,255,0.03)';
    el.style.color = role === 'user' ? '#fff' : '#fff';
    el.innerText = text;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
}

async function sendDashboardChat() {
    const input = document.getElementById('dashboardChatInput');
    if (!input) return;
    const message = input.value.trim();
    if (!message) return;
    appendDashboardMessage('user', message);
    input.value = '';

    if (!window.AI_AVAILABLE) {
        appendDashboardMessage('ai', '⚠️ AI is currently unavailable. Use the dashboard search or retry later.');
        return;
    }

    try {
        const token = localStorage.getItem('authToken') || localStorage.getItem('access_token');
        const resp = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token || ''}` },
            body: JSON.stringify({ message })
        });
        if (!resp.ok) throw new Error('AI chat failed');
        const data = await resp.json();
        appendDashboardMessage('ai', data.response || data.message || 'No response');
    } catch (e) {
        appendDashboardMessage('ai', '❌ Error: ' + e.message);
    }
}

// Initialize chat handlers on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Chat handlers
    const sendBtn = document.getElementById('dashboardChatSend');
    const input = document.getElementById('dashboardChatInput');
    if (sendBtn) sendBtn.addEventListener('click', () => sendDashboardChat());
    if (input) input.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendDashboardChat(); });

    // XIRR & Compare handlers
    const fetchBtn = document.getElementById('fetch-xirr-btn');
    if (fetchBtn) fetchBtn.addEventListener('click', () => fetchXirrAndCompare());
    
    // Only auto-populate portfolio ID if user is authenticated
    const token = localStorage.getItem('authToken');
    if (token) {
        autoPopulatePortfolioId();
    }
});

async function autoPopulatePortfolioId() {
    const pidInput = document.getElementById('portfolio-id-input');
    if (!pidInput) return;

    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('authToken') || localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
        const resp = await fetch('/api/portfolio/latest-id', { headers });
        if (resp.ok) {
            const data = await resp.json();
            pidInput.value = data.id;
        }
    } catch (e) {
        // Silent fail — user can enter manually
    }
}

async function fetchXirrAndCompare() {
    const pid = document.getElementById('portfolio-id-input').value;
    if (!pid) { toast.error('Enter a portfolio ID'); return; }
    const large = parseFloat(document.getElementById('large-rate').value)/100 || 0.12;
    const mid = parseFloat(document.getElementById('mid-rate').value)/100 || 0.14;
    const small = parseFloat(document.getElementById('small-rate').value)/100 || 0.16;

    // Prepare headers with auth if present
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('authToken') || localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
        // Fetch XIRR
        const xresp = await fetch(`/api/analytics/xirr/${pid}`, { headers });
        if (!xresp.ok) { const t = await xresp.text(); throw new Error(t || 'XIRR fetch failed'); }
        const xdata = await xresp.json();
        document.getElementById('portfolio-xirr').textContent = xdata.portfolio_xirr_pct ? xdata.portfolio_xirr_pct + ' %' : '-- %';

        // Fetch comparison
        const creq = `/api/analytics/compare_index/${pid}?large_rate=${large}&mid_rate=${mid}&small_rate=${small}`;
        const cresp = await fetch(creq, { headers });
        if (!cresp.ok) { const t = await cresp.text(); throw new Error(t || 'Compare fetch failed'); }
        const cdata = await cresp.json();

        // Render compare results
        const el = document.getElementById('compare-results');
        const lines = [];
        lines.push(`<strong>Allocation:</strong> Large ${cdata.allocation_pct.Large?.toFixed(1) || 0}% | Mid ${cdata.allocation_pct.Mid?.toFixed(1) || 0}% | Small ${cdata.allocation_pct.Small?.toFixed(1) || 0}%`);
        lines.push(`<strong>Actual AUM:</strong> ₹${(cdata.actual_by_bucket.Large||0).toFixed(0)} (Large), ₹${(cdata.actual_by_bucket.Mid||0).toFixed(0)} (Mid), ₹${(cdata.actual_by_bucket.Small||0).toFixed(0)} (Small)`);
        lines.push(`<strong>Hypothetical Index Value:</strong> ₹${(cdata.hypothetical_by_bucket.Large||0).toFixed(0)} (Large), ₹${(cdata.hypothetical_by_bucket.Mid||0).toFixed(0)} (Mid), ₹${(cdata.hypothetical_by_bucket.Small||0).toFixed(0)} (Small)`);
        lines.push(`<strong>Hypothetical Total:</strong> ₹${(cdata.hypothetical_total||0).toFixed(0)} vs Actual ₹${( (cdata.actual_by_bucket.Large||0)+(cdata.actual_by_bucket.Mid||0)+(cdata.actual_by_bucket.Small||0) ).toFixed(0)}`);
        el.innerHTML = lines.join('<br>');

    } catch (e) {
        toast.error('Failed: ' + e.message);
    }
}
