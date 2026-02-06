/**
 * Goal Planning with Gamification - Interactive JavaScript
 * Drag & Drop functionality with financial projections
 */

const goalIcons = {
    baby: '👶',
    education: '🎓',
    wedding: '💍',
    bike: '🏍️',
    car: '🚗',
    house: '🏠',
    vacation: '✈️',
    retirement: '🏖️',
    custom: '🎯'
};

const goalDefaults = {
    baby: { name: 'New Baby', amount: 700000 },
    education: { name: 'Child Education', amount: 2000000 },
    wedding: { name: 'Wedding', amount: 3000000 },
    bike: { name: 'Bike/Scooty', amount: 150000 },
    car: { name: 'Car', amount: 1500000 },
    house: { name: 'House/Flat', amount: 5000000 },
    vacation: { name: 'Dream Vacation', amount: 300000 },
    retirement: { name: 'Retirement', amount: 10000000 },
    custom: { name: 'Custom Goal', amount: 500000 }
};

let placedGoals = [];
let draggedGoal = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeDragAndDrop();
    updateTimelineRuler();
    updateAgeInputListeners();
});

function initializeDragAndDrop() {
    const goalItems = document.querySelectorAll('.goal-item');
    const timelineArea = document.getElementById('timelineArea');
    const timelineTrack = document.getElementById('timelineTrack');
    
    // Make goal items draggable
    goalItems.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
    });
    
    // Setup drop zone
    timelineArea.addEventListener('dragover', handleDragOver);
    timelineArea.addEventListener('drop', handleDrop);
    timelineArea.addEventListener('dragleave', handleDragLeave);
    timelineTrack.addEventListener('dragover', handleDragOver);
    timelineTrack.addEventListener('drop', handleDrop);
}

function handleDragStart(e) {
    draggedGoal = {
        type: this.dataset.goalType,
        icon: goalIcons[this.dataset.goalType],
        name: goalDefaults[this.dataset.goalType].name,
        amount: goalDefaults[this.dataset.goalType].amount
    };
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'copy';
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    document.getElementById('timelineArea').classList.add('drag-over');
}

function handleDragLeave(e) {
    if (e.target.id === 'timelineArea') {
        document.getElementById('timelineArea').classList.remove('drag-over');
    }
}

function handleDrop(e) {
    e.preventDefault();
    document.getElementById('timelineArea').classList.remove('drag-over');
    
    if (!draggedGoal) return;
    
    // Calculate age based on drop position
    const trackRect = document.getElementById('timelineTrack').getBoundingClientRect();
    const dropX = e.clientX - trackRect.left;
    const dropPercent = (dropX / trackRect.width) * 100;
    
    const currentAge = parseInt(document.getElementById('currentAge').value);
    const targetAge = parseInt(document.getElementById('targetAge').value);
    const ageRange = targetAge - currentAge;
    const goalAge = Math.round(currentAge + (ageRange * dropPercent / 100));
    
    // Prompt for amount if custom goal
    let amount = draggedGoal.amount;
    let name = draggedGoal.name;
    
    if (draggedGoal.type === 'custom') {
        name = prompt('Enter goal name:', 'My Goal') || 'Custom Goal';
        amount = parseInt(prompt('Enter goal amount (₹):', '500000')) || 500000;
    }
    
    // Create goal object
    const goal = {
        id: Date.now(),
        type: draggedGoal.type,
        icon: draggedGoal.icon,
        name: name,
        age: goalAge,
        amount: amount,
        position: dropPercent
    };
    
    placedGoals.push(goal);
    renderPlacedGoals();
    updateEmptyState();
    
    // Track event
    if (typeof trackFeatureUsage !== 'undefined') {
        trackFeatureUsage('goal_added', { goal_type: goal.type, age: goal.age });
    }
    
    draggedGoal = null;
}

