/**
 * Dashboard Modals JavaScript - Manual Entry and Upload Modals
 */

// AMC list - will be fetched from backend
let amcList = [];
let fundsByAmc = {};

async function showManualEntryModal() {
    document.getElementById('manualEntryModal').style.display = 'block';
    
    // Load AMC list first if not already loaded
    if (amcList.length === 0) {
        await loadAmcList();
    }
    
    // Load existing data if available
    await loadExistingManualData();
}

function closeManualEntryModal() {
    document.getElementById('manualEntryModal').style.display = 'none';
}

async function loadExistingManualData() {
    const tbody = document.getElementById('entryTableBody');
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        // Not authenticated - show 5 empty rows
        tbody.innerHTML = '';
        for (let i = 0; i < 5; i++) {
            addManualEntryRow();
        }
        return;
    }

    try {
        // Fetch user's portfolio from database
        const response = await fetch('/api/portfolio/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch portfolio');
        }

        const data = await response.json();
        console.log('Loaded portfolio data:', data);

        // Check if portfolio exists and has holdings
        if (data.holdings && data.holdings.length > 0) {
            // Pre-populate form with existing data
            tbody.innerHTML = ''; // Clear existing rows

            data.holdings.forEach(holding => {
                addManualEntryRowWithData(holding);
            });

            console.log(`✅ Pre-populated ${data.holdings.length} holdings`);
        } else {
            // No existing data - add 5 empty rows
            tbody.innerHTML = '';
            for (let i = 0; i < 5; i++) {
                addManualEntryRow();
            }
        }
    } catch (error) {
        console.error('Error loading existing data:', error);
        // On error, show 5 empty rows
        tbody.innerHTML = '';
        for (let i = 0; i < 5; i++) {
            addManualEntryRow();
        }
    }
}

function addManualEntryRowWithData(holding) {
    const tbody = document.getElementById('entryTableBody');
    const row = document.createElement('tr');
    
    // Generate AMC dropdown options with pre-selected value
    let amcOptions = '';
    if (amcList.length === 0) {
        amcList = ['HDFC', 'ICICI Prudential', 'SBI', 'Axis', 'Kotak', 'DSP', 'Nippon India', 'UTI', 'Mirae Asset', 'Parag Parikh'];
    }
    
    amcOptions = amcList.map(amc => 
        `<option value="${amc}" ${amc === holding.amc ? 'selected' : ''}>${amc}</option>`
    ).join('');
    
    const fundEnabled = holding.amc ? '' : 'disabled';
    
    row.innerHTML = `
        <td>
            <select class="amc-select" onchange="onAmcChange(this)" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.3); background: rgba(255, 255, 255, 0.15); color: #ffffff;" required>
                <option value="">Select AMC...</option>
                ${amcOptions}
            </select>
        </td>
        <td style="position: relative;">
            <input type="text" class="fund-search" placeholder="${holding.amc ? 'Search funds...' : 'Select AMC first'}" 
                   oninput="searchFunds(this)" 
                   onfocus="showFundDropdown(this)"
                   data-fund-id="${holding.id || ''}" 
                   value="${holding.fund_name || ''}"
                   ${fundEnabled}
                   style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.3); background: rgba(255, 255, 255, 0.15); color: #ffffff;"
                   required>
            <div class="fund-dropdown" style="display: none; position: absolute; top: 100%; left: 0; right: 0; background: rgba(20, 20, 40, 0.98); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px; max-height: 250px; overflow-y: auto; z-index: 1000; margin-top: 4px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);"></div>
        </td>
        <td><input type="number" step="0.01" min="0" placeholder="10000" value="${holding.invested || holding.invested_amount || ''}" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.3); background: rgba(255, 255, 255, 0.15); color: #ffffff;" required></td>
        <td><button class="btn" style="padding: 6px 12px; background: rgba(255,0,0,0.2); border-color: #ff4444;" onclick="removeRow(this)">×</button></td>
    `;
    tbody.appendChild(row);
}

