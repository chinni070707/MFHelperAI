# Email Service Setup Guide

## 🎯 Quick Setup with Resend

### Step 1: Get Resend API Key

1. Go to [https://resend.com](https://resend.com)
2. Sign up (it's free!)
3. Verify your email
4. Go to **API Keys** section
5. Click **Create API Key**
6. Copy the API key (starts with `re_`)

### Step 2: Configure MFHelper

1. **Update `.env` file:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Add Resend configuration:**
   ```env
   # Email Configuration (Resend)
   RESEND_API_KEY=re_your_api_key_here
   RESEND_FROM_EMAIL=onboarding@resend.dev  # Use this for testing
   FRONTEND_URL=http://localhost:3000
   ```

3. **For production** (custom domain):
   ```env
   RESEND_FROM_EMAIL=noreply@yourdomain.com
   ```

### Step 3: Test Email Service

1. **Start backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Test with curl or Postman:**
   ```bash
   # Test email service
   curl -X POST http://localhost:8000/api/email/test-email \
     -H "Content-Type: application/json" \
     -d '{"email":"your@email.com","name":"Test User"}'
   ```

3. **Test OTP sending:**
   ```bash
   # Send OTP
   curl -X POST http://localhost:8000/api/email/send-otp \
     -H "Content-Type: application/json" \
     -d '{"email":"your@email.com","purpose":"verification"}'
   
   # Verify OTP
   curl -X POST http://localhost:8000/api/email/verify-otp \
     -H "Content-Type: application/json" \
     -d '{"email":"your@email.com","otp":"123456","purpose":"verification"}'
   ```

---

## 📧 Available Email Types

### 1. **OTP/Verification Email**
```python
POST /api/email/send-otp
{
  "email": "user@example.com",
  "purpose": "verification"  # or "password_reset", "login"
}
```

### 2. **Welcome Email**
```python
POST /api/email/send-welcome
{
  "email": "newuser@example.com",
  "name": "New User"
}
```

### 3. **Feedback Confirmation**
```python
POST /api/email/send-feedback
{
  "name": "User Name",
  "email": "user@example.com",
  "feedback_type": "bug",
  "subject": "Issue with portfolio",
  "message": "Detailed feedback..."
}
```

---

## 🆓 Resend Free Tier

**Generous Free Tier:**
- ✅ **3,000 emails/month**
- ✅ **100 emails/day**
- ✅ Perfect for startups
- ✅ No credit card required

**When to upgrade:**
- Need more than 3,000 emails/month
- Want custom domain (production)
- Pro: $20/month for 50,000 emails

---

## 🎨 Email Templates

All emails use responsive HTML templates with:
- ✅ MFHelper branding
- ✅ Mobile-friendly design
- ✅ Professional styling
- ✅ Security tips (for OTP)

Templates available:
1. **OTP Email** - Large, clear OTP display
2. **Welcome Email** - Onboarding guide
3. **Password Reset** - Secure reset link
4. **Portfolio Update** - Performance summary
5. **Feedback Confirmation** - Thank you message

---

## 🔐 Security Features

### OTP Service
- ✅ 10-minute expiration
- ✅ Maximum 3 attempts
- ✅ 1-minute cooldown (anti-spam)
- ✅ Auto-cleanup of expired OTPs
- ✅ Purpose-based isolation

### Best Practices
- Never log full OTPs
- Rate limit OTP requests
- Clear OTP after verification
- Use HTTPS only in production

---

## 🚀 Production Setup

### 1. **Domain Verification (Resend)**

1. Go to Resend Dashboard → **Domains**
2. Add your domain: `mfhelper.com`
3. Add DNS records:
   ```
   Type: TXT
   Name: resend._domainkey
   Value: [Provided by Resend]
   ```
4. Wait for verification (~5-10 minutes)
5. Update `.env`:
   ```env
   RESEND_FROM_EMAIL=noreply@mfhelper.com
   ```

### 2. **Environment Variables (Render)**

1. Go to Render Dashboard → Your Service
2. Add Environment Variables:
   ```
   RESEND_API_KEY=re_your_production_key
   RESEND_FROM_EMAIL=noreply@mfhelper.com
   FRONTEND_URL=https://mfhelper.com
   ```

### 3. **Testing in Production**

```bash
# Test from production URL
curl -X POST https://mfhelper.onrender.com/api/email/test-email \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","name":"Test"}'
```

---

## 🐛 Troubleshooting

### Email not sending?

1. **Check API key:**
   ```bash
   echo $RESEND_API_KEY
   ```

2. **Check logs:**
   ```bash
   # Backend terminal will show:
   # ⚠️ RESEND_API_KEY not configured - email not sent
   ```

3. **Test API key directly:**
   ```bash
   curl https://api.resend.com/emails \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "from": "onboarding@resend.dev",
       "to": "your@email.com",
       "subject": "Test",
       "html": "<h1>Test</h1>"
     }'
   ```

### OTP not working?

1. **Check OTP hasn't expired** (10 minutes)
2. **Check attempts** (max 3)
3. **Wait cooldown** (1 minute between requests)
4. **Clear expired OTPs:**
   ```bash
   curl http://localhost:8000/api/email/cleanup-expired
   ```

### Emails going to spam?

1. ✅ **Verify domain** (SPF, DKIM)
2. ✅ **Use professional content**
3. ✅ **Add unsubscribe link** (for marketing)
4. ✅ **Warm up IP** (gradually increase volume)

---

## 📊 Monitoring

### Check Resend Dashboard:
- **Delivery rate**: Should be >99%
- **Bounce rate**: Should be <1%
- **Spam complaints**: Should be 0

### API Endpoints:
```bash
# Check service health
curl http://localhost:8000/health

# Check email logs (implement if needed)
curl http://localhost:8000/api/admin/email-logs
```

---

## 💰 Cost Estimation

### Startup (0-1000 users):
- **Resend Free**: 3,000 emails/month = **$0**
- Average: 3 emails/user/month
- **Cost: $0/month**

### Growth (1000-10000 users):
- **Resend Pro**: $20/month for 50K emails
- Average: 5 emails/user/month = 50K emails/month
- **Cost: $20/month**

### Scale (10000+ users):
- **Resend Business**: $80/month for 100K emails
- Or add **Amazon SES**: $0.10 per 1,000 emails
- **Cost: $80/month** or **$10-50/month (SES)**

---

## 🔄 Migration to SES (Future)

When you outgrow Resend (>100K emails/month):

1. **Keep Resend for OTP** (reliability)
2. **Add Amazon SES for marketing** (cost)
3. **Use hybrid approach**:
   ```python
   # Critical emails → Resend
   # Bulk/marketing → SES
   ```

---

## ✅ Integration Checklist

- [ ] Resend account created
- [ ] API key added to `.env`
- [ ] Test email sent successfully
- [ ] OTP tested and working
- [ ] Welcome email integrated with signup
- [ ] Password reset email working
- [ ] Feedback form sends confirmation
- [ ] Domain verified (production)
- [ ] DNS records configured
- [ ] Monitoring setup
- [ ] Error handling tested

---

## 📚 Resources

- **Resend Docs**: https://resend.com/docs
- **Resend API Reference**: https://resend.com/docs/api-reference
- **Python SDK**: https://github.com/resendlabs/resend-python
- **FastAPI Integration**: https://resend.com/docs/send-with-fastapi
- **Email Best Practices**: https://resend.com/docs/knowledge-base

---

## 🆘 Support

Need help?
1. Check Resend documentation
2. Check backend logs
3. Test with curl commands
4. Contact: support@mfhelper.com

**Happy Emailing! 📧**