function renderPlacedGoals() {
    const track = document.getElementById('timelineTrack');
    const existingGoals = track.querySelectorAll('.placed-goal');
    existingGoals.forEach(g => g.remove());
    
    placedGoals.forEach(goal => {
        const goalEl = document.createElement('div');
        goalEl.className = 'placed-goal';
        goalEl.style.left = `${goal.position}%`;
        goalEl.style.transform = 'translateX(-50%)';
        
        goalEl.innerHTML = `
            <div class="placed-goal-icon">${goal.icon}</div>
            <div class="placed-goal-info">
                <div class="placed-goal-name">${goal.name}</div>
                <div class="placed-goal-age">Age ${goal.age} | ₹${formatAmount(goal.amount)}</div>
            </div>
            <button class="remove-goal" onclick="removeGoal(${goal.id})">×</button>
        `;
        
        track.appendChild(goalEl);
    });
}

function removeGoal(goalId) {
    placedGoals = placedGoals.filter(g => g.id !== goalId);
    renderPlacedGoals();
    updateEmptyState();
    
    // Track event
    if (typeof trackFeatureUsage !== 'undefined') {
        trackFeatureUsage('goal_removed');
    }
}

function updateTimelineRuler() {
    const currentAge = parseInt(document.getElementById('currentAge').value);
    const targetAge = parseInt(document.getElementById('targetAge').value);
    const ruler = document.getElementById('timelineRuler');
    
    ruler.innerHTML = '';
    
    const steps = 6;
    const ageRange = targetAge - currentAge;
    
    for (let i = 0; i <= steps; i++) {
        const age = Math.round(currentAge + (ageRange * i / steps));
        const marker = document.createElement('div');
        marker.className = 'age-marker';
        marker.textContent = `Age ${age}`;
        ruler.appendChild(marker);
    }
}

function updateAgeInputListeners() {
    document.getElementById('currentAge').addEventListener('change', () => {
        updateTimelineRuler();
        repositionGoals();
    });
    
    document.getElementById('targetAge').addEventListener('change', () => {
        updateTimelineRuler();
        repositionGoals();
    });
}

function repositionGoals() {
    const currentAge = parseInt(document.getElementById('currentAge').value);
    const targetAge = parseInt(document.getElementById('targetAge').value);
    
    placedGoals.forEach(goal => {
        const ageOffset = goal.age - currentAge;
        const ageRange = targetAge - currentAge;
        goal.position = (ageOffset / ageRange) * 100;
    });
    
    renderPlacedGoals();
}

function updateEmptyState() {
    const emptyState = document.getElementById('emptyState');
    if (placedGoals.length > 0) {
        emptyState.style.display = 'none';
    } else {
        emptyState.style.display = 'block';
    }
}

function calculateProjection() {
    if (placedGoals.length === 0) {
        alert('Please add some goals to your timeline first!');
        return;
    }
    
    const currentAge = parseInt(document.getElementById('currentAge').value);
    const targetAge = parseInt(document.getElementById('targetAge').value);
    const currentSavings = parseFloat(document.getElementById('currentSavings').value) || 0;
    const monthlyInvestment = parseFloat(document.getElementById('monthlyInvestment').value) || 0;
    const returnRate = parseFloat(document.getElementById('expectedReturn').value) || 12;
    
    // Sort goals by age
    const sortedGoals = [...placedGoals].sort((a, b) => a.age - b.age);
    
    // Calculate year-by-year projection
    const projectionData = [];
    let currentValue = currentSavings;
    let totalInvested = currentSavings;
    let totalGoalAmount = 0;
    let totalWithdrawn = 0;
    
    for (let age = currentAge; age <= targetAge; age++) {
        const year = age - currentAge;
        
        // Add monthly investments
        const yearlyInvestment = monthlyInvestment * 12;
        currentValue += yearlyInvestment;
        totalInvested += yearlyInvestment;
        
        // Apply returns
        currentValue = currentValue * (1 + returnRate / 100);
        
        // Check for goals at this age
        const goalsThisYear = sortedGoals.filter(g => g.age === age);
        let withdrawalThisYear = 0;
        
        goalsThisYear.forEach(goal => {
            withdrawalThisYear += goal.amount;
            totalGoalAmount += goal.amount;
        });
        
        // Withdraw for goals
        currentValue -= withdrawalThisYear;
        totalWithdrawn += withdrawalThisYear;
        
        // Ensure non-negative
        if (currentValue < 0) currentValue = 0;
        
        projectionData.push({
            age: age,
            value: currentValue,
            invested: totalInvested,
            withdrawn: withdrawalThisYear,
            goals: goalsThisYear.length,
            goalsText: goalsThisYear.map(g => `${g.icon} ${g.name}`).join(', ')
        });
    }
    
    // Render chart
    renderProjectionChart(projectionData);
    
    // Update summary
    updateSummary(totalInvested, totalGoalAmount, totalWithdrawn, projectionData[projectionData.length - 1].value);
    
    // Track event
    if (typeof trackFeatureUsage !== 'undefined') {
        trackFeatureUsage('projection_calculated', {
            goals_count: placedGoals.length,
            years: targetAge - currentAge
        });
    }
}