async function loadAmcList() {
    try {
        const response = await fetch('/api/funds/amc-list');
        const data = await response.json();
        if (data.success) {
            amcList = data.amcs || [];
        }
    } catch (error) {
        console.error('❌ Failed to load AMC list:', error);
        // Fallback to common AMCs
        amcList = ['HDFC', 'ICICI Prudential', 'SBI', 'Axis', 'Kotak', 'Aditya Birla Sun Life', 'Nippon India', 'UTI', 'DSP', 'Franklin Templeton', 'Mirae Asset', 'Parag Parikh', 'Motilal Oswal', 'Edelweiss', 'PGIM', 'Tata', 'Invesco', 'Sundaram', 'Quantum', 'Quant', 'Mahindra Manulife', 'HSBC', 'Baroda BNP Paribas', 'LIC', 'Canara Robeco', 'BOI AXA', 'JM Financial', 'IDFC', 'L&T', 'Principal', 'Shriram'];
    }
}

// AMC Selection and Fund Search
let fundSearchTimeout = null;
let cachedFunds = [];

function onAmcChange(select) {
    const row = select.closest('tr');
    const fundInput = row.querySelector('.fund-search');
    const amc = select.value;
    
    // Clear fund selection when AMC changes
    fundInput.value = '';
    fundInput.setAttribute('data-fund-id', '');
    fundInput.disabled = !amc;
    
    if (amc) {
        fundInput.placeholder = `Search ${amc} funds...`;
        // Pre-fetch funds for this AMC
        prefetchFundsByAmc(amc);
    } else {
        fundInput.placeholder = 'Select AMC first';
    }
}

async function prefetchFundsByAmc(amc) {
    if (fundsByAmc[amc]) return; // Already cached
    
    try {
        const response = await fetch(`/api/funds/list?amc=${encodeURIComponent(amc)}&limit=100`);
        const data = await response.json();
        if (data.success) {
            fundsByAmc[amc] = data.funds || [];
        }
    } catch (error) {
        console.error('Failed to fetch funds for AMC:', error);
    }
}

