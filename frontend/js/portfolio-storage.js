/**
 * Portfolio Storage Manager
 * Handles localStorage operations for portfolio data (demo and guest mode)
 * Provides persistence across browser sessions
 */

class PortfolioStorage {
    constructor() {
        this.STORAGE_KEYS = {
            MODE: 'portfolioMode',              // 'demo' | 'guest' | 'authenticated'
            DEMO_DATA: 'demoPortfolioData',
            GUEST_DATA: 'guestPortfolioData',
            LOADED_AT: 'portfolioLoadedAt',
            DEMO_LOADED_AT: 'demoLoadedAt',
            EXPIRY_DAYS: 30                     // Data expires after 30 days
        };
    }

    // ============ Mode Management ============
    
    getMode() {
        return localStorage.getItem(this.STORAGE_KEYS.MODE) || null;
    }

    setMode(mode) {
        localStorage.setItem(this.STORAGE_KEYS.MODE, mode);
        localStorage.setItem(this.STORAGE_KEYS.LOADED_AT, new Date().toISOString());
    }

    isDemoMode() {
        return this.getMode() === 'demo';
    }

    isGuestMode() {
        return this.getMode() === 'guest';
    }

    isAuthenticated() {
        return this.getMode() === 'authenticated';
    }

    clearMode() {
        localStorage.removeItem(this.STORAGE_KEYS.MODE);
        localStorage.removeItem(this.STORAGE_KEYS.LOADED_AT);
    }

    // ============ Demo Portfolio ============

    saveDemoData(portfolioData) {
        try {
            const data = {
                ...portfolioData,
                savedAt: new Date().toISOString(),
                expiresAt: this.getExpiryDate()
            };
            localStorage.setItem(this.STORAGE_KEYS.DEMO_DATA, JSON.stringify(data));
            localStorage.setItem(this.STORAGE_KEYS.DEMO_LOADED_AT, data.savedAt);
            this.setMode('demo');
            return true;
        } catch (error) {
            console.error('Failed to save demo data:', error);
            return false;
        }
    }

    loadDemoData() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEYS.DEMO_DATA);
            if (!data) return null;

            const portfolio = JSON.parse(data);
            
            // Check expiry
            if (this.isExpired(portfolio.expiresAt)) {
                this.clearDemoData();
                return null;
            }

            return portfolio;
        } catch (error) {
            console.error('Failed to load demo data:', error);
            return null;
        }
    }

    clearDemoData() {
        localStorage.removeItem(this.STORAGE_KEYS.DEMO_DATA);
        localStorage.removeItem(this.STORAGE_KEYS.DEMO_LOADED_AT);
    }

    // ============ Guest Portfolio ============

    saveGuestData(portfolioData) {
        try {
            const data = {
                ...portfolioData,
                savedAt: new Date().toISOString(),
                expiresAt: this.getExpiryDate()
            };
            localStorage.setItem(this.STORAGE_KEYS.GUEST_DATA, JSON.stringify(data));
            this.setMode('guest');
            return true;
        } catch (error) {
            console.error('Failed to save guest data:', error);
            return false;
        }
    }

    loadGuestData() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEYS.GUEST_DATA);
            if (!data) return null;

            const portfolio = JSON.parse(data);
            
            // Check expiry
            if (this.isExpired(portfolio.expiresAt)) {
                this.clearGuestData();
                return null;
            }

            return portfolio;
        } catch (error) {
            console.error('Failed to load guest data:', error);
            return null;
        }
    }

    clearGuestData() {
        localStorage.removeItem(this.STORAGE_KEYS.GUEST_DATA);
    }

    // ============ Generic Portfolio Operations ============

    /**
     * Load the current portfolio data (alias for getCurrentPortfolio)
     */
    load() {
        return this.getCurrentPortfolio();
    }

    /**
     * Save the current portfolio data (alias for saveCurrentPortfolio)
     */
    save(portfolioData) {
        return this.saveCurrentPortfolio(portfolioData);
    }

    getCurrentPortfolio() {
        const mode = this.getMode();
        
        if (mode === 'demo') {
            return this.loadDemoData();
        } else if (mode === 'guest') {
            return this.loadGuestData();
        }
        
        return null;
    }

    saveCurrentPortfolio(portfolioData) {
        const mode = this.getMode();
        
        if (mode === 'demo') {
            return this.saveDemoData(portfolioData);
        } else if (mode === 'guest') {
            return this.saveGuestData(portfolioData);
        }
        
        return false;
    }

    clearCurrentPortfolio() {
        const mode = this.getMode();
        
        if (mode === 'demo') {
            this.clearDemoData();
        } else if (mode === 'guest') {
            this.clearGuestData();
        }
        
        this.clearMode();
    }

    // ============ Utility Methods ============

    getExpiryDate() {
        const date = new Date();
        date.setDate(date.getDate() + this.STORAGE_KEYS.EXPIRY_DAYS);
        return date.toISOString();
    }

    isExpired(expiryDateStr) {
        if (!expiryDateStr) return true;
        return new Date(expiryDateStr) < new Date();
    }

    getLoadedAt() {
        return localStorage.getItem(this.STORAGE_KEYS.LOADED_AT);
    }

    getDaysUntilExpiry() {
        const portfolio = this.getCurrentPortfolio();
        if (!portfolio || !portfolio.expiresAt) return 0;

        const expiry = new Date(portfolio.expiresAt);
        const now = new Date();
        const diffTime = expiry - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        return Math.max(0, diffDays);
    }

    // ============ Data Structure Helpers ============

    createPortfolioStructure(holdings, metadata = {}) {
        return {
            holdings: holdings || [],
            metadata: {
                totalInvested: 0,
                currentValue: 0,
                totalGain: 0,
                fundCount: holdings ? holdings.length : 0,
                lastUpdated: new Date().toISOString(),
                ...metadata
            },
            savedAt: new Date().toISOString(),
            expiresAt: this.getExpiryDate()
        };
    }

    // ============ Migration & Cleanup ============

    migrateToAuthenticated(authToken) {
        // Get current portfolio data
        const portfolio = this.getCurrentPortfolio();
        
        // Clear local storage
        this.clearCurrentPortfolio();
        
        // Set authenticated mode
        this.setMode('authenticated');
        localStorage.setItem('authToken', authToken);
        
        return portfolio;
    }

    clearAllData() {
        this.clearDemoData();
        this.clearGuestData();
        this.clearMode();
        localStorage.removeItem('authToken');
    }

    // ============ Storage Info ============

    getStorageInfo() {
        return {
            mode: this.getMode(),
            hasData: this.getCurrentPortfolio() !== null,
            loadedAt: this.getLoadedAt(),
            daysUntilExpiry: this.getDaysUntilExpiry(),
            isExpired: this.getDaysUntilExpiry() === 0,
            storageSize: this.getStorageSize()
        };
    }

    getStorageSize() {
        let total = 0;
        for (let key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                total += localStorage[key].length + key.length;
            }
        }
        return (total / 1024).toFixed(2) + ' KB';
    }
}

// Global instance
const portfolioStorage = new PortfolioStorage();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PortfolioStorage;
}