function renderProjectionChart(data) {
    const ages = data.map(d => `Age ${d.age}`);
    const values = data.map(d => d.value);
    const invested = data.map(d => d.invested);
    
    // Create annotations for goals
    const annotations = [];
    data.forEach((d, i) => {
        if (d.goals > 0) {
            annotations.push({
                x: `Age ${d.age}`,
                y: d.value,
                text: d.goalsText,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: '#f72585',
                ax: 0,
                ay: -40,
                bgcolor: 'rgba(247,37,133,0.9)',
                bordercolor: '#f72585',
                borderwidth: 2,
                borderpad: 4,
                font: { color: 'white', size: 10 }
            });
        }
    });
    
    const trace1 = {
        x: ages,
        y: values,
        name: 'Portfolio Value',
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: '#00d4ff',
            width: 3
        },
        marker: {
            size: 8,
            color: '#00d4ff'
        },
        fill: 'tozeroy',
        fillcolor: 'rgba(0,212,255,0.1)'
    };
    
    const trace2 = {
        x: ages,
        y: invested,
        name: 'Total Invested',
        type: 'scatter',
        mode: 'lines',
        line: {
            color: '#7b2cbf',
            width: 2,
            dash: 'dash'
        }
    };
    
    const layout = {
        title: {
            text: '💰 Your Financial Journey with Goals',
            font: { color: 'white', size: 18 }
        },
        xaxis: {
            title: 'Age',
            color: 'white',
            gridcolor: 'rgba(255,255,255,0.1)'
        },
        yaxis: {
            title: 'Amount (₹)',
            color: 'white',
            gridcolor: 'rgba(255,255,255,0.1)',
            tickformat: ',.0f'
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { color: 'white' },
        annotations: annotations,
        legend: {
            font: { color: 'white' },
            bgcolor: 'rgba(0,0,0,0.3)'
        },
        hovermode: 'x unified'
    };
    
    const config = {
        responsive: true,
        displayModeBar: false
    };
    
    Plotly.newPlot('goalChart', [trace1, trace2], layout, config);
}

function updateSummary(totalInvested, totalGoals, totalWithdrawn, finalValue) {
    const summaryContainer = document.getElementById('goalsSummary');
    
    const returns = finalValue + totalWithdrawn - totalInvested;
    const returnPercent = (returns / totalInvested * 100).toFixed(1);
    
    summaryContainer.innerHTML = `
        <div class="summary-card">
            <h3>💰 Total Investment</h3>
            <div class="summary-value">₹${formatAmount(totalInvested)}</div>
        </div>
        <div class="summary-card">
            <h3>🎯 Total Goals</h3>
            <div class="summary-value">₹${formatAmount(totalGoals)}</div>
        </div>
        <div class="summary-card">
            <h3>📈 Total Returns</h3>
            <div class="summary-value">₹${formatAmount(returns)}</div>
            <p style="font-size: 0.9rem; margin-top: 5px; opacity: 0.8;">${returnPercent}% gain</p>
        </div>
        <div class="summary-card">
            <h3>💵 Final Value</h3>
            <div class="summary-value">₹${formatAmount(finalValue)}</div>
        </div>
    `;
}

function formatAmount(amount) {
    if (amount >= 10000000) {
        return (amount / 10000000).toFixed(2) + ' Cr';
    } else if (amount >= 100000) {
        return (amount / 100000).toFixed(2) + ' L';
    } else {
        return amount.toLocaleString('en-IN');
    }
}