async function searchFunds(input) {
    const row = input.closest('tr');
    const amcSelect = row.querySelector('.amc-select');
    const selectedAmc = amcSelect.value;
    
    if (!selectedAmc) {
        alert('Please select AMC / Fund House first');
        input.value = '';
        return;
    }
    
    const searchTerm = input.value.trim();
    const dropdown = input.parentElement.querySelector('.fund-dropdown');
    
    if (searchTerm.length < 2) {
        dropdown.style.display = 'none';
        return;
    }

    // Debounce search
    clearTimeout(fundSearchTimeout);
    fundSearchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/funds/list?search=${encodeURIComponent(searchTerm)}&amc=${encodeURIComponent(selectedAmc)}&dropdown=true&limit=20`);
            const data = await response.json();
            
            if (data.success && data.funds.length > 0) {
                displayFundOptions(dropdown, data.funds, input);
            } else {
                dropdown.innerHTML = `<div style="padding: 12px; color: rgba(255,255,255,0.6);">No ${selectedAmc} funds found</div>`;
                dropdown.style.display = 'block';
            }
        } catch (error) {
            console.error('Fund search error:', error);
        }
    }, 300);
}

function showFundDropdown(input) {
    const row = input.closest('tr');
    const amcSelect = row.querySelector('.amc-select');
    const selectedAmc = amcSelect.value;
    
    if (!selectedAmc) {
        return;
    }
    
    const dropdown = input.parentElement.querySelector('.fund-dropdown');
    
    // Show cached funds for this AMC
    if (fundsByAmc[selectedAmc] && fundsByAmc[selectedAmc].length > 0) {
        displayFundOptions(dropdown, fundsByAmc[selectedAmc], input);
    }
}

function displayFundOptions(dropdown, funds, input) {
    dropdown.innerHTML = '';
    
    funds.forEach(fund => {
        const option = document.createElement('div');
        option.className = 'fund-option';
        option.innerHTML = `
            <div class="fund-option-name">${fund.scheme_name}</div>
            <div class="fund-option-details">${fund.amc || ''} ${fund.category ? '• ' + fund.category : ''}</div>
        `;
        option.onclick = () => selectFund(fund, input, dropdown);
        dropdown.appendChild(option);
    });
    
    dropdown.style.display = 'block';
    cachedFunds = funds;
}

function selectFund(fund, input, dropdown) {
    input.value = fund.scheme_name;
    input.setAttribute('data-fund-id', fund.value);
    dropdown.style.display = 'none';
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('.fund-search') && !e.target.closest('.fund-dropdown')) {
        document.querySelectorAll('.fund-dropdown').forEach(d => d.style.display = 'none');
    }
});

function addManualEntryRow() {
    const tbody = document.getElementById('entryTableBody');
    const row = document.createElement('tr');
    
    // Generate AMC dropdown options
    let amcOptions = '';
    if (amcList.length === 0) {
        // Use fallback
        amcList = ['HDFC', 'ICICI Prudential', 'SBI', 'Axis', 'Kotak', 'DSP', 'Nippon India', 'UTI', 'Mirae Asset', 'Parag Parikh'];
    }
    
    amcOptions = amcList.map(amc => `<option value="${amc}">${amc}</option>`).join('');
    
    row.innerHTML = `
        <td>
            <select class="amc-select" onchange="onAmcChange(this)" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.3); background: rgba(255, 255, 255, 0.15); color: #ffffff;" required>
                <option value="">Select AMC...</option>
                ${amcOptions}
            </select>
        </td>
        <td style="position: relative;">
            <input type="text" class="fund-search" placeholder="Select AMC first" 
                   oninput="searchFunds(this)" 
                   onfocus="showFundDropdown(this)"
                   data-fund-id="" 
                   disabled
                   style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.3); background: rgba(255, 255, 255, 0.15); color: #ffffff;"
                   required>
            <div class="fund-dropdown" style="display: none; position: absolute; top: 100%; left: 0; right: 0; background: rgba(20, 20, 40, 0.98); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px; max-height: 250px; overflow-y: auto; z-index: 1000; margin-top: 4px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);"></div>
        </td>
        <td><input type="number" step="0.01" min="0" placeholder="10000" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.3); background: rgba(255, 255, 255, 0.15); color: #ffffff;" required></td>
        <td><button class="btn" style="padding: 6px 12px; background: rgba(255,0,0,0.2); border-color: #ff4444;" onclick="removeRow(this)">×</button></td>
    `;
    tbody.appendChild(row);
}

function removeRow(button) {
    const row = button.closest('tr');
    const tbody = document.getElementById('entryTableBody');
    if (tbody.children.length > 1) {
        row.remove();
    } else {
        alert('At least one row is required');
    }
}

async function saveManualEntries() {
    const tbody = document.getElementById('entryTableBody');
    const rows = tbody.querySelectorAll('tr');
    const holdings = [];
    
    for (const row of rows) {
        const amcSelect = row.querySelector('.amc-select');
        const fundInput = row.querySelector('.fund-search');
        const amountInput = row.querySelector('input[type="number"]');
        
        const amc = amcSelect ? amcSelect.value.trim() : '';
        const schemeName = fundInput.value.trim();
        const fundId = fundInput.getAttribute('data-fund-id');
        const amount = parseFloat(amountInput.value);
        
        // Skip empty rows
        if (!amc && !schemeName && !amount) {
            continue;
        }
        
        if (!amc || !schemeName || !amount || amount <= 0) {
            alert('Please fill all fields with valid values (AMC, Scheme Name, and Amount)');
            return;
        }
        
        holdings.push({
            amc: amc,
            scheme_name: schemeName,
            fund_id: fundId || null,
            invested_amount: amount
        });
    }
    
    if (holdings.length === 0) {
        alert('Please add at least one fund');
        return;
    }
    
    try {
        let token = localStorage.getItem('authToken');
        
        // If no token, create a guest user account first
        if (!token) {
            console.log('No auth token found, creating guest user...');
            const guestResponse = await fetch('/api/auth/guest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!guestResponse.ok) {
                throw new Error('Failed to create guest account');
            }
            
            const guestData = await guestResponse.json();
            token = guestData.access_token;
            
            // Store the guest token
            localStorage.setItem('authToken', token);
            localStorage.setItem('isGuestUser', 'true');
            
            console.log('Guest user created successfully');
        }
        
        // Save to database (works for both authenticated and guest users)
        const response = await fetch('/api/portfolio/manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ holdings })
        });
        
        if (!response.ok) throw new Error('Failed to save portfolio');
        
        const data = await response.json();
        console.log('✅ Portfolio saved:', data);
        
        // Also save to localStorage as backup
        const portfolioData = {
            holdings: holdings,
            source: 'manual_entry',
            savedAt: new Date().toISOString(),
            portfolio_id: data.portfolio_id
        };
        portfolioStorage.save(portfolioData);
        
        const isGuest = localStorage.getItem('isGuestUser') === 'true';
        if (isGuest) {
            alert('Portfolio saved! Sign up to access your data permanently from any device.');
        } else {
            alert('Portfolio saved successfully!');
        }
        
        closeManualEntryModal();
        
        // Wait for database transaction to complete before reloading
        console.log('⏳ Waiting for database commit...');
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Reload the page to show the new data
        window.location.reload();
    } catch (error) {
        console.error('Error saving portfolio:', error);
        alert('Error saving portfolio: ' + error.message);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const manualModal = document.getElementById('manualEntryModal');
    const uploadModal = document.getElementById('uploadModal');
    
    if (event.target === manualModal) {
        closeManualEntryModal();
    }
    if (event.target === uploadModal) {
        closeUploadModal();
    }
}

// Upload Modal Functions
let selectedFile = null;

function showUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    selectedFile = null;
    document.getElementById('selectedFileName').textContent = '';
    document.getElementById('uploadButton').disabled = true;
    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('progressBar').style.width = '0%';
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        document.getElementById('selectedFileName').textContent = `Selected: ${file.name}`;
        document.getElementById('uploadButton').disabled = false;
        
        // Show password field for PDF files
        if (file.name.toLowerCase().endsWith('.pdf')) {
            document.getElementById('pdfPasswordSection').style.display = 'block';
        } else {
            document.getElementById('pdfPasswordSection').style.display = 'none';
        }
    }
}

async function uploadFile() {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }

    const uploadButton = document.getElementById('uploadButton');
    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('uploadStatus');

    try {
        uploadButton.disabled = true;
        progressDiv.style.display = 'block';
        statusText.textContent = 'Uploading...';
        progressBar.style.width = '30%';

        const formData = new FormData();
        formData.append('file', selectedFile);
        
        // Add password if provided for PDF files
        if (selectedFile.name.toLowerCase().endsWith('.pdf')) {
            const password = document.getElementById('pdfPassword').value;
            if (password) {
                formData.append('password', password);
            }
        }

        let token = localStorage.getItem('authToken');
        
        // If no token, create a guest user account first
        if (!token) {
            console.log('No auth token found, creating guest user...');
            statusText.textContent = 'Creating guest account...';
            
            const guestResponse = await fetch('/api/auth/guest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!guestResponse.ok) {
                throw new Error('Failed to create guest account');
            }
            
            const guestData = await guestResponse.json();
            token = guestData.access_token;
            
            // Store the guest token
            localStorage.setItem('authToken', token);
            localStorage.setItem('isGuestUser', 'true');
            
            console.log('Guest user created successfully');
            statusText.textContent = 'Uploading...';
        }

        const response = await fetch('/api/upload/cas', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        progressBar.style.width = '70%';
        statusText.textContent = 'Processing...';

        if (!response.ok) {
            const error = await response.json();
            // Improve error message for password-protected PDFs
            let errorMsg = error.detail || 'Upload failed';
            if (errorMsg.includes('PAN as password') || errorMsg.includes('password protected')) {
                errorMsg = 'PDF is password protected. Please enter the PDF password above.';
            }
            throw new Error(errorMsg);
        }

        progressBar.style.width = '100%';
        
        const isGuest = localStorage.getItem('isGuestUser') === 'true';
        if (isGuest) {
            statusText.textContent = 'Success! Sign up to save permanently. Reloading...';
        } else {
            statusText.textContent = 'Success! Reloading dashboard...';
        }

        // Wait a moment to show success, then reload
        setTimeout(() => {
            closeUploadModal();
            window.location.reload();
        }, 1500);

    } catch (error) {
        statusText.textContent = 'Error: ' + error.message;
        statusText.style.color = '#ff4444';
        uploadButton.disabled = false;
        progressBar.style.width = '0%';
        
        setTimeout(() => {
            statusText.style.color = 'rgba(255,255,255,0.8)';
        }, 3000);
    }
}

// Check URL parameter for upload=true
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('upload') === 'true') {
        showUploadModal();
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});
