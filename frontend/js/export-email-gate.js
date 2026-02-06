/**
 * Export Email Gate
 * Requires email before allowing portfolio export
 */

class ExportEmailGate {
    constructor() {
        this.modal = null;
        this.init();
    }

    init() {
        const style = document.createElement('style');
        style.textContent = this.getStyles();
        document.head.appendChild(style);

        this.createModal();
    }

    createModal() {
        const modal = document.createElement('div');
        modal.id = 'exportEmailModal';
        modal.className = 'export-email-modal';
        modal.innerHTML = `
            <div class="export-email-content">
                <h2>📤 Export Your Portfolio</h2>
                <p>Enter your email to receive the portfolio report</p>
                
                <form id="exportEmailForm" onsubmit="exportEmailGate.handleSubmit(event)">
                    <div class="email-input-group">
                        <input type="email" name="email" required 
                               placeholder="your@email.com" 
                               autocomplete="email">
                        <button type="submit" id="exportEmailBtn">
                            Send Report
                        </button>
                    </div>
                    
                    <label class="checkbox-label">
                        <input type="checkbox" name="newsletter" checked>
                        Subscribe to investment tips and market updates
                    </label>
                </form>
                
                <button class="export-cancel" onclick="exportEmailGate.close()">Cancel</button>
            </div>
        `;

        document.body.appendChild(modal);
        this.modal = modal;
    }

    show(callback) {
        // Check if already authenticated
        if (localStorage.getItem('authToken')) {
            // Directly proceed with export
            if (callback) callback();
            return;
        }

        // Check if email already captured this session
        const capturedEmail = sessionStorage.getItem('capturedEmail');
        if (capturedEmail) {
            // Directly proceed with export
            if (callback) callback();
            return;
        }

        this.exportCallback = callback;
        this.modal.style.display = 'flex';
    }

    close() {
        this.modal.style.display = 'none';
        this.exportCallback = null;
    }

    async handleSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const btn = document.getElementById('exportEmailBtn');
        const originalText = btn.textContent;

        btn.disabled = true;
        btn.textContent = 'Sending...';

        try {
            const formData = new FormData(form);
            const email = formData.get('email');
            const newsletter = formData.get('newsletter') === 'on';

            // Capture lead
            const response = await fetch('/api/auth/leads/capture', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    source: 'export-gate'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to process email');
            }

            // Store email in session
            sessionStorage.setItem('capturedEmail', email);

            if (typeof showToast === 'function') {
                showToast('Email captured! Preparing export...', 'success');
            }

            this.close();

            // Execute export callback
            if (this.exportCallback) {
                setTimeout(() => this.exportCallback(), 500);
            }

        } catch (error) {
            if (typeof showToast === 'function') {
                showToast(error.message, 'error');
            } else {
                alert(error.message);
            }
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }

    getStyles() {
        return `
            .export-email-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.85);
                backdrop-filter: blur(10px);
                z-index: 10002;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s;
            }

            .export-email-content {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 20px;
                padding: 40px;
                max-width: 500px;
                width: 90%;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .export-email-content h2 {
                color: #fff;
                font-size: 2rem;
                margin-bottom: 15px;
            }

            .export-email-content p {
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 30px;
                font-size: 1.1rem;
            }

            .email-input-group {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }

            .email-input-group input {
                flex: 1;
                padding: 14px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                color: #fff;
                font-size: 1rem;
                transition: all 0.3s;
            }

            .email-input-group input:focus {
                outline: none;
                border-color: #667eea;
                background: rgba(255, 255, 255, 0.08);
            }

            .email-input-group button {
                padding: 14px 24px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s;
                white-space: nowrap;
            }

            .email-input-group button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            }

            .email-input-group button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .checkbox-label {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 0.9rem;
                margin-bottom: 20px;
                cursor: pointer;
            }

            .checkbox-label input {
                cursor: pointer;
            }

            .export-cancel {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                cursor: pointer;
                font-size: 1rem;
                padding: 10px 20px;
                transition: color 0.3s;
            }

            .export-cancel:hover {
                color: #fff;
            }

            @media (max-width: 600px) {
                .export-email-content {
                    padding: 30px 20px;
                }

                .email-input-group {
                    flex-direction: column;
                }
            }
        `;
    }
}

// Initialize
const exportEmailGate = new ExportEmailGate();

// Override export function to use email gate
function gatedExport(exportFunction) {
    exportEmailGate.show(exportFunction);
}
