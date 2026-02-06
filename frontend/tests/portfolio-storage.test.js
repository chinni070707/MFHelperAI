/**
 * Tests for Portfolio Storage Manager
 * Tests localStorage operations for demo and guest mode
 */

describe('PortfolioStorage', () => {
    let storage;

    beforeEach(() => {
        // Clear localStorage before each test
        localStorage.clear();
        sessionStorage.clear();
        
        // Create new instance
        storage = new PortfolioStorage();
    });

    describe('Mode Management', () => {
        test('should set and get portfolio mode', () => {
            storage.setMode('demo');
            expect(storage.getMode()).toBe('demo');
            expect(storage.isDemoMode()).toBe(true);
            expect(storage.isGuestMode()).toBe(false);
        });

        test('should detect demo mode', () => {
            storage.setMode('demo');
            expect(storage.isDemoMode()).toBe(true);
        });

        test('should detect guest mode', () => {
            storage.setMode('guest');
            expect(storage.isGuestMode()).toBe(true);
        });

        test('should detect authenticated mode', () => {
            storage.setMode('authenticated');
            expect(storage.isAuthenticated()).toBe(true);
        });

        test('should clear mode', () => {
            storage.setMode('demo');
            storage.clearMode();
            expect(storage.getMode()).toBeNull();
        });
    });

    describe('Demo Portfolio', () => {
        const sampleData = {
            holdings: [
                { scheme_name: 'Test Fund', invested_amount: 10000 }
            ],
            metadata: { totalInvested: 10000 }
        };

        test('should save demo data', () => {
            const result = storage.saveDemoData(sampleData);
            expect(result).toBe(true);
            expect(storage.getMode()).toBe('demo');
        });

        test('should load demo data', () => {
            storage.saveDemoData(sampleData);
            const loaded = storage.loadDemoData();
            
            expect(loaded).not.toBeNull();
            expect(loaded.holdings).toHaveLength(1);
            expect(loaded.holdings[0].scheme_name).toBe('Test Fund');
        });

        test('should return null for expired demo data', () => {
            const expiredData = {
                ...sampleData,
                expiresAt: new Date(Date.now() - 1000).toISOString()
            };
            
            localStorage.setItem('demoPortfolioData', JSON.stringify(expiredData));
            
            const loaded = storage.loadDemoData();
            expect(loaded).toBeNull();
        });

        test('should clear demo data', () => {
            storage.saveDemoData(sampleData);
            storage.clearDemoData();
            
            expect(storage.loadDemoData()).toBeNull();
        });
    });

    describe('Guest Portfolio', () => {
        const sampleData = {
            holdings: [
                { scheme_name: 'Test Fund', invested_amount: 10000 }
            ],
            metadata: { totalInvested: 10000 }
        };

        test('should save guest data', () => {
            const result = storage.saveGuestData(sampleData);
            expect(result).toBe(true);
            expect(storage.getMode()).toBe('guest');
        });

        test('should load guest data', () => {
            storage.saveGuestData(sampleData);
            const loaded = storage.loadGuestData();
            
            expect(loaded).not.toBeNull();
            expect(loaded.holdings).toHaveLength(1);
        });

        test('should clear guest data', () => {
            storage.saveGuestData(sampleData);
            storage.clearGuestData();
            
            expect(storage.loadGuestData()).toBeNull();
        });
    });

    describe('Generic Operations', () => {
        const demoData = {
            holdings: [{ scheme_name: 'Demo Fund' }],
            metadata: {}
        };

        const guestData = {
            holdings: [{ scheme_name: 'Guest Fund' }],
            metadata: {}
        };

        test('should get current portfolio based on mode', () => {
            storage.saveDemoData(demoData);
            const portfolio = storage.getCurrentPortfolio();
            
            expect(portfolio).not.toBeNull();
            expect(portfolio.holdings[0].scheme_name).toBe('Demo Fund');
        });

        test('should save current portfolio based on mode', () => {
            storage.setMode('guest');
            const result = storage.saveCurrentPortfolio(guestData);
            
            expect(result).toBe(true);
            const loaded = storage.getCurrentPortfolio();
            expect(loaded.holdings[0].scheme_name).toBe('Guest Fund');
        });

        test('should clear current portfolio', () => {
            storage.saveDemoData(demoData);
            storage.clearCurrentPortfolio();
            
            expect(storage.getCurrentPortfolio()).toBeNull();
            expect(storage.getMode()).toBeNull();
        });
    });

    describe('Expiry Management', () => {
        test('should calculate days until expiry', () => {
            const futureDate = new Date();
            futureDate.setDate(futureDate.getDate() + 15);
            
            const data = {
                holdings: [],
                metadata: {},
                expiresAt: futureDate.toISOString()
            };
            
            storage.saveDemoData(data);
            const daysLeft = storage.getDaysUntilExpiry();
            
            expect(daysLeft).toBeGreaterThanOrEqual(14);
            expect(daysLeft).toBeLessThanOrEqual(16);
        });

        test('should detect expired data', () => {
            const pastDate = new Date(Date.now() - 86400000).toISOString();
            expect(storage.isExpired(pastDate)).toBe(true);
        });

        test('should detect non-expired data', () => {
            const futureDate = new Date(Date.now() + 86400000).toISOString();
            expect(storage.isExpired(futureDate)).toBe(false);
        });
    });

    describe('Migration', () => {
        test('should migrate to authenticated', () => {
            const data = {
                holdings: [{ scheme_name: 'Test Fund' }],
                metadata: {}
            };
            
            storage.saveGuestData(data);
            const token = 'test-token-123';
            
            const portfolio = storage.migrateToAuthenticated(token);
            
            expect(portfolio).not.toBeNull();
            expect(storage.getMode()).toBe('authenticated');
            expect(localStorage.getItem('authToken')).toBe(token);
            expect(storage.loadGuestData()).toBeNull();
        });
    });

    describe('Storage Info', () => {
        test('should provide storage information', () => {
            const data = {
                holdings: [],
                metadata: {}
            };
            
            storage.saveDemoData(data);
            const info = storage.getStorageInfo();
            
            expect(info.mode).toBe('demo');
            expect(info.hasData).toBe(true);
            expect(info.daysUntilExpiry).toBeGreaterThan(0);
            expect(info.isExpired).toBe(false);
        });
    });

    describe('Data Structure', () => {
        test('should create portfolio structure', () => {
            const holdings = [
                { scheme_name: 'Fund 1', invested_amount: 10000 },
                { scheme_name: 'Fund 2', invested_amount: 20000 }
            ];
            
            const portfolio = storage.createPortfolioStructure(holdings);
            
            expect(portfolio.holdings).toHaveLength(2);
            expect(portfolio.metadata.fundCount).toBe(2);
            expect(portfolio.savedAt).toBeDefined();
            expect(portfolio.expiresAt).toBeDefined();
        });
    });
});

// Run tests
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PortfolioStorage };
}
