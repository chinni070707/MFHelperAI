/**
 * Reusable Footer Component for MFHelper
 * Includes SEBI guidelines, About Us, Contact, etc.
 */

function createFooter() {
    const footerHTML = `
        <footer style="
            background: #1A3A2A;
            border-top: 1px solid rgba(127,192,76,0.2);
            margin-top: 40px;
            padding: 24px 20px 12px;
            color: rgba(255,255,255,0.85);
        ">
            <div style="max-width: 1400px; margin: 0 auto;">
                <!-- Main Footer Content -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 24px; margin-bottom: 16px;">
                    
                    <!-- About Section -->
                    <div>
                        <h3 style="color: #7FC04C; margin-bottom: 8px; font-size: 1rem;">📊 About MFHelper</h3>
                        <p style="font-size: 0.85rem; line-height: 1.5; opacity: 0.8;">
                            MFHelper is a free portfolio tracking and analysis tool for Indian mutual fund investors. 
                            We help you understand your investments better with advanced analytics and insights.
                        </p>
                        <div style="margin-top: 8px;">
                            <a href="mailto:support@mfhelper.com" style="color: #7FC04C; text-decoration: none; font-size: 0.85rem;">
                                ✉️ support@mfhelper.com
                            </a>
                        </div>
                    </div>
                    
                    <!-- Quick Links -->
                    <div>
                        <h3 style="color: #7FC04C; margin-bottom: 8px; font-size: 1rem;">🔗 Quick Links</h3>
                        <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem; line-height: 1.7;">
                            <li><a href="/dashboard.html" style="color: rgba(255,255,255,0.7); text-decoration: none; transition: color 0.3s;">🏠 Dashboard</a></li>
                            <li><a href="/goal-planning.html" style="color: rgba(255,255,255,0.7); text-decoration: none;">🎯 Goal Planning</a></li>
                            <li><a href="#" onclick="showAboutModal(); return false;" style="color: rgba(255,255,255,0.7); text-decoration: none;">ℹ️ About Us</a></li>
                            <li><a href="#" onclick="showContactModal(); return false;" style="color: rgba(255,255,255,0.7); text-decoration: none;">📞 Contact</a></li>
                            <li><a href="#" onclick="showPrivacyModal(); return false;" style="color: rgba(255,255,255,0.7); text-decoration: none;">🔒 Privacy Policy</a></li>
                            <li><a href="#" onclick="showTermsModal(); return false;" style="color: rgba(255,255,255,0.7); text-decoration: none;">📜 Terms of Service</a></li>
                        </ul>
                    </div>
                    
                    <!-- SEBI Disclaimer -->
                    <div>
                        <h3 style="color: #7FC04C; margin-bottom: 8px; font-size: 1rem;">⚖️ SEBI Guidelines</h3>
                        <div style="font-size: 0.8rem; line-height: 1.5; opacity: 0.7;">
                            <p style="margin-bottom: 6px;">
                                <strong>IMPORTANT:</strong> MFHelper is NOT a SEBI registered investment adviser.
                            </p>
                            <p style="margin-bottom: 6px;">
                                We provide portfolio tracking and analysis tools only. This is NOT investment advice.
                            </p>
                            <p>
                                Always consult with a SEBI registered investment adviser before making investment decisions.
                            </p>
                        </div>
                        <a href="#" onclick="showSEBIModal(); return false;" style="
                            display: inline-block;
                            margin-top: 8px;
                            padding: 6px 12px;
                            background: rgba(127,192,76,0.15);
                            border: 1px solid #7FC04C;
                            border-radius: 6px;
                            color: #7FC04C;
                            text-decoration: none;
                            font-size: 0.8rem;
                            transition: all 0.3s;
                        ">📖 Read Full Disclaimer</a>
                    </div>
                    
                    <!-- Social & Trust Badges -->
                    <div>
                        <h3 style="color: #7FC04C; margin-bottom: 8px; font-size: 1rem;">🌐 Connect</h3>
                        <div style="display: flex; gap: 12px; margin-bottom: 12px;">
                            <a href="#" style="color: rgba(255,255,255,0.7); font-size: 1.5rem; transition: color 0.3s;" title="Twitter">🐦</a>
                            <a href="#" style="color: rgba(255,255,255,0.7); font-size: 1.5rem; transition: color 0.3s;" title="LinkedIn">💼</a>
                            <a href="#" style="color: rgba(255,255,255,0.7); font-size: 1.5rem; transition: color 0.3s;" title="GitHub">💻</a>
                        </div>
                        <div style="font-size: 0.8rem; line-height: 1.6; opacity: 0.7;">
                            <p>✅ 100% Free to Use</p>
                            <p>🔒 Your Data is Private</p>
                            <p>📱 Mobile Responsive</p>
                            <p>🇮🇳 Made in India</p>
                        </div>
                    </div>
                </div>
                
                <!-- Bottom Bar -->
                <div style="
                    border-top: 1px solid rgba(127,192,76,0.15);
                    padding-top: 12px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 10px;
                    font-size: 0.8rem;
                    opacity: 0.6;
                ">
                    <div>
                        © 2026 MFHelper. All rights reserved.
                    </div>
                    <div>
                        Version 1.0.0 | Last Updated: Feb 2026
                    </div>
                </div>
            </div>
        </footer>
        
        <!-- Modal Container for Popups -->
        <div id="modalContainer"></div>
    `;
    
    return footerHTML;
}

