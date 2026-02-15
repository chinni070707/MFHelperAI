"""
Email HTML Templates
All email templates follow responsive design best practices
"""

# Base template wrapper
def base_email_template(content: str) -> str:
    """Wrap content in base email template"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MFHelper</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', 'Helvetica', sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; max-width: 100%; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #7FC04C 0%, #6BA83C 100%); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">MFHelper</h1>
                            <p style="margin: 5px 0 0; color: #ffffff; font-size: 14px;">Smart Mutual Fund Portfolio Management</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            {content}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 10px; font-size: 14px; color: #6c757d;">
                                © 2026 MFHelper. All rights reserved.
                            </p>
                            <p style="margin: 0 0 10px; font-size: 12px; color: #6c757d;">
                                This email was sent to you as a registered user of MFHelper.
                            </p>
                            <p style="margin: 0; font-size: 12px;">
                                <a href="https://mfhelper.com/privacy" style="color: #7FC04C; text-decoration: none;">Privacy Policy</a> |
                                <a href="https://mfhelper.com/terms" style="color: #7FC04C; text-decoration: none;">Terms of Service</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

def generate_otp_email(otp: str, name: str, expires_in_minutes: int = 10) -> str:
    """Generate OTP verification email"""
    content = f"""
        <div style="text-align: center;">
            <h2 style="color: #2d3748; margin: 0 0 10px;">Verify Your Email</h2>
            <p style="color: #6c757d; font-size: 16px; margin: 0 0 30px;">Hi {name},</p>
            <p style="color: #6c757d; font-size: 14px; margin: 0 0 30px;">
                Use this OTP to verify your email address. This code will expire in {expires_in_minutes} minutes.
            </p>
            
            <!-- OTP Box -->
            <div style="background: linear-gradient(135deg, #7FC04C 0%, #6BA83C 100%); padding: 20px; border-radius: 8px; margin: 0 0 30px;">
                <p style="margin: 0 0 10px; color: #ffffff; font-size: 14px; font-weight: 600;">YOUR OTP CODE</p>
                <p style="margin: 0; color: #ffffff; font-size: 36px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                    {otp}
                </p>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; margin: 0 0 10px;">
                <strong>Security Tips:</strong>
            </p>
            <ul style="color: #6c757d; font-size: 13px; text-align: left; padding-left: 30px; margin: 0 0 20px;">
                <li>Never share this OTP with anyone</li>
                <li>MFHelper will never ask for your OTP via phone or email</li>
                <li>If you didn't request this, please ignore this email</li>
            </ul>
            
            <p style="color: #6c757d; font-size: 13px; margin: 0;">
                This code expires at <strong>{expires_in_minutes} minutes</strong> from now.
            </p>
        </div>
    """
    return base_email_template(content)

def generate_welcome_email(name: str) -> str:
    """Generate welcome email for new users"""
    content = f"""
        <div>
            <h2 style="color: #2d3748; margin: 0 0 20px;">Welcome to MFHelper! 🎉</h2>
            <p style="color: #6c757d; font-size: 16px; margin: 0 0 20px;">Hi {name},</p>
            <p style="color: #6c757d; font-size: 16px; margin: 0 0 20px;">
                Thank you for joining MFHelper! We're excited to help you manage your mutual fund portfolio smartly.
            </p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 0 0 20px;">
                <h3 style="color: #2d3748; margin: 0 0 15px; font-size: 18px;">Get Started:</h3>
                <ul style="color: #6c757d; font-size: 14px; margin: 0; padding-left: 20px; line-height: 1.8;">
                    <li><strong>Add Your Portfolio:</strong> Upload CAS statement or enter funds manually</li>
                    <li><strong>Analyze Overlap:</strong> Check if your funds have overlapping stocks</li>
                    <li><strong>Track Performance:</strong> Monitor your portfolio returns in real-time</li>
                    <li><strong>Plan Goals:</strong> Use our calculators for retirement, education planning</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://mfhelper.com/portfolio.html" style="display: inline-block; background: linear-gradient(135deg, #7FC04C 0%, #6BA83C 100%); color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 6px; font-weight: 600; font-size: 16px;">
                    Go to Dashboard →
                </a>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; margin: 20px 0 0;">
                Need help? Reply to this email or check our <a href="https://mfhelper.com/help" style="color: #7FC04C; text-decoration: none;">Help Center</a>.
            </p>
        </div>
    """
    return base_email_template(content)

def generate_password_reset_email(name: str, reset_url: str) -> str:
    """Generate password reset email"""
    content = f"""
        <div style="text-align: center;">
            <h2 style="color: #2d3748; margin: 0 0 10px;">Reset Your Password</h2>
            <p style="color: #6c757d; font-size: 16px; margin: 0 0 30px;">Hi {name},</p>
            <p style="color: #6c757d; font-size: 14px; margin: 0 0 30px;">
                We received a request to reset your password. Click the button below to create a new password:
            </p>
            
            <div style="margin: 0 0 30px;">
                <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #7FC04C 0%, #6BA83C 100%); color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 6px; font-weight: 600; font-size: 16px;">
                    Reset Password
                </a>
            </div>
            
            <p style="color: #6c757d; font-size: 13px; margin: 0 0 20px;">
                Or copy and paste this link in your browser:
            </p>
            <p style="color: #7FC04C; font-size: 12px; word-break: break-all; margin: 0 0 30px;">
                {reset_url}
            </p>
            
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; text-align: left; margin: 0 0 20px;">
                <p style="margin: 0; color: #856404; font-size: 13px;">
                    <strong>⚠️ Security Notice:</strong><br>
                    This link will expire in 1 hour. If you didn't request a password reset, please ignore this email and your password will remain unchanged.
                </p>
            </div>
        </div>
    """
    return base_email_template(content)

def generate_portfolio_update_email(
    name: str,
    total_value: float,
    total_invested: float,
    returns: float,
    returns_pct: float
) -> str:
    """Generate portfolio update notification email"""
    
    returns_color = "#10b981" if returns >= 0 else "#ef4444"
    returns_icon = "📈" if returns >= 0 else "📉"
    
    def format_currency(amount):
        if amount >= 10000000:
            return f"₹{amount/10000000:.2f}Cr"
        elif amount >= 100000:
            return f"₹{amount/100000:.2f}L"
        else:
            return f"₹{amount:,.0f}"
    
    content = f"""
        <div>
            <h2 style="color: #2d3748; margin: 0 0 10px;">Portfolio Update {returns_icon}</h2>
            <p style="color: #6c757d; font-size: 16px; margin: 0 0 30px;">Hi {name},</p>
            <p style="color: #6c757d; font-size: 14px; margin: 0 0 30px;">
                Here's your latest portfolio summary:
            </p>
            
            <!-- Summary Cards -->
            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 0 0 30px;">
                <tr>
                    <td style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center; width: 33%;">
                        <p style="margin: 0 0 5px; color: #6c757d; font-size: 12px; text-transform: uppercase;">Current Value</p>
                        <p style="margin: 0; color: #2d3748; font-size: 20px; font-weight: bold;">{format_currency(total_value)}</p>
                    </td>
                    <td style="width: 10px;"></td>
                    <td style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center; width: 33%;">
                        <p style="margin: 0 0 5px; color: #6c757d; font-size: 12px; text-transform: uppercase;">Invested</p>
                        <p style="margin: 0; color: #2d3748; font-size: 20px; font-weight: bold;">{format_currency(total_invested)}</p>
                    </td>
                    <td style="width: 10px;"></td>
                    <td style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center; width: 33%;">
                        <p style="margin: 0 0 5px; color: #6c757d; font-size: 12px; text-transform: uppercase;">Returns</p>
                        <p style="margin: 0; color: {returns_color}; font-size: 20px; font-weight: bold;">{format_currency(returns)}<br><span style="font-size: 14px;">({returns_pct:+.2f}%)</span></p>
                    </td>
                </tr>
            </table>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://mfhelper.com/portfolio.html" style="display: inline-block; background: linear-gradient(135deg, #7FC04C 0%, #6BA83C 100%); color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 6px; font-weight: 600; font-size: 16px;">
                    View Full Portfolio →
                </a>
            </div>
        </div>
    """
    return base_email_template(content)

def generate_feedback_confirmation_email(name: str, feedback_type: str) -> str:
    """Generate feedback confirmation email"""
    content = f"""
        <div style="text-align: center;">
            <h2 style="color: #2d3748; margin: 0 0 10px;">Thank You for Your Feedback! 💚</h2>
            <p style="color: #6c757d; font-size: 16px; margin: 0 0 30px;">Hi {name},</p>
            <p style="color: #6c757d; font-size: 14px; margin: 0 0 30px;">
                We've received your <strong>{feedback_type}</strong> and our team will review it shortly.
            </p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 0 0 30px; text-align: left;">
                <p style="color: #6c757d; font-size: 14px; margin: 0 0 10px;">
                    Your feedback helps us improve MFHelper for everyone. We typically respond within:
                </p>
                <ul style="color: #6c757d; font-size: 13px; margin: 0; padding-left: 20px; line-height: 1.8;">
                    <li><strong>Bug reports:</strong> 24-48 hours</li>
                    <li><strong>Feature requests:</strong> 3-5 business days</li>
                    <li><strong>General feedback:</strong> 1 week</li>
                </ul>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; margin: 0;">
                In the meantime, feel free to explore our other features!
            </p>
        </div>
    """
    return base_email_template(content)

def generate_cas_upload_success_email(name: str, funds_count: int, total_value: float) -> str:
    """Generate CAS upload success notification"""
    
    def format_currency(amount):
        if amount >= 10000000:
            return f"₹{amount/10000000:.2f}Cr"
        return f"₹{amount/100000:.2f}L"
    
    content = f"""
        <div>
            <h2 style="color: #2d3748; margin: 0 0 10px;">CAS Upload Successful! ✅</h2>
            <p style="color: #6c757d; font-size: 16px; margin: 0 0 30px;">Hi {name},</p>
            <p style="color: #6c757d; font-size: 14px; margin: 0 0 30px;">
                Your Consolidated Account Statement (CAS) has been successfully processed.
            </p>
            
            <div style="background-color: #d1fae5; border-left: 4px solid #10b981; padding: 20px; margin: 0 0 30px;">
                <p style="margin: 0 0 10px; color: #065f46; font-size: 16px; font-weight: 600;">
                    Portfolio Summary
                </p>
                <p style="margin: 0; color: #065f46; font-size: 14px;">
                    <strong>{funds_count}</strong> funds imported<br>
                    Total portfolio value: <strong>{format_currency(total_value)}</strong>
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://mfhelper.com/portfolio.html" style="display: inline-block; background: linear-gradient(135deg, #7FC04C 0%, #6BA83C 100%); color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 6px; font-weight: 600; font-size: 16px;">
                    View Your Portfolio →
                </a>
            </div>
            
            <p style="color: #6c757d; font-size: 13px; margin: 0;">
                Next steps: Analyze fund overlap, check portfolio allocation, and plan your goals!
            </p>
        </div>
    """
    return base_email_template(content)
