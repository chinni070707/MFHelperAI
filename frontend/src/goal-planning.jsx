import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import * as d3 from 'd3';

// SVG Icon Components for Goals
const goalIconData = {
    house: {
        color: '#10b981',
        bgColor: 'rgba(16, 185, 129, 0.2)',
        path: 'M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'
    },
    vehicle: {
        color: '#3b82f6',
        bgColor: 'rgba(59, 130, 246, 0.2)',
        path: 'M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2M7 17a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM17 17a2 2 0 1 0 0-4 2 2 0 0 0 0 4z'
    },
    education: {
        color: '#8b5cf6',
        bgColor: 'rgba(139, 92, 246, 0.2)',
        path: 'M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.084a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0zM22 10v6M6 12.5V16a6 3 0 0 0 12 0v-3.5'
    },
    marriage: {
        color: '#ec4899',
        bgColor: 'rgba(236, 72, 153, 0.2)',
        path: 'M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z'
    },
    vacation: {
        color: '#f59e0b',
        bgColor: 'rgba(245, 158, 11, 0.2)',
        path: 'M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z'
    },
    business: {
        color: '#6366f1',
        bgColor: 'rgba(99, 102, 241, 0.2)',
        path: 'M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16M2 6h20v14H2zM2 14h20'
    },
    emergency: {
        color: '#ef4444',
        bgColor: 'rgba(239, 68, 68, 0.2)',
        path: 'M12 6v4M14 14h-4M14 18h-4M14 8h-4M18 12h2a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2h2M18 22V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v18'
    },
    custom: {
        color: '#14b8a6',
        bgColor: 'rgba(20, 184, 166, 0.2)',
        path: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM12 6a6 6 0 1 0 0 12 6 6 0 0 0 0-12zM12 10a2 2 0 1 0 0 4 2 2 0 0 0 0-4z'
    },
    expense: {
        color: '#f97316',
        bgColor: 'rgba(249, 115, 22, 0.2)',
        path: 'M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'
    }
};

// Goal Icon Component
function GoalIcon({ iconType, size = 28, className = '' }) {
    const iconInfo = goalIconData[iconType] || goalIconData.custom;
    const containerSize = size + 20;
    
    return (
        <div 
            className={`goal-icon-container ${className}`}
            style={{
                width: containerSize,
                height: containerSize,
                borderRadius: '50%',
                background: iconInfo.bgColor,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.3s ease'
            }}
        >
            <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width={size} 
                height={size} 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke={iconInfo.color}
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
            >
                <path d={iconInfo.path} />
            </svg>
        </div>
    );
}

// Helper to get emoji fallback for D3 chart
const iconTypeToEmoji = {
    house: '🏠',
    vehicle: '🚗',
    education: '🎓',
    marriage: '💍',
    vacation: '🌴',
    business: '💼',
    emergency: '🏥',
    custom: '✨',
    expense: '💸'
};