// Modal Functions
function showModal(title, content) {
    const modal = document.getElementById('modalContainer');
    modal.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 20px;
        " onclick="closeModal(event)">
            <div style="
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 16px;
                max-width: 800px;
                width: 100%;
                max-height: 90vh;
                overflow-y: auto;
                padding: 40px;
                color: white;
                box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            " onclick="event.stopPropagation()">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                    <h2 style="color: #00d4ff; font-size: 1.8rem; margin: 0;">${title}</h2>
                    <button onclick="closeModal()" style="
                        background: none;
                        border: none;
                        color: white;
                        font-size: 2rem;
                        cursor: pointer;
                        opacity: 0.7;
                        transition: opacity 0.3s;
                        padding: 0;
                        width: 40px;
                        height: 40px;
                    ">×</button>
                </div>
                <div style="line-height: 1.8; opacity: 0.9;">
                    ${content}
                </div>
            </div>
        </div>
    `;
}

function closeModal(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('modalContainer').innerHTML = '';
}

function showAboutModal() {
    const content = `
        <h3 style="color: #00d4ff; margin-bottom: 15px;">🚀 Our Mission</h3>
        <p>MFHelper was created to democratize mutual fund portfolio analysis in India. We believe every investor deserves access to professional-grade portfolio analytics, regardless of their wealth or investment size.</p>
        
        <h3 style="color: #00d4ff; margin: 30px 0 15px;">💡 What We Offer</h3>
        <ul style="padding-left: 20px;">
            <li>Free portfolio tracking across multiple funds</li>
            <li>Automatic CAS (Consolidated Account Statement) import</li>
            <li>Advanced analytics: overlap detection, asset allocation, performance tracking</li>
            <li>Goal-based planning with gamification</li>
            <li>XIRR calculations for accurate returns</li>
            <li>Tax harvesting suggestions</li>
            <li>Rebalancing recommendations</li>
        </ul>
        
        <h3 style="color: #00d4ff; margin: 30px 0 15px;">🎯 Our Values</h3>
        <ul style="padding-left: 20px;">
            <li><strong>Transparency:</strong> No hidden fees, no commissions, no conflicts of interest</li>
            <li><strong>Privacy:</strong> Your data stays private. We don't sell your information</li>
            <li><strong>Education:</strong> We help you understand your investments better</li>
            <li><strong>Simplicity:</strong> Complex analytics made simple and actionable</li>
        </ul>
        
        <h3 style="color: #00d4ff; margin: 30px 0 15px;">👥 Who We Are</h3>
        <p>We're a team of investors, developers, and finance enthusiasts who were frustrated with existing portfolio tracking tools. So we built MFHelper - the tool we wished existed.</p>
        
        <div style="
            background: rgba(0,212,255,0.1);
            border-left: 3px solid #00d4ff;
            padding: 15px;
            margin-top: 30px;
            border-radius: 4px;
        ">
            <strong>🌟 Our Goal:</strong> To become India's most trusted mutual fund portfolio analysis platform.
        </div>
    `;
    showModal('📊 About MFHelper', content);
}

function showContactModal() {
    const content = `
        <h3 style="color: #00d4ff; margin-bottom: 15px;">📧 Get in Touch</h3>
        <p>We'd love to hear from you! Whether you have questions, feedback, or need help, we're here for you.</p>
        
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin: 20px 0;">
            <h4 style="color: #00d4ff; margin-bottom: 15px;">📬 Contact Information</h4>
            <p><strong>Email:</strong> <a href="mailto:support@mfhelper.com" style="color: #00d4ff;">support@mfhelper.com</a></p>
            <p><strong>Response Time:</strong> Within 24-48 hours</p>
        </div>
        
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin: 20px 0;">
            <h4 style="color: #00d4ff; margin-bottom: 15px;">💬 Feedback & Suggestions</h4>
            <p>Have an idea to improve MFHelper? We're all ears!</p>
            <p><a href="mailto:feedback@mfhelper.com" style="color: #00d4ff;">feedback@mfhelper.com</a></p>
        </div>
        
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin: 20px 0;">
            <h4 style="color: #00d4ff; margin-bottom: 15px;">🐛 Report a Bug</h4>
            <p>Found something broken? Let us know!</p>
            <p><a href="mailto:bugs@mfhelper.com" style="color: #00d4ff;">bugs@mfhelper.com</a></p>
        </div>
        
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin: 20px 0;">
            <h4 style="color: #00d4ff; margin-bottom: 15px;">🤝 Partnerships & Collaborations</h4>
            <p>Interested in partnering with us?</p>
            <p><a href="mailto:partnerships@mfhelper.com" style="color: #00d4ff;">partnerships@mfhelper.com</a></p>
        </div>
        
        <div style="
            background: rgba(247,37,133,0.1);
            border-left: 3px solid #f72585;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
        ">
            <strong>⚠️ Note:</strong> For investment advice, please consult with a SEBI registered investment adviser. We do not provide personalized investment recommendations.
        </div>
    `;
    showModal('📞 Contact Us', content);
}

function showSEBIModal() {
    const content = `
        <h3 style="color: #00d4ff; margin-bottom: 15px;">⚖️ SEBI Compliance & Disclaimers</h3>
        
        <div style="
            background: rgba(247,37,133,0.1);
            border: 2px solid #f72585;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 12px;
        ">
            <h4 style="color: #f72585; margin-bottom: 10px;">⚠️ IMPORTANT DISCLOSURE</h4>
            <p style="font-size: 1.1rem; font-weight: 600;">
                MFHelper is NOT a SEBI registered Investment Adviser under the SEBI (Investment Advisers) Regulations, 2013.
            </p>
        </div>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">📋 What We Are</h4>
        <p>MFHelper is a portfolio tracking and analysis tool. We provide:</p>
        <ul style="padding-left: 20px; margin-top: 10px;">
            <li>Portfolio tracking functionality</li>
            <li>Historical performance analysis</li>
            <li>Asset allocation visualization</li>
            <li>Overlap detection between funds</li>
            <li>XIRR calculation tools</li>
            <li>Educational content about mutual funds</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🚫 What We Are NOT</h4>
        <ul style="padding-left: 20px;">
            <li>We do NOT provide personalized investment advice</li>
            <li>We do NOT recommend specific funds or investment strategies</li>
            <li>We do NOT manage your investments</li>
            <li>We do NOT execute trades on your behalf</li>
            <li>We do NOT guarantee any returns or performance</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">📖 SEBI Guidelines for Investors</h4>
        <p>According to SEBI regulations:</p>
        <ul style="padding-left: 20px; margin-top: 10px;">
            <li>Always verify if your investment adviser is SEBI registered</li>
            <li>Check registration status at <a href="https://www.sebi.gov.in/" target="_blank" style="color: #00d4ff;">www.sebi.gov.in</a></li>
            <li>Do not rely solely on past performance for investment decisions</li>
            <li>Read all scheme-related documents carefully before investing</li>
            <li>Mutual fund investments are subject to market risks</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🔍 Find a SEBI Registered Adviser</h4>
        <p>To consult with a SEBI registered investment adviser:</p>
        <ol style="padding-left: 20px; margin-top: 10px;">
            <li>Visit <a href="https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=35" target="_blank" style="color: #00d4ff;">SEBI's official website</a></li>
            <li>Check the list of registered Investment Advisers</li>
            <li>Verify their registration number and validity</li>
            <li>Understand their fee structure before engagement</li>
        </ol>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">⚖️ Relevant SEBI Regulations</h4>
        <ul style="padding-left: 20px;">
            <li>SEBI (Investment Advisers) Regulations, 2013</li>
            <li>SEBI (Mutual Funds) Regulations, 1996</li>
            <li>SEBI (Prohibition of Fraudulent and Unfair Trade Practices) Regulations, 2003</li>
        </ul>
        
        <div style="
            background: rgba(0,212,255,0.1);
            border-left: 3px solid #00d4ff;
            padding: 15px;
            margin-top: 30px;
            border-radius: 4px;
        ">
            <strong>💡 Remember:</strong> Mutual fund investments are subject to market risks. Read all scheme related documents carefully before investing. Past performance is not indicative of future returns.
        </div>
    `;
    showModal('⚖️ SEBI Guidelines & Disclaimers', content);
}

function showPrivacyModal() {
    const content = `
        <h3 style="color: #00d4ff; margin-bottom: 15px;">🔒 Privacy Policy</h3>
        <p><em>Last Updated: February 7, 2026</em></p>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">📊 Data We Collect</h4>
        <p>When you use MFHelper, we may collect:</p>
        <ul style="padding-left: 20px;">
            <li><strong>Portfolio Data:</strong> Fund names, investment amounts, transaction history you manually enter or upload</li>
            <li><strong>Account Information:</strong> Email address, name (if you create an account)</li>
            <li><strong>Usage Data:</strong> Pages visited, features used, time spent (via Google Analytics)</li>
            <li><strong>Technical Data:</strong> IP address, browser type, device information</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🎯 How We Use Your Data</h4>
        <ul style="padding-left: 20px;">
            <li>To provide portfolio tracking and analysis services</li>
            <li>To calculate returns, allocations, and other metrics</li>
            <li>To improve our service and user experience</li>
            <li>To send important updates (if you opt-in)</li>
            <li>To analyze usage patterns (anonymized data only)</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🔐 Data Security</h4>
        <p>We take data security seriously:</p>
        <ul style="padding-left: 20px;">
            <li>All data transmitted over HTTPS encryption</li>
            <li>Your portfolio data is stored securely</li>
            <li>We do NOT share your personal data with third parties</li>
            <li>We do NOT sell your data to anyone</li>
            <li>No data is shared with AMCs, advisors, or brokers</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🇮🇳 Compliance with Indian Laws</h4>
        <p>We comply with:</p>
        <ul style="padding-left: 20px;">
            <li>Digital Personal Data Protection Act (DPDP), 2023</li>
            <li>Information Technology Act, 2000</li>
            <li>SEBI regulations regarding data handling</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">👤 Your Rights</h4>
        <p>You have the right to:</p>
        <ul style="padding-left: 20px;">
            <li>Access your data</li>
            <li>Export your portfolio data</li>
            <li>Delete your account and all associated data</li>
            <li>Opt-out of analytics tracking</li>
            <li>Request data corrections</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🍪 Cookies</h4>
        <p>We use cookies for:</p>
        <ul style="padding-left: 20px;">
            <li>Session management (keeping you logged in)</li>
            <li>Analytics (Google Analytics)</li>
            <li>Performance optimization</li>
        </ul>
        <p>You can disable cookies in your browser settings, but some features may not work.</p>
        
        <div style="
            background: rgba(0,212,255,0.1);
            border-left: 3px solid #00d4ff;
            padding: 15px;
            margin-top: 30px;
            border-radius: 4px;
        ">
            <strong>📧 Questions?</strong> Contact us at privacy@mfhelper.com
        </div>
    `;
    showModal('🔒 Privacy Policy', content);
}

function showTermsModal() {
    const content = `
        <h3 style="color: #00d4ff; margin-bottom: 15px;">📜 Terms of Service</h3>
        <p><em>Last Updated: February 7, 2026</em></p>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">✅ Acceptance of Terms</h4>
        <p>By using MFHelper, you agree to these terms. If you don't agree, please don't use our service.</p>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🎯 Service Description</h4>
        <p>MFHelper is a portfolio tracking tool that:</p>
        <ul style="padding-left: 20px;">
            <li>Tracks mutual fund investments</li>
            <li>Calculates returns and performance metrics</li>
            <li>Provides visualizations and analytics</li>
            <li>Offers educational content</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">⚠️ Disclaimers & Limitations</h4>
        <ul style="padding-left: 20px;">
            <li><strong>No Investment Advice:</strong> We do NOT provide investment recommendations</li>
            <li><strong>No Guarantees:</strong> Calculations are for informational purposes only</li>
            <li><strong>Market Risks:</strong> Mutual funds are subject to market risks</li>
            <li><strong>Accuracy:</strong> While we strive for accuracy, data may contain errors</li>
            <li><strong>Third-Party Data:</strong> We rely on external sources for NAV and fund data</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">👤 User Responsibilities</h4>
        <p>You agree to:</p>
        <ul style="padding-left: 20px;">
            <li>Provide accurate information</li>
            <li>Keep your account credentials secure</li>
            <li>Not misuse the service or attempt unauthorized access</li>
            <li>Verify all calculations independently</li>
            <li>Consult a SEBI registered adviser for investment decisions</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">💰 Pricing & Fees</h4>
        <p>Current Status: <strong>100% FREE</strong></p>
        <p>We reserve the right to introduce premium features in the future. Any changes will be communicated in advance.</p>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🚫 Limitation of Liability</h4>
        <p>MFHelper and its creators are NOT liable for:</p>
        <ul style="padding-left: 20px;">
            <li>Investment losses or gains</li>
            <li>Decisions made based on our tools</li>
            <li>Data inaccuracies or service interruptions</li>
            <li>Third-party actions or content</li>
        </ul>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">🔄 Changes to Terms</h4>
        <p>We may update these terms at any time. Continued use of the service after changes constitutes acceptance.</p>
        
        <h4 style="color: #00d4ff; margin: 25px 0 15px;">⚖️ Governing Law</h4>
        <p>These terms are governed by the laws of India. Any disputes will be subject to the jurisdiction of Indian courts.</p>
        
        <div style="
            background: rgba(247,37,133,0.1);
            border-left: 3px solid #f72585;
            padding: 15px;
            margin-top: 30px;
            border-radius: 4px;
        ">
            <strong>⚠️ Critical Reminder:</strong> MFHelper is a tool, not an investment adviser. Always do your own research and consult professionals before making investment decisions.
        </div>
    `;
    showModal('📜 Terms of Service', content);
}

// Initialize footer on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const footerPlaceholder = document.getElementById('footer-placeholder');
        if (footerPlaceholder) {
            footerPlaceholder.innerHTML = createFooter();
        }
    });
} else {
    const footerPlaceholder = document.getElementById('footer-placeholder');
    if (footerPlaceholder) {
        footerPlaceholder.innerHTML = createFooter();
    }
}
