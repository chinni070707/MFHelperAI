// SIP Calculator - Advanced Features
// Modes: Forward, Reverse (Goal-based), Retirement Planning

let currentMode = 'forward';

// Mode Switching
function switchMode(mode) {
    currentMode = mode;
    
    // Update tabs
    document.querySelectorAll('.mode-tab').forEach(tab => tab.classList.remove('active'));
    document.getElementById(`tab-${mode}`).classList.add('active');
    
    // Show/hide input sections
    document.getElementById('forwardMode').style.display = mode === 'forward' ? 'block' : 'none';
    document.getElementById('reverseMode').style.display = mode === 'reverse' ? 'block' : 'none';
    document.getElementById('retirementMode').style.display = mode === 'retirement' ? 'block' : 'none';
    
    // Clear results
    document.getElementById('resultsCard').innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📈</div>
            <h3>Calculate Your ${mode === 'forward' ? 'Returns' : mode === 'reverse' ? 'Required SIP' : 'Retirement Plan'}</h3>
            <p>Enter your details and click calculate</p>
        </div>
    `;
}

// Toggle step-up section
function toggleStepUp() {
    const enabled = document.getElementById('enableStepUp').checked;
    document.getElementById('stepUpGroup').style.display = enabled ? 'block' : 'none';
}

// Update inflation based on goal type
function updateGoalInflation() {
    const goalType = document.getElementById('goalType').value;
    const inflationInput = document.getElementById('inflationRate');
    const inflationHelp = document.getElementById('inflationHelp');
    
    const inflationRates = {
        'retirement': { rate: 6, help: 'General inflation: 5-6%' },
        'education': { rate: 10, help: 'Education inflation: 8-12%' },
        'house': { rate: 5, help: 'Real estate inflation: 4-6%' },
        'wedding': { rate: 8, help: 'Wedding cost inflation: 7-10%' },
        'car': { rate: 4, help: 'Vehicle inflation: 3-5%' },
        'custom': { rate: 6, help: 'General inflation: 5-6%' }
    };
    
    const config = inflationRates[goalType];
    inflationInput.value = config.rate;
    inflationHelp.textContent = config.help;
}

// Utility Functions
function formatCurrency(amount) {
    if (amount >= 10000000) { // >= 1 Crore
        return `₹${(amount / 10000000).toFixed(2)}Cr`;
    } else if (amount >= 100000) { // >= 1 Lakh
        return `₹${(amount / 100000).toFixed(2)}L`;
    } else {
        return `₹${amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    }
}

function formatPercentage(value) {
    return `${value.toFixed(2)}%`;
}

// ==================== FORWARD CALCULATOR ====================
function calculateSIP() {
    const sipAmount = parseFloat(document.getElementById('sipAmount').value);
    const duration = parseInt(document.getElementById('duration').value);
    const returnRate = parseFloat(document.getElementById('returnRate').value) / 100;
    const enableStepUp = document.getElementById('enableStepUp').checked;
    const stepUpRate = parseFloat(document.getElementById('stepUpRate').value) / 100;

    if (!sipAmount || sipAmount < 500) {
        alert('Please enter a valid SIP amount (minimum ₹500)');
        return;
    }
    if (!duration || duration < 1) {
        alert('Please enter a valid investment period');
        return;
    }

    // Calculate regular SIP
    const regularSIP = calculateRegularSIP(sipAmount, duration, returnRate);

    // Calculate market scenarios
    const scenarios = calculateScenarios(sipAmount, duration, enableStepUp, stepUpRate);

    // Calculate step-up SIP
    let stepUpSIP = null;
    if (enableStepUp) {
        stepUpSIP = calculateStepUpSIP(sipAmount, duration, returnRate, stepUpRate);
    }

    displayForwardResults(regularSIP, stepUpSIP, scenarios, enableStepUp);
}