function FinancialPlanner() {
    // State
    const [currentAge, setCurrentAge] = useState(30);
    const [currentNetworth, setCurrentNetworth] = useState(3000000);
    const [growthRate, setGrowthRate] = useState(8);
    const [inflationRate, setInflationRate] = useState(6);
    const [retirementAge, setRetirementAge] = useState(60);
    const [retirementExpense, setRetirementExpense] = useState(100000);
    const [lifeEndAge, setLifeEndAge] = useState(80);
    const [goals, setGoals] = useState([]);
    const [sips, setSips] = useState([]);
    const [lumpsums, setLumpsums] = useState([]);
    const [showGoalPopup, setShowGoalPopup] = useState(false);
    const [clickedAge, setClickedAge] = useState(null);
    const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 });
    const [scenario, setScenario] = useState('medium');
    const [draggedTemplate, setDraggedTemplate] = useState(null);
    const [dropAge, setDropAge] = useState(null);
    const [isDraggingOver, setIsDraggingOver] = useState(false);
    
    // Input Modal State
    const [inputModal, setInputModal] = useState({
        show: false,
        title: '',
        fields: [],
        onSubmit: null,
        onCancel: null
    });
    
    const showInputModal = (config) => {
        setInputModal({
            show: true,
            title: config.title || 'Enter Details',
            fields: config.fields || [],
            onSubmit: config.onSubmit,
            onCancel: config.onCancel || (() => setInputModal(prev => ({...prev, show: false})))
        });
    };
    
    const closeInputModal = () => {
        setInputModal(prev => ({...prev, show: false}));
    };
    
    // Confirm Modal State
    const [confirmModal, setConfirmModal] = useState({
        show: false,
        title: '',
        message: '',
        onConfirm: null,
        onCancel: null
    });
    
    const showConfirmModal = (config) => {
        setConfirmModal({
            show: true,
            title: config.title || 'Confirm',
            message: config.message || 'Are you sure?',
            onConfirm: config.onConfirm,
            onCancel: config.onCancel || (() => setConfirmModal(prev => ({...prev, show: false})))
        });
    };
    
    const closeConfirmModal = () => {
        setConfirmModal(prev => ({...prev, show: false}));
    };
    
    const svgRef = useRef(null);
    const containerRef = useRef(null);
    
    // Chart dimensions
    const width = 900;
    const height = 500;
    const margin = { top: 40, right: 40, bottom: 60, left: 80 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    // Get scenario-based growth rate
    const getScenarioGrowthRate = () => {
        if (scenario === 'optimistic') return 14;
        if (scenario === 'pessimistic') return 8;
        return 12; // medium
    };
    
    // Calculate wealth projection
    const calculateProjection = () => {
        const projection = [];
        let wealth = currentNetworth;
        const effectiveGrowthRate = getScenarioGrowthRate();
        
        for (let age = currentAge; age <= lifeEndAge; age++) {
            wealth = wealth * (1 + effectiveGrowthRate / 100);
            
            sips.forEach(sip => {
                if (age >= sip.startAge && age <= sip.endAge) {
                    wealth += sip.amount * 12;
                }
            });
            
            lumpsums.forEach(lump => {
                if (age === lump.age) {
                    wealth += lump.amount;
                }
            });
            
            goals.forEach(goal => {
                if (age === goal.age) {
                    wealth -= goal.amount;
                }
            });
            
            if (age >= retirementAge) {
                const yearlyExpense = retirementExpense * 12;
                wealth -= yearlyExpense * Math.pow(1 + inflationRate / 100, age - retirementAge);
            }
            
            projection.push({ age, wealth: Math.max(0, wealth) });
            
            if (wealth <= 0) break;
        }
        
        return projection;
    };
    
    const projection = calculateProjection();
    const peakWealth = Math.max(...projection.map(p => p.wealth));
    const wealthAtRetirement = projection.find(p => p.age === retirementAge)?.wealth || 0;
    const moneyRunsOutAge = projection.find(p => p.wealth <= 0)?.age || (projection.length > 0 ? projection[projection.length - 1].age : lifeEndAge);
    
    // Format currency
    const formatCurrency = (amount) => {
        if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
        if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)} L`;
        if (amount >= 1000) return `₹${(amount / 1000).toFixed(2)} K`;
        return `₹${amount.toLocaleString('en-IN')}`;
    };
    
    // D3 Visualization
    useEffect(() => {
        if (!svgRef.current || projection.length === 0) return;
        
        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();
        
        const xScale = d3.scaleLinear()
            .domain([currentAge, lifeEndAge])
            .range([0, innerWidth]);
        
        const maxWealth = Math.max(peakWealth, currentNetworth * 2);
        const yScale = d3.scaleLinear()
            .domain([0, maxWealth])
            .range([innerHeight, 0]);
        
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // Invisible rectangle for click detection
        g.append('rect')
            .attr('width', innerWidth)
            .attr('height', innerHeight)
            .attr('fill', 'transparent')
            .style('cursor', 'crosshair')
            .on('mousemove', function(event) {
                const [mouseX] = d3.pointer(event);
                const age = Math.round(xScale.invert(mouseX));
                
                if (age >= currentAge && age <= lifeEndAge) {
                    g.selectAll('.hover-line').remove();
                    
                    g.append('line')
                        .attr('class', 'hover-line')
                        .attr('x1', xScale(age))
                        .attr('x2', xScale(age))
                        .attr('y1', 0)
                        .attr('y2', innerHeight)
                        .attr('stroke', '#3b82f6')
                        .attr('stroke-width', 1)
                        .attr('stroke-dasharray', '4,4')
                        .attr('opacity', 0.5);
                    
                    g.append('text')
                        .attr('class', 'hover-line')
                        .attr('x', xScale(age))
                        .attr('y', -5)
                        .attr('text-anchor', 'middle')
                        .attr('fill', '#3b82f6')
                        .attr('font-size', '14px')
                        .attr('font-weight', 'bold')
                        .text(`Age ${age}`);
                }
            })
            .on('mouseout', function() {
                g.selectAll('.hover-line').remove();
            })
            .on('click', function(event) {
                const [mouseX, mouseY] = d3.pointer(event);
                const age = Math.round(xScale.invert(mouseX));
                
                if (age >= currentAge && age <= lifeEndAge) {
                    const svgRect = svgRef.current.getBoundingClientRect();
                    const containerRect = containerRef.current.getBoundingClientRect();
                    const clickX = event.clientX - containerRect.left;
                    const clickY = event.clientY - containerRect.top;
                    
                    setClickedAge(age);
                    setPopupPosition({ x: clickX, y: clickY });
                    setShowGoalPopup(true);
                }
            });
        
        // Gradient
        const gradient = svg.append('defs')
            .append('linearGradient')
            .attr('id', 'wealthGradient')
            .attr('x1', '0%')
            .attr('y1', '0%')
            .attr('x2', '0%')
            .attr('y2', '100%');
        
        gradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#7FC04C')
            .attr('stop-opacity', 0.6);
        
        gradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#7FC04C')
            .attr('stop-opacity', 0.1);
        
        // Grid lines
        const yTicks = yScale.ticks(8);
        g.selectAll('.grid-line')
            .data(yTicks)
            .enter()
            .append('line')
            .attr('class', 'grid-line')
            .attr('x1', 0)
            .attr('x2', innerWidth)
            .attr('y1', d => yScale(d))
            .attr('y2', d => yScale(d));
        
        // Retirement line
        g.append('line')
            .attr('x1', xScale(retirementAge))
            .attr('x2', xScale(retirementAge))
            .attr('y1', 0)
            .attr('y2', innerHeight)
            .attr('stroke', '#f59e0b')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '8,4');
        
        g.append('text')
            .attr('x', xScale(retirementAge))
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .attr('fill', '#f59e0b')
            .attr('font-weight', 'bold')
            .attr('font-size', '12px')
            .text(`🏖️ Retirement ${retirementAge}`);
        
        // Drop indicator line (when dragging)
        if (dropAge && draggedTemplate) {
            g.append('line')
                .attr('class', 'drop-indicator-line')
                .attr('x1', xScale(dropAge))
                .attr('x2', xScale(dropAge))
                .attr('y1', 0)
                .attr('y2', innerHeight)
                .attr('stroke', '#3b82f6')
                .attr('stroke-width', 3)
                .attr('stroke-dasharray', '10,5')
                .style('filter', 'drop-shadow(0 0 8px #3b82f6)');
            
            g.append('text')
                .attr('class', 'drop-indicator-line')
                .attr('x', xScale(dropAge))
                .attr('y', -25)
                .attr('text-anchor', 'middle')
                .attr('fill', '#3b82f6')
                .attr('font-weight', 'bold')
                .attr('font-size', '14px')
                .text(`Drop at Age ${dropAge}`);
            
            g.append('text')
                .attr('class', 'drop-indicator-line')
                .attr('x', xScale(dropAge))
                .attr('y', innerHeight / 2)
                .attr('text-anchor', 'middle')
                .attr('font-size', '48px')
                .text(iconTypeToEmoji[draggedTemplate.iconType] || '⭐')
                .style('opacity', 0.6);
        }
        
        // Area under curve
        const area = d3.area()
            .x(d => xScale(d.age))
            .y0(innerHeight)
            .y1(d => yScale(d.wealth))
            .curve(d3.curveMonotoneX);
        
        g.append('path')
            .datum(projection)
            .attr('class', 'wealth-area')
            .attr('d', area);
        
        // Wealth curve
        const line = d3.line()
            .x(d => xScale(d.age))
            .y(d => yScale(d.wealth))
            .curve(d3.curveMonotoneX);
        
        g.append('path')
            .datum(projection)
            .attr('class', 'wealth-curve')
            .attr('d', line);
        
        // X Axis
        const xAxis = d3.axisBottom(xScale)
            .ticks(10)
            .tickFormat(d => d);
        
        g.append('g')
            .attr('transform', `translate(0,${innerHeight})`)
            .call(xAxis)
            .attr('color', 'rgba(0,0,0,0.5)');
        
        g.append('text')
            .attr('x', innerWidth / 2)
            .attr('y', innerHeight + 45)
            .attr('text-anchor', 'middle')
            .attr('fill', '#495057')
            .attr('font-weight', 'bold')
            .text('Age (Years)');
        
        // Y Axis
        const yAxis = d3.axisLeft(yScale)
            .ticks(8)
            .tickFormat(d => formatCurrency(d));
        
        g.append('g')
            .call(yAxis)
            .attr('color', 'rgba(0,0,0,0.5)');
        
        g.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -innerHeight / 2)
            .attr('y', -60)
            .attr('text-anchor', 'middle')
            .attr('fill', '#495057')
            .attr('font-weight', 'bold')
            .text('Net Worth');
        
        // Goal markers
        goals.forEach((goal) => {
            const goalData = projection.find(p => p.age === goal.age);
            if (!goalData) return;
            
            const goalG = g.append('g')
                .attr('class', 'goal-marker')
                .attr('transform', `translate(${xScale(goal.age)},${yScale(goalData.wealth)})`)
                .style('cursor', 'grab');
            
            goalG.append('circle')
                .attr('r', 24)
                .attr('fill', 'rgba(247, 37, 133, 0.9)')
                .attr('stroke', 'white')
                .attr('stroke-width', 3);
            
            goalG.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .attr('font-size', '20px')
                .text(iconTypeToEmoji[goal.iconType] || '⭐');
            
            goalG.append('title')
                .text(`${goal.name}\n${formatCurrency(goal.amount)}\nAge ${goal.age}`);
        });
        
    }, [projection, goals, retirementAge, currentAge, lifeEndAge, dropAge, draggedTemplate]);
    
    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyPress = (e) => {
            if (e.key === 'Escape' && showGoalPopup) {
                setShowGoalPopup(false);
            }
        };
        
        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, [showGoalPopup]);
    
    const goalTemplates = [
        { iconType: 'house', name: 'House Purchase', defaultAmount: 5000000 },
        { iconType: 'vehicle', name: 'Vehicle', defaultAmount: 1000000 },
        { iconType: 'education', name: 'Education', defaultAmount: 2500000 },
        { iconType: 'marriage', name: 'Marriage', defaultAmount: 1500000 },
        { iconType: 'vacation', name: 'Vacation', defaultAmount: 500000 },
        { iconType: 'business', name: 'Business', defaultAmount: 5000000 },
        { iconType: 'emergency', name: 'Emergency', defaultAmount: 1000000 },
        { iconType: 'custom', name: 'Custom', defaultAmount: 1000000 }
    ];
    
    const addGoalFromPopup = (template, amount) => {
        if (!amount || amount <= 0 || !clickedAge) return;
        
        setGoals([...goals, {
            iconType: template.iconType,
            name: template.name,
            amount: parseFloat(amount),
            age: clickedAge
        }]);
        
        setShowGoalPopup(false);
        setClickedAge(null);
    };
    
    const addIncome = (amount) => {
        if (!amount || amount <= 0 || !clickedAge) return;
        
        setLumpsums([...lumpsums, { amount: parseFloat(amount), age: clickedAge }]);
        setShowGoalPopup(false);
        setClickedAge(null);
    };
    
    const addExpense = (amount, name = 'Expense') => {
        if (!amount || amount <= 0 || !clickedAge) return;
        
        setGoals([...goals, {
            iconType: 'expense',
            name: name,
            amount: parseFloat(amount),
            age: clickedAge
        }]);
        
        setShowGoalPopup(false);
        setClickedAge(null);
    };
    
    const deleteGoal = (index) => {
        showConfirmModal({
            title: '🗑️ Delete Goal',
            message: 'Are you sure you want to delete this goal?',
            onConfirm: () => {
                setGoals(goals.filter((_, i) => i !== index));
            }
        });
    };
    
    // Drag and drop handlers
    const handleDragStart = (template) => {
        setDraggedTemplate(template);
    };
    
    const handleDragEnd = () => {
        setDraggedTemplate(null);
        setDropAge(null);
        setIsDraggingOver(false);
    };
    
    const handleDragOver = (e, age) => {
        e.preventDefault();
        setDropAge(age);
        setIsDraggingOver(true);
    };
    
    const handleDragLeave = () => {
        setIsDraggingOver(false);
    };
    
    const handleDrop = (e, age) => {
        e.preventDefault();
        setIsDraggingOver(false);
        
        if (!draggedTemplate || !age) return;
        
        const template = draggedTemplate;
        showInputModal({
            title: `🎯 Add ${template.name} at Age ${age}`,
            fields: [
                {
                    name: 'amount',
                    label: 'Amount (₹)',
                    type: 'number',
                    defaultValue: template.defaultAmount,
                    placeholder: 'Enter amount'
                }
            ],
            onSubmit: (values) => {
                const amount = parseFloat(values.amount);
                if (amount && amount > 0) {
                    const newGoal = {
                        iconType: template.iconType,
                        name: template.name,
                        amount: amount,
                        age: age
                    };
                    setGoals([...goals, newGoal]);
                }
                setDraggedTemplate(null);
                setDropAge(null);
            }
        });
    };
    
    const addSIP = () => {
        showInputModal({
            title: '📈 Add Monthly SIP',
            fields: [
                {
                    name: 'amount',
                    label: 'Monthly SIP Amount (₹)',
                    type: 'number',
                    defaultValue: '10000',
                    placeholder: 'Enter monthly amount'
                },
                {
                    name: 'startAge',
                    label: 'Start Age',
                    type: 'number',
                    defaultValue: currentAge.toString(),
                    placeholder: 'Age to start SIP'
                },
                {
                    name: 'endAge',
                    label: 'End Age',
                    type: 'number',
                    defaultValue: retirementAge.toString(),
                    placeholder: 'Age to end SIP'
                }
            ],
            onSubmit: (values) => {
                const amount = parseFloat(values.amount);
                const startAge = parseInt(values.startAge);
                const endAge = parseInt(values.endAge);
                
                if (amount && startAge && endAge && endAge > startAge) {
                    setSips([...sips, { amount, startAge, endAge }]);
                }
            }
        });
    };
    
    const addLumpsum = () => {
        showInputModal({
            title: '💰 Add Lumpsum Investment',
            fields: [
                {
                    name: 'amount',
                    label: 'Lumpsum Amount (₹)',
                    type: 'number',
                    defaultValue: '500000',
                    placeholder: 'Enter lumpsum amount'
                },
                {
                    name: 'age',
                    label: 'Investment Age',
                    type: 'number',
                    defaultValue: (currentAge + 5).toString(),
                    placeholder: 'Age when you will invest'
                }
            ],
            onSubmit: (values) => {
                const amount = parseFloat(values.amount);
                const age = parseInt(values.age);
                
                if (amount && age && age > currentAge) {
                    setLumpsums([...lumpsums, { amount, age }]);
                }
            }
        });
    };
    
    // Scenario button style helper
    const scenarioBtn = (name, label, color) => {
        const active = scenario === name;
        return (
            <button
                style={{
                    padding: '4px 12px',
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    transition: 'all 0.2s',
                    border: 'none',
                    cursor: 'pointer',
                    background: active ? color : 'rgba(0,0,0,0.05)',
                    color: active ? '#fff' : '#6C757D',
                }}
                onClick={() => setScenario(name)}
            >
                {label}
            </button>
        );
    };
    
    return (
        <div style={{minHeight: '100vh', padding: '24px'}}>
            <div style={{maxWidth: '1280px', margin: '0 auto'}}>
                {/* Header */}
                <div className="glass-card" style={{marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <h1 style={{fontSize: '1.875rem', fontWeight: 700, color: 'var(--primary-green)'}}>
                        💰 Your Financial Life Journey
                    </h1>
                    <a href="/" className="btn-secondary" style={{width: 'auto', padding: '10px 20px'}}>
                        ← Back
                    </a>
                </div>
                
                <p style={{textAlign: 'center', fontSize: '1.1rem', color: 'var(--text-secondary)', marginBottom: '32px'}}>
                    Click anywhere on the timeline to add goals, income, or expenses!
                </p>
                
                {/* Goal Popup */}
                {showGoalPopup && (
                    <div 
                        style={{
                            position: 'fixed',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'rgba(0,0,0,0.7)',
                            backdropFilter: 'blur(5px)',
                            zIndex: 9999,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                        onClick={() => setShowGoalPopup(false)}
                    >
                        <div 
                            className="glass-card"
                            style={{
                                maxWidth: '600px',
                                width: '90%',
                                maxHeight: '80vh',
                                overflowY: 'auto'
                            }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
                                <h3 style={{fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-green)'}}>
                                    Add Event at Age {clickedAge}
                                </h3>
                                <button 
                                    onClick={() => setShowGoalPopup(false)}
                                    style={{background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.8rem', color: '#6C757D'}}
                                >
                                    ×
                                </button>
                            </div>
                            
                            {/* Goal Templates */}
                            <div style={{marginBottom: '24px'}}>
                                <h4 style={{fontSize: '1.1rem', fontWeight: 600, marginBottom: '12px', color: 'var(--text-secondary)'}}>🎯 Life Goals</h4>
                                <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px'}}>
                                    {goalTemplates.map((template, index) => (
                                        <div
                                            key={index}
                                            className="goal-card"
                                            onClick={() => {
                                                showInputModal({
                                                    title: `🎯 Add ${template.name}`,
                                                    fields: [{
                                                        name: 'amount',
                                                        label: 'Amount (₹)',
                                                        type: 'number',
                                                        defaultValue: template.defaultAmount,
                                                        placeholder: 'Enter amount'
                                                    }],
                                                    onSubmit: (values) => {
                                                        if (values.amount) addGoalFromPopup(template, values.amount);
                                                    }
                                                });
                                            }}
                                        >
                                            <div style={{marginBottom: '4px', display: 'flex', justifyContent: 'center'}}><GoalIcon iconType={template.iconType} size={20} /></div>
                                            <div style={{fontSize: '0.75rem', fontWeight: 600}}>{template.name}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            
                            {/* Quick Income/Expense */}
                            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px'}}>
                                <div>
                                    <h4 style={{fontSize: '1.1rem', fontWeight: 600, marginBottom: '12px', color: '#10b981'}}>💰 Add Income</h4>
                                    <button
                                        className="btn-primary"
                                        style={{background: 'linear-gradient(135deg, #10b981, #059669)'}}
                                        onClick={() => {
                                            showInputModal({
                                                title: '💰 Add Income',
                                                fields: [{
                                                    name: 'amount',
                                                    label: 'Income/Lumpsum Amount (₹)',
                                                    type: 'number',
                                                    defaultValue: '500000',
                                                    placeholder: 'Enter income amount'
                                                }],
                                                onSubmit: (values) => {
                                                    if (values.amount) addIncome(values.amount);
                                                }
                                            });
                                        }}
                                    >
                                        Add Lumpsum Income
                                    </button>
                                </div>
                                <div>
                                    <h4 style={{fontSize: '1.1rem', fontWeight: 600, marginBottom: '12px', color: '#ef4444'}}>💸 Add Expense</h4>
                                    <button
                                        className="btn-primary"
                                        style={{background: 'linear-gradient(135deg, #ef4444, #dc2626)'}}
                                        onClick={() => {
                                            showInputModal({
                                                title: '💸 Add Expense',
                                                fields: [
                                                    {
                                                        name: 'name',
                                                        label: 'Expense Name',
                                                        type: 'text',
                                                        defaultValue: 'Other Expense',
                                                        placeholder: 'Enter expense name'
                                                    },
                                                    {
                                                        name: 'amount',
                                                        label: 'Amount (₹)',
                                                        type: 'number',
                                                        defaultValue: '100000',
                                                        placeholder: 'Enter amount'
                                                    }
                                                ],
                                                onSubmit: (values) => {
                                                    if (values.name && values.amount) {
                                                        addExpense(values.amount, values.name);
                                                    }
                                                }
                                            });
                                        }}
                                    >
                                        Add One-time Expense
                                    </button>
                                </div>
                            </div>
                            
                            <div style={{textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '16px'}}>
                                Click outside to close or press Escape
                            </div>
                        </div>
                    </div>
                )}
                
                {/* Summary Cards */}
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px'}} className="gp-summary-grid">
                    <div className="stat-card">
                        <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px'}}>Retirement Corpus (Age {retirementAge})</div>
                        <div style={{fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-green)'}}>{formatCurrency(wealthAtRetirement)}</div>
                    </div>
                    <div className="stat-card">
                        <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px'}}>Funds Available Till</div>
                        <div style={{fontSize: '1.5rem', fontWeight: 700, color: 'var(--dark-green)'}}>
                            {moneyRunsOutAge >= lifeEndAge ? `Age ${lifeEndAge}+` : `Age ${moneyRunsOutAge}`}
                        </div>
                    </div>
                    <div className="stat-card">
                        <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px'}}>Peak Wealth</div>
                        <div style={{fontSize: '1.5rem', fontWeight: 700, color: '#8b5cf6'}}>{formatCurrency(peakWealth)}</div>
                    </div>
                    <div className="stat-card">
                        <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px'}}>Total Goals</div>
                        <div style={{fontSize: '1.5rem', fontWeight: 700, color: '#ec4899'}}>{goals.length}</div>
                        <div style={{fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px'}}>
                            {formatCurrency(goals.reduce((sum, g) => sum + g.amount, 0))}
                        </div>
                    </div>
                </div>
                
                {/* Chart and Goals Side by Side */}
                <div style={{display: 'flex', gap: '16px', marginBottom: '24px'}} className="gp-chart-row">
                    {/* Main Chart Area */}
                    <div className="glass-card" style={{flex: '3'}}>
                        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px'}}>
                            <div>
                                <h3 style={{fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary-green)'}}>📈 Your Wealth Growth Timeline</h3>
                                <p style={{fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px'}}>👆 Click on the chart at any age to add events</p>
                            </div>
                            <div style={{display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap'}}>
                                <div style={{display: 'flex', gap: '8px'}}>
                                    {scenarioBtn('optimistic', 'Optimistic (14%)', '#22c55e')}
                                    {scenarioBtn('medium', 'Medium (12%)', '#3b82f6')}
                                    {scenarioBtn('pessimistic', 'Pessimistic (8%)', '#ef4444')}
                                </div>
                                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                                    <label style={{fontSize: '0.85rem', whiteSpace: 'nowrap', marginBottom: 0}}>Life End Age:</label>
                                    <input 
                                        type="number" 
                                        value={lifeEndAge} 
                                        onChange={e => setLifeEndAge(parseInt(e.target.value))} 
                                        min={retirementAge + 10}
                                        max="120"
                                        style={{width: '80px', fontSize: '14px', padding: '6px 10px'}}
                                    />
                                </div>
                            </div>
                        </div>
                        <div 
                            ref={containerRef} 
                            className={`drop-zone ${isDraggingOver ? 'drag-over' : ''}`}
                            style={{position: 'relative', overflowX: 'auto'}}
                            onDragOver={(e) => {
                                e.preventDefault();
                                if (!draggedTemplate) return;
                                const rect = e.currentTarget.getBoundingClientRect();
                                const x = e.clientX - rect.left - margin.left;
                                const xScale = d3.scaleLinear()
                                    .domain([currentAge, lifeEndAge])
                                    .range([0, innerWidth]);
                                const age = Math.round(xScale.invert(x));
                                if (age >= currentAge && age <= lifeEndAge) {
                                    handleDragOver(e, age);
                                }
                            }}
                            onDragLeave={handleDragLeave}
                            onDrop={(e) => {
                                if (!dropAge) return;
                                handleDrop(e, dropAge);
                            }}
                        >
                            <svg ref={svgRef} width={width} height={height} style={{display: 'block', margin: '0 auto'}} />
                            {draggedTemplate && dropAge && (
                                <div 
                                    className="goal-ghost"
                                    style={{
                                        position: 'absolute',
                                        left: `${margin.left + (dropAge - currentAge) / (lifeEndAge - currentAge) * innerWidth}px`,
                                        top: '50%',
                                        transform: 'translate(-50%, -50%)'
                                    }}
                                >
                                    <GoalIcon iconType={draggedTemplate.iconType} size={32} />
                                </div>
                            )}
                        </div>
                    </div>
                    
                    {/* Goal Templates - 1/4 width */}
                    <div className="glass-card" style={{flex: '1', minWidth: '250px'}}>
                        <h3 style={{fontSize: '1.1rem', fontWeight: 700, marginBottom: '8px', color: 'var(--primary-green)'}}>🎯 Drag & Drop Goals</h3>
                        <p style={{color: 'var(--text-secondary)', marginBottom: '12px', fontSize: '0.85rem'}}>
                            Drag any goal icon and drop it on the chart!
                        </p>
                        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px'}}>
                            {goalTemplates.map((template, index) => (
                                <div
                                    key={index}
                                    className={`goal-card ${draggedTemplate?.name === template.name ? 'dragging' : ''}`}
                                    draggable="true"
                                    onDragStart={() => handleDragStart(template)}
                                    onDragEnd={handleDragEnd}
                                    onClick={() => {
                                        showInputModal({
                                            title: `🎯 Add ${template.name}`,
                                            fields: [
                                                {
                                                    name: 'age',
                                                    label: 'Target Age',
                                                    type: 'number',
                                                    defaultValue: (currentAge + 5).toString(),
                                                    placeholder: 'Enter target age'
                                                },
                                                {
                                                    name: 'amount',
                                                    label: 'Amount (₹)',
                                                    type: 'number',
                                                    defaultValue: template.defaultAmount,
                                                    placeholder: 'Enter amount'
                                                }
                                            ],
                                            onSubmit: (values) => {
                                                const age = parseInt(values.age);
                                                const amount = parseFloat(values.amount);
                                                if (age && age > currentAge && amount) {
                                                    setGoals([...goals, {
                                                        iconType: template.iconType,
                                                        name: template.name,
                                                        amount: amount,
                                                        age: age
                                                    }]);
                                                }
                                            }
                                        });
                                    }}
                                >
                                    <div style={{marginBottom: '8px', display: 'flex', justifyContent: 'center'}}><GoalIcon iconType={template.iconType} size={24} /></div>
                                    <div style={{fontSize: '0.75rem', fontWeight: 600}}>{template.name}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
                
                {/* Detailed Controls and Goals List */}
                <div className="footer-controls" style={{display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '12px'}} >
                    {/* Controls */}
                    <div style={{display: 'flex', flexDirection: 'column', gap: '12px'}}>
                        {/* Basic Info */}
                        <div className="glass-card">
                            <h3 style={{fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px', color: 'var(--primary-green)'}}>📊 Basic Information</h3>
                            <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                                <div>
                                    <label>Current Age</label>
                                    <input type="number" value={currentAge} onChange={e => setCurrentAge(parseInt(e.target.value))} min="18" max="80" />
                                </div>
                                <div>
                                    <label>Current Net Worth (₹)</label>
                                    <input type="number" value={currentNetworth} onChange={e => setCurrentNetworth(parseFloat(e.target.value))} step="100000" />
                                </div>
                                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
                                    <div>
                                        <label>Growth Rate (Scenario)</label>
                                        <div style={{padding: '12px 16px', borderRadius: '8px', background: 'rgba(0,0,0,0.03)', textAlign: 'center'}}>
                                            <span style={{fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary-green)'}}>{getScenarioGrowthRate()}%</span>
                                            <div style={{fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px', textTransform: 'capitalize'}}>{scenario}</div>
                                        </div>
                                    </div>
                                    <div>
                                        <label>Inflation (%)</label>
                                        <input type="number" value={inflationRate} onChange={e => setInflationRate(parseFloat(e.target.value))} step="0.5" />
                                    </div>
                                </div>
                                <div>
                                    <label>Retirement Age</label>
                                    <input type="number" value={retirementAge} onChange={e => setRetirementAge(parseInt(e.target.value))} min="40" max="80" />
                                </div>
                                <div>
                                    <label>Monthly Expense Post-Retirement (₹)</label>
                                    <input type="number" value={retirementExpense} onChange={e => setRetirementExpense(parseFloat(e.target.value))} step="10000" />
                                </div>
                            </div>
                        </div>
                        
                        {/* Add Investment */}
                        <div className="glass-card">
                            <h3 style={{fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px', color: 'var(--primary-green)'}}>💼 Add Investment</h3>
                            <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                                <button onClick={addSIP} className="btn-primary">
                                    📈 Add SIP
                                </button>
                                <button onClick={addLumpsum} className="btn-secondary">
                                    ➕ Add Lumpsum
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    {/* Goals List and Investments */}
                    <div style={{display: 'flex', flexDirection: 'column', gap: '12px'}}>
                        {/* Goals List */}
                        {goals.length > 0 && (
                            <div className="glass-card">
                                <h3 style={{fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px', color: 'var(--primary-green)'}}>📋 Planned Goals</h3>
                                <div style={{display: 'flex', flexDirection: 'column', gap: '12px'}}>
                                    {goals.map((goal, index) => (
                                        <div key={index} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', background: 'rgba(0,0,0,0.02)', borderRadius: '8px'}}>
                                            <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                                                <GoalIcon iconType={goal.iconType} size={24} />
                                                <div>
                                                    <div style={{fontWeight: 600}}>{goal.name}</div>
                                                    <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>Age {goal.age} • {formatCurrency(goal.amount)}</div>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => deleteGoal(index)}
                                                style={{color: '#ef4444', padding: '4px 12px', borderRadius: '4px', background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1rem'}}
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        {/* SIP List */}
                        {sips.length > 0 && (
                            <div className="glass-card">
                                <h3 style={{fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px', color: 'var(--primary-green)'}}>📈 Active SIPs</h3>
                                <div style={{display: 'flex', flexDirection: 'column', gap: '12px'}}>
                                    {sips.map((sip, index) => (
                                        <div key={index} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', background: 'rgba(0,0,0,0.02)', borderRadius: '8px'}}>
                                            <div>
                                                <div style={{fontWeight: 600}}>{formatCurrency(sip.amount)}/month</div>
                                                <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>Age {sip.startAge} to {sip.endAge}</div>
                                            </div>
                                            <button
                                                onClick={() => setSips(sips.filter((_, i) => i !== index))}
                                                style={{color: '#ef4444', padding: '4px 12px', borderRadius: '4px', background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1rem'}}
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        {/* Lumpsum List */}
                        {lumpsums.length > 0 && (
                            <div className="glass-card">
                                <h3 style={{fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px', color: 'var(--primary-green)'}}>➕ Lumpsum Investments</h3>
                                <div style={{display: 'flex', flexDirection: 'column', gap: '12px'}}>
                                    {lumpsums.map((lump, index) => (
                                        <div key={index} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', background: 'rgba(0,0,0,0.02)', borderRadius: '8px'}}>
                                            <div>
                                                <div style={{fontWeight: 600}}>{formatCurrency(lump.amount)}</div>
                                                <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>At Age {lump.age}</div>
                                            </div>
                                            <button
                                                onClick={() => setLumpsums(lumpsums.filter((_, i) => i !== index))}
                                                style={{color: '#ef4444', padding: '4px 12px', borderRadius: '4px', background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1rem'}}
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
            
            {/* Custom Input Modal */}
            {inputModal.show && (
                <div 
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0,0,0,0.7)',
                        backdropFilter: 'blur(5px)',
                        zIndex: 10000,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                    onClick={closeInputModal}
                >
                    <div 
                        className="glass-card"
                        style={{
                            maxWidth: '450px',
                            width: '90%',
                            animation: 'scaleIn 0.2s ease-out'
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px'}}>
                            <h3 style={{fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary-green)'}}>
                                {inputModal.title}
                            </h3>
                            <button 
                                onClick={closeInputModal}
                                style={{background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.5rem', color: '#6C757D'}}
                            >
                                ×
                            </button>
                        </div>
                        
                        <form onSubmit={(e) => {
                            e.preventDefault();
                            const formData = new FormData(e.target);
                            const values = {};
                            inputModal.fields.forEach(f => {
                                values[f.name] = formData.get(f.name);
                            });
                            if (inputModal.onSubmit) inputModal.onSubmit(values);
                            closeInputModal();
                        }}>
                            {inputModal.fields.map((field, idx) => (
                                <div key={idx} style={{marginBottom: '16px'}}>
                                    <label style={{display: 'block', fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '8px'}}>
                                        {field.label}
                                    </label>
                                    <input
                                        type={field.type || 'text'}
                                        name={field.name}
                                        defaultValue={field.defaultValue || ''}
                                        placeholder={field.placeholder || ''}
                                        required={field.required !== false}
                                        autoFocus={idx === 0}
                                        style={{
                                            width: '100%',
                                            padding: '12px 16px',
                                            borderRadius: '8px',
                                            background: 'var(--white)',
                                            border: '1px solid var(--gray-200)',
                                            color: 'var(--text-primary)',
                                            fontSize: '1rem',
                                            transition: 'border-color 0.3s'
                                        }}
                                    />
                                </div>
                            ))}
                            
                            <div style={{display: 'flex', gap: '12px', marginTop: '24px'}}>
                                <button
                                    type="button"
                                    onClick={closeInputModal}
                                    style={{
                                        flex: 1,
                                        padding: '12px 16px',
                                        borderRadius: '8px',
                                        background: '#6C757D',
                                        color: '#fff',
                                        fontWeight: 600,
                                        border: 'none',
                                        cursor: 'pointer',
                                        transition: 'background 0.2s'
                                    }}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    style={{
                                        flex: 1,
                                        padding: '12px 16px',
                                        borderRadius: '8px',
                                        background: 'var(--primary-green)',
                                        color: '#fff',
                                        fontWeight: 600,
                                        border: 'none',
                                        cursor: 'pointer',
                                        transition: 'background 0.2s'
                                    }}
                                >
                                    Confirm
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
            
            {/* Custom Confirm Modal */}
            {confirmModal.show && (
                <div 
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0,0,0,0.7)',
                        backdropFilter: 'blur(5px)',
                        zIndex: 10000,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                    onClick={closeConfirmModal}
                >
                    <div 
                        className="glass-card"
                        style={{
                            maxWidth: '400px',
                            width: '90%',
                            textAlign: 'center',
                            animation: 'scaleIn 0.2s ease-out'
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h3 style={{fontSize: '1.25rem', fontWeight: 700, color: '#f59e0b', marginBottom: '16px'}}>
                            {confirmModal.title}
                        </h3>
                        <p style={{color: 'var(--text-secondary)', marginBottom: '24px'}}>
                            {confirmModal.message}
                        </p>
                        
                        <div style={{display: 'flex', gap: '12px'}}>
                            <button
                                onClick={() => {
                                    closeConfirmModal();
                                    if (confirmModal.onCancel) confirmModal.onCancel();
                                }}
                                style={{
                                    flex: 1,
                                    padding: '12px 16px',
                                    borderRadius: '8px',
                                    background: '#6C757D',
                                    color: '#fff',
                                    fontWeight: 600,
                                    border: 'none',
                                    cursor: 'pointer'
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => {
                                    closeConfirmModal();
                                    if (confirmModal.onConfirm) confirmModal.onConfirm();
                                }}
                                style={{
                                    flex: 1,
                                    padding: '12px 16px',
                                    borderRadius: '8px',
                                    background: '#ef4444',
                                    color: '#fff',
                                    fontWeight: 600,
                                    border: 'none',
                                    cursor: 'pointer'
                                }}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Mount the app
ReactDOM.render(<FinancialPlanner />, document.getElementById('root'));