function calculateRegularSIP(monthlyAmount, years, annualReturn) {
    const months = years * 12;
    const monthlyRate = annualReturn / 12;
    
    let totalInvested = 0;
    let maturityValue = 0;
    const yearlyData = [];

    for (let month = 1; month <= months; month++) {
        totalInvested += monthlyAmount;
        maturityValue = (maturityValue + monthlyAmount) * (1 + monthlyRate);

        if (month % 12 === 0) {
            yearlyData.push({
                year: month / 12,
                invested: totalInvested,
                value: maturityValue
            });
        }
    }

    return {
        totalInvested,
        maturityValue,
        returns: maturityValue - totalInvested,
        yearlyData
    };
}

function calculateStepUpSIP(initialAmount, years, annualReturn, stepUpRate) {
    const monthlyRate = annualReturn / 12;
    
    let currentMonthlyAmount = initialAmount;
    let totalInvested = 0;
    let maturityValue = 0;
    const yearlyData = [];

    for (let year =  1; year <= years; year++) {
        for (let month = 1; month <= 12; month++) {
            totalInvested += currentMonthlyAmount;
            maturityValue = (maturityValue + currentMonthlyAmount) * (1 + monthlyRate);
        }

        yearlyData.push({
            year: year,
            invested: totalInvested,
            value: maturityValue,
            monthlyAmount: currentMonthlyAmount
        });

        currentMonthlyAmount *= (1 + stepUpRate);
    }

    return {
        totalInvested,
        maturityValue,
        returns: maturityValue - totalInvested,
        yearlyData,
        finalMonthlyAmount: currentMonthlyAmount / (1 + stepUpRate)
    };
}

function calculateScenarios(sipAmount, duration, enableStepUp, stepUpRate) {
    const scenarios = [
        { name: 'Pessimistic', return: 0.07, label: '7% (Conservative)', class: 'pessimistic', icon: '📉' },
        { name: 'Realistic', return: 0.12, label: '12% (Average)', class: 'realistic', icon: '📊' },
        { name: 'Optimistic', return: 0.15, label: '15% (Aggressive)', class: 'optimistic', icon: '📈' }
    ];

    return scenarios.map(s => {
        const result = enableStepUp 
            ? calculateStepUpSIP(sipAmount, duration, s.return, stepUpRate)
            : calculateRegularSIP(sipAmount, duration, s.return);
        return { ...s, ...result };
    });
}

function displayForwardResults(regularSIP, stepUpSIP, scenarios, showComparison) {
    const resultsCard = document.getElementById('resultsCard');
    const primaryData = stepUpSIP || regularSIP;

    let html = `
        <h2 class="card-title">📊 Investment Projection</h2>
        
        <!-- Summary Cards -->
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Total Invested</div>
                <div class="summary-value">${formatCurrency(primaryData.totalInvested)}</div>
                <div class="summary-sub">${primaryData.yearlyData.length} years of SIP</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Maturity Value</div>
                <div class="summary-value">${formatCurrency(primaryData.maturityValue)}</div>
                <div class="summary-sub">Expected corpus</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Total Returns</div>
                <div class="summary-value">${formatCurrency(primaryData.returns)}</div>
                <div class="summary-sub">${formatPercentage((primaryData.returns / primaryData.totalInvested) * 100)} gain</div>
            </div>
        </div>

        <!-- Market Scenarios -->
        <div class="info-box">
            <div class="info-box-title">
                <span>💡</span>
                <span>Market Scenario Analysis</span>
            </div>
            <div class="info-box-content">
                Markets don't always give the same returns. Here's how your investment could perform under different scenarios:
            </div>
        </div>

        <div class="scenario-grid">
            ${scenarios.map(s => `
                <div class="scenario-card ${s.class}">
                    <div class="scenario-label">${s.icon} ${s.name}</div>
                    <div class="scenario-return">${s.label}</div>
                    <div class="scenario-value">${formatCurrency(s.maturityValue)}</div>
                </div>
            `).join('')}
        </div>

        <!-- Growth Chart -->
        <div class="chart-container">
            <div class="chart-title">📈 Wealth Growth Over Time</div>
            <div id="growthChart"></div>
        </div>
    `;

    if (showComparison && stepUpSIP) {
        html += `
            <!-- Step-up vs Regular Comparison -->
            <div class="info-box">
                <div class="info-box-title">
                    <span>🚀</span>
                    <span>Power of Step-up SIP</span>
                </div>
                <div class="info-box-content">
                    By increasing your SIP annually, you significantly boost your wealth creation potential.
                </div>
            </div>

            <div class="comparison-table">
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Regular SIP</th>
                            <th>Step-up SIP</th>
                            <th>Benefit</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Total Investment</td>
                            <td>${formatCurrency(regularSIP.totalInvested)}</td>
                            <td>${formatCurrency(stepUpSIP.totalInvested)}</td>
                            <td class="highlight">+${formatCurrency(stepUpSIP.totalInvested - regularSIP.totalInvested)}</td>
                        </tr>
                        <tr>
                            <td>Maturity Value</td>
                            <td>${formatCurrency(regularSIP.maturityValue)}</td>
                            <td>${formatCurrency(stepUpSIP.maturityValue)}</td>
                            <td class="highlight">+${formatCurrency(stepUpSIP.maturityValue - regularSIP.maturityValue)}</td>
                        </tr>
                        <tr>
                            <td>Total Returns</td>
                            <td>${formatCurrency(regularSIP.returns)}</td>
                            <td>${formatCurrency(stepUpSIP.returns)}</td>
                            <td class="highlight">+${formatCurrency(stepUpSIP.returns - regularSIP.returns)}</td>
                        </tr>
                        <tr>
                            <td>Return %</td>
                            <td>${formatPercentage((regularSIP.returns / regularSIP.totalInvested) * 100)}</td>
                            <td>${formatPercentage((stepUpSIP.returns / stepUpSIP.totalInvested) * 100)}</td>
                            <td><span class="benefit-badge">✓ Better Returns</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    }

    resultsCard.innerHTML = html;
    plotGrowthChart(regularSIP, stepUpSIP, scenarios);
    trackAnalytics('forward_sip', { step_up: showComparison });
}

// ==================== REVERSE CALCULATOR (GOAL-BASED) ====================
function calculateGoal() {
    const goalType = document.getElementById('goalType').value;
    const goalAmount = parseFloat(document.getElementById('goalAmount').value);
    const goalYears = parseInt(document.getElementById('goalYears').value);
    const inflationRate = parseFloat(document.getElementById('inflationRate').value) / 100;
    const expectedReturn = parseFloat(document.getElementById('expectedReturn').value) / 100;
    const existingCorpus = parseFloat(document.getElementById('existingCorpus').value) || 0;

    if (!goalAmount || goalAmount < 100000) {
        alert('Please enter a valid goal amount (minimum ₹1 Lakh)');
        return;
    }
    if (!goalYears || goalYears < 1) {
        alert('Please enter a valid time period');
        return;
    }

    // Calculate future value with inflation
    const futureValue = goalAmount * Math.pow(1 + inflationRate, goalYears);

    // Calculate future value of existing corpus
    const existingFutureValue = existingCorpus * Math.pow(1 + expectedReturn, goalYears);

    // Calculate gap
    const gap = Math.max(0, futureValue - existingFutureValue);

    // Calculate required monthly SIP
    const months = goalYears * 12;
    const monthlyRate = expectedReturn / 12;
    const requiredSIP = gap * monthlyRate / ((Math.pow(1 + monthlyRate, months) - 1) * (1 + monthlyRate));

    // Calculate step-up SIP (with 10% annual increase)
    const stepUpSIP = calculateRequiredStepUpSIP(gap, goalYears, expectedReturn, 0.10);

    displayGoalResults({
        goalType,
        goalAmount,
        futureValue,
        goalYears,
        inflationRate,
        existingCorpus,
        existingFutureValue,
        gap,
        requiredSIP,
        stepUpSIP,
        expectedReturn
    });
}

function calculateRequiredStepUpSIP(targetAmount, years, annualReturn, stepUpRate) {
    // Iterative calculation for step-up SIP
    let low = 0, high = targetAmount / (years * 12);
    let iterations = 0;
    const maxIterations = 100;

    while (high - low > 1 && iterations < maxIterations) {
        const mid = (low + high) / 2;
        const result = calculateStepUpSIP(mid, years, annualReturn, stepUpRate);
        
        if (result.maturityValue < targetAmount) {
            low = mid;
        } else {
            high = mid;
        }
        iterations++;
    }

    const initialSIP = (low + high) / 2;
    const result = calculateStepUpSIP(initialSIP, years, annualReturn, stepUpRate);
    
    return {
        initialMonthly: initialSIP,
        finalMonthly: result.finalMonthlyAmount,
        totalInvested: result.totalInvested,
        maturityValue: result.maturityValue
    };
}

function displayGoalResults(data) {
    const resultsCard = document.getElementById('resultsCard');

    const goalNames = {
        'retirement': '🏖️ Retirement',
        'education': '🎓 Child Education',
        'house': '🏠 House/Property',
        'wedding': '💒 Wedding',
        'car': '🚗 Car/Vehicle',
        'custom': '🎯 Custom Goal'
    };

    let html = `
        <h2 class="card-title">🎯 Goal-Based Investment Plan</h2>
        
        <!-- Goal Summary -->
        <div class="info-box">
            <div class="info-box-title">
                <span>${goalNames[data.goalType].split(' ')[0]}</span>
                <span>Your Goal: ${goalNames[data.goalType]}</span>
            </div>
            <div class="info-box-content">
                <strong>Target:</strong> ${formatCurrency(data.goalAmount)} (today's value) → ${formatCurrency(data.futureValue)} (in ${data.goalYears} years)<br>
                <strong>Inflation:</strong> ${formatPercentage(data.inflationRate * 100)} annually
                ${data.existingCorpus > 0 ? `<br><strong>Existing Corpus:</strong> ${formatCurrency(data.existingCorpus)} → ${formatCurrency(data.existingFutureValue)} (future value)` : ''}
            </div>
        </div>

        <!-- Required SIP -->
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Regular Monthly SIP</div>
                <div class="summary-value">${formatCurrency(data.requiredSIP)}</div>
                <div class="summary-sub">Fixed amount every month</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Step-up SIP (Start)</div>
                <div class="summary-value">${formatCurrency(data.stepUpSIP.initialMonthly)}</div>
                <div class="summary-sub">Increase 10% annually</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Step-up SIP (Final)</div>
                <div class="summary-value">${formatCurrency(data.stepUpSIP.finalMonthly)}</div>
                <div class="summary-sub">Year ${data.goalYears}</div>
            </div>
        </div>

        <!-- Comparison -->
        <div class="chart-container">
            <div class="chart-title">💰 Investment Strategies Comparison</div>
            <div id="goalChart"></div>
        </div>

        <!-- Alternative Strategies -->
        <div class="info-box">
            <div class="info-box-title">
                <span>💡</span>
                <span>Smart Investment Tips</span>
            </div>
            <div class="info-box-content">
                <strong>Regular SIP:</strong> Invest ${formatCurrency(data.requiredSIP)}/month for ${data.goalYears} years<br>
                <strong>Step-up SIP:</strong> Start with ${formatCurrency(data.stepUpSIP.initialMonthly)}/month, increase by 10% annually<br>
                <strong>Lumpsum + SIP:</strong> Invest ${formatCurrency(data.existingCorpus)} now + ${formatCurrency(data.requiredSIP * 0.8)}/month<br>
                <strong>Extend Timeline:</strong> ${data.goalYears + 3} years → Only ${formatCurrency(data.requiredSIP * 0.75)}/month needed
            </div>
        </div>

        <!-- Scenario Analysis -->
        <div class="chart-container">
            <div class="chart-title">📊 What If Analysis</div>
            <div class="comparison-table">
                <table>
                    <thead>
                        <tr>
                            <th>Scenario</th>
                            <th>Change</th>
                            <th>Required SIP</th>
                            <th>Impact</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Base Case</td>
                            <td>-</td>
                            <td>${formatCurrency(data.requiredSIP)}</td>
                            <td>-</td>
                        </tr>
                        <tr>
                            <td>Extend by 3 years</td>
                            <td>${data.goalYears} → ${data.goalYears + 3} years</td>
                            <td class="highlight">${formatCurrency(data.requiredSIP * 0.72)}</td>
                            <td><span class="benefit-badge">28% less</span></td>
                        </tr>
                        <tr>
                            <td>Higher returns</td>
                            <td>${formatPercentage(data.expectedReturn * 100)} → ${formatPercentage((data.expectedReturn + 0.03) * 100)}</td>
                            <td class="highlight">${formatCurrency(data.requiredSIP * 0.85)}</td>
                            <td><span class="benefit-badge">15% less</span></td>
                        </tr>
                        <tr>
                            <td>Reduce goal</td>
                            <td>${formatCurrency(data.goalAmount)} → ${formatCurrency(data.goalAmount * 0.8)}</td>
                            <td class="highlight">${formatCurrency(data.requiredSIP * 0.8)}</td>
                            <td><span class="benefit-badge">20% less</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;

    resultsCard.innerHTML = html;
    plotGoalChart(data);
    trackAnalytics('goal_based', { goal_type: data.goalType });
}

// ==================== RETIREMENT CALCULATOR ====================
function calculateRetirement() {
    const currentAge = parseInt(document.getElementById('currentAge').value);
    const retirementAge = parseInt(document.getElementById('retirementAge').value);
    const lifeExpectancy = parseInt(document.getElementById('lifeExpectancy').value);
    const monthlyExpenses = parseFloat(document.getElementById('monthlyExpenses').value);
    const expenseInflation = parseFloat(document.getElementById('expenseInflation').value) / 100;
    const preRetirementReturn = parseFloat(document.getElementById('preRetirementReturn').value) / 100;
    const postRetirementReturn = parseFloat(document.getElementById('postRetirementReturn').value) / 100;

    if (currentAge >= retirementAge) {
        alert('Retirement age must be greater than current age');
        return;
    }
    if (retirementAge >= lifeExpectancy) {
        alert('Life expectancy must be greater than retirement age');
        return;
    }

    const yearsToRetirement = retirementAge - currentAge;
    const yearsInRetirement = lifeExpectancy - retirementAge;

    // Calculate future monthly expenses at retirement
    const futureMonthlyExpenses = monthlyExpenses * Math.pow(1 + expenseInflation, yearsToRetirement);

    // Calculate corpus needed considering post-retirement inflation and returns
    // Using present value of annuity formula
    const monthlyRealReturn = (postRetirementReturn - expenseInflation) / 12;
    const monthsInRetirement = yearsInRetirement * 12;
    
    let corpusNeeded;
    if (Math.abs(monthlyRealReturn) < 0.0001) {
        // If real return is ~0, use simple multiplication
        corpusNeeded = futureMonthlyExpenses * monthsInRetirement;
    } else {
        corpusNeeded = futureMonthlyExpenses * ((1 - Math.pow(1 + monthlyRealReturn, -monthsInRetirement)) / monthlyRealReturn);
    }

    // Calculate required monthly SIP
    const months = yearsToRetirement * 12;
    const monthlyRate = preRetirementReturn / 12;
    const requiredSIP = corpusNeeded * monthlyRate / ((Math.pow(1 + monthlyRate, months) - 1) * (1 + monthlyRate));

    // Calculate with step-up
    const stepUpSIP = calculateRequiredStepUpSIP(corpusNeeded, yearsToRetirement, preRetirementReturn, 0.10);

    // Calculate SWP (Systematic Withdrawal Plan)
    const withdrawalRate = 0.04; // 4% rule
    const sustainableWithdrawal = (corpusNeeded * withdrawalRate) / 12;

    displayRetirementResults({
        currentAge,
        retirementAge,
        lifeExpectancy,
        yearsToRetirement,
        yearsInRetirement,
        monthlyExpenses,
        futureMonthlyExpenses,
        corpusNeeded,
        requiredSIP,
        stepUpSIP,
        sustainableWithdrawal,
        expenseInflation,
        preRetirementReturn,
        postRetirementReturn
    });
}

function displayRetirementResults(data) {
    const resultsCard = document.getElementById('resultsCard');

    let html = `
        <h2 class="card-title">🏖️ Retirement Investment Plan</h2>
        
        <!-- Retirement Overview -->
        <div class="info-box">
            <div class="info-box-title">
                <span>🎯</span>
                <span>Your Retirement Journey</span>
            </div>
            <div class="info-box-content">
                <strong>Current Age:</strong> ${data.currentAge} years<br>
                <strong>Years to Retirement:</strong> ${data.yearsToRetirement} years (retire at ${data.retirementAge})<br>
                <strong>Retirement Duration:</strong> ${data.yearsInRetirement} years (till age ${data.lifeExpectancy})<br>
                <strong>Monthly Expenses Today:</strong> ${formatCurrency(data.monthlyExpenses)}<br>
                <strong>Monthly Expenses at Retirement:</strong> ${formatCurrency(data.futureMonthlyExpenses)}
            </div>
        </div>

        <!-- Corpus Required -->
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Corpus Needed</div>
                <div class="summary-value">${formatCurrency(data.corpusNeeded)}</div>
                <div class="summary-sub">At retirement age ${data.retirementAge}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Monthly SIP Required</div>
                <div class="summary-value">${formatCurrency(data.requiredSIP)}</div>
                <div class="summary-sub">For ${data.yearsToRetirement} years</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Or Step-up SIP (Start)</div>
                <div class="summary-value">${formatCurrency(data.stepUpSIP.initialMonthly)}</div>
                <div class="summary-sub">Increase 10% annually</div>
            </div>
        </div>

        <!-- Investment Timeline -->
        <div class="chart-container">
            <div class="chart-title">📊 Retirement Corpus Growth</div>
            <div id="retirementChart"></div>
        </div>

        <!-- Post-Retirement Strategy -->
        <div class="info-box">
            <div class="info-box-title">
                <span>💰</span>
                <span>Post-Retirement Withdrawal Strategy</span>
            </div>
            <div class="info-box-content">
                <strong>Corpus at Retirement:</strong> ${formatCurrency(data.corpusNeeded)}<br>
                <strong>Recommended Withdrawal:</strong> ${formatCurrency(data.sustainableWithdrawal)}/month (4% annual rule)<br>
                <strong>Duration:</strong> Sustainable for ${data.yearsInRetirement}+ years<br>
                <strong>Strategy:</strong> Keep corpus in balanced funds with ${formatPercentage(data.postRetirementReturn * 100)} expected return
            </div>
        </div>

        <!-- Investment Options -->
        <div class="chart-container">
            <div class="chart-title">🎯 Investment Strategy Options</div>
            <div class="comparison-table">
                <table>
                    <thead>
                        <tr>
                            <th>Strategy</th>
                            <th>Monthly Investment</th>
                            <th>Total Invested</th>
                            <th>Corpus at Retirement</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Regular SIP</strong></td>
                            <td class="highlight">${formatCurrency(data.requiredSIP)}</td>
                            <td>${formatCurrency(data.requiredSIP * data.yearsToRetirement * 12)}</td>
                            <td>${formatCurrency(data.corpusNeeded)}</td>
                        </tr>
                        <tr>
                            <td><strong>Step-up SIP (10%)</strong></td>
                            <td class="highlight">${formatCurrency(data.stepUpSIP.initialMonthly)} → ${formatCurrency(data.stepUpSIP.finalMonthly)}</td>
                            <td>${formatCurrency(data.stepUpSIP.totalInvested)}</td>
                            <td>${formatCurrency(data.corpusNeeded)}</td>
                        </tr>
                        <tr>
                            <td><strong>Aggressive (15% return)</strong></td>
                            <td class="highlight">${formatCurrency(data.requiredSIP * 0.78)}</td>
                            <td>${formatCurrency(data.requiredSIP * 0.78 * data.yearsToRetirement * 12)}</td>
                            <td>${formatCurrency(data.corpusNeeded)}</td>
                        </tr>
                        <tr>
                            <td><strong>Delayed Retirement (+3 years)</strong></td>
                            <td class="highlight">${formatCurrency(data.requiredSIP * 0.68)}</td>
                            <td>${formatCurrency(data.requiredSIP * 0.68 * (data.yearsToRetirement + 3) * 12)}</td>
                            <td>${formatCurrency(data.corpusNeeded)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Risk Mitigation -->
        <div class="info-box">
            <div class="info-box-title">
                <span>⚠️</span>
                <span>Important Considerations</span>
            </div>
            <div class="info-box-content">
                <strong>Healthcare:</strong> Add ₹20-30L for medical emergencies in retirement<br>
                <strong>Inflation Protection:</strong> Keep some allocation in equity even post-retirement<br>
                <strong>Emergency Buffer:</strong> Maintain 2-3 years expenses in liquid funds<br>
                <strong>Review Annually:</strong> Adjust SIP with salary increases and market conditions
            </div>
        </div>
    `;

    resultsCard.innerHTML = html;
    plotRetirementChart(data);
    trackAnalytics('retirement_plan', { years_to_retirement: data.yearsToRetirement });
}

// ==================== CHARTING FUNCTIONS ====================
function plotGrowthChart(regularSIP, stepUpSIP, scenarios) {
    const traces = [];

    // Regular SIP - Invested amount
    traces.push({
        x: regularSIP.yearlyData.map(d => `Year ${d.year}`),
        y: regularSIP.yearlyData.map(d => d.invested),
        name: 'Invested (Regular)',
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#F59E0B', width: 2, dash: 'dot' },
        marker: { size: 6 }
    });

    // Regular SIP - Portfolio value
    traces.push({
        x: regularSIP.yearlyData.map(d => `Year ${d.year}`),
        y: regularSIP.yearlyData.map(d => d.value),
        name: 'Portfolio Value (Regular)',
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#7FC04C', width: 3 },
        marker: { size: 8 }
    });

    if (stepUpSIP) {
        // Step-up SIP - Invested amount
        traces.push({
            x: stepUpSIP.yearlyData.map(d => `Year ${d.year}`),
            y: stepUpSIP.yearlyData.map(d => d.invested),
            name: 'Invested (Step-up)',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#EF4444', width: 2, dash: 'dot' },
            marker: { size: 6 }
        });

        // Step-up SIP - Portfolio value
        traces.push({
            x: stepUpSIP.yearlyData.map(d => `Year ${d.year}`),
            y: stepUpSIP.yearlyData.map(d => d.value),
            name: 'Portfolio Value (Step-up)',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#10B981', width: 3 },
            marker: { size: 8 }
        });
    }

    const layout = {
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.2,
            x: 0.5,
            xanchor: 'center'
        },
        xaxis: {
            title: 'Investment Period',
            gridcolor: '#E5E7EB',
            color: '#6B7280'
        },
        yaxis: {
            title: 'Amount (Rs.)',
            gridcolor: '#E5E7EB',
            color: '#6B7280'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#111827' },
        hovermode: 'x unified',
        margin: { t: 20, b: 80, l: 80, r: 20 }
    };

    const config = { responsive: true, displayModeBar: false };

    Plotly.newPlot('growthChart', traces, layout, config);
}

function plotGoalChart(data) {
    const years = Array.from({ length: data.goalYears + 1 }, (_, i) => i);
    
    const regularSIPData = years.map(year => data.requiredSIP * 12 * year);
    const stepUpSIPData = years.map(year => {
        let invested = 0;
        let monthly = data.stepUpSIP.initialMonthly;
        for (let y = 0; y < year; y++) {
            invested += monthly * 12;
            monthly *= 1.1;
        }
        return invested;
    });

    const traces = [
        {
            x: years.map(y => `Year ${y}`),
            y: regularSIPData,
            name: 'Regular SIP (Invested)',
            type: 'bar',
            marker: { color: '#7FC04C' }
        },
        {
            x: years.map(y => `Year ${y}`),
            y: stepUpSIPData,
            name: 'Step-up SIP (Invested)',
            type: 'bar',
            marker: { color: '#10B981' }
        },
        {
            x: [`Year ${data.goalYears}`],
            y: [data.futureValue],
            name: 'Target Corpus',
            type: 'scatter',
            mode: 'markers',
            marker: { color: '#EF4444', size: 15, symbol: 'star' }
        }
    ];

    const layout = {
        barmode: 'group',
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.2,
            x: 0.5,
            xanchor: 'center'
        },
        xaxis: {
            title: 'Years',
            gridcolor: '#E5E7EB',
            color: '#6B7280'
        },
        yaxis: {
            title: 'Amount (Rs.)',
            gridcolor: '#E5E7EB',
            color: '#6B7280'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#111827' },
        margin: { t: 20, b: 80, l: 80, r: 20 }
    };

    const config = { responsive: true, displayModeBar: false };

    Plotly.newPlot('goalChart', traces, layout, config);
}

function plotRetirementChart(data) {
    const years = Array.from({ length: data.yearsToRetirement + 1 }, (_, i) => i);
    
    const sipInvested = years.map(year => data.requiredSIP * 12 * year);
    
    const corpusGrowth = years.map(year => {
        if (year === 0) return 0;
        const months = year * 12;
        const monthlyRate = data.preRetirementReturn / 12;
        let value = 0;
        for (let m = 1; m <= months; m++) {
            value = (value + data.requiredSIP) * (1 + monthlyRate);
        }
        return value;
    });

    const traces = [
        {
            x: years.map(y => data.currentAge + y),
            y: sipInvested,
            name: 'Total Invested',
            type: 'scatter',
            fill: 'tozeroy',
            line: { color: '#F59E0B', width: 2 }
        },
        {
            x: years.map(y => data.currentAge + y),
            y: corpusGrowth,
            name: 'Corpus Value',
            type: 'scatter',
            fill: 'tonexty',
            line: { color: '#7FC04C', width: 3 }
        },
        {
            x: [data.retirementAge],
            y: [data.corpusNeeded],
            name: 'Target Corpus',
            type: 'scatter',
            mode: 'markers',
            marker: { color: '#EF4444', size: 15, symbol: 'star' }
        }
    ];

    const layout = {
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.2,
            x: 0.5,
            xanchor: 'center'
        },
        xaxis: {
            title: 'Age (Years)',
            gridcolor: '#E5E7EB',
            color: '#6B7280'
        },
        yaxis: {
            title: 'Amount (Rs.)',
            gridcolor: '#E5E7EB',
            color: '#6B7280'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#111827' },
        hovermode: 'x unified',
        margin: { t: 20, b: 80, l: 80, r: 20 }
    };

    const config = { responsive: true, displayModeBar: false };

    Plotly.newPlot('retirementChart', traces, layout, config);
}

// ==================== ANALYTICS ====================
function trackAnalytics(eventName, params) {
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, {
            page: 'sip-calculator',
            ...params
        });
    }
}

// Calculate on page load with default values
window.addEventListener('load', () => {
    calculateSIP();
});
