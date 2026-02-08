# Google OAuth Integration Setup Guide

This guide walks you through setting up Google Sign-In for MFHelper.

## 📋 Overview

Users can now sign in with their Google account in addition to email/password authentication. The integration supports:
- **One-click sign-in** with Google account
- **Automatic account creation** for new users
- **Account linking** for existing users
- **Profile picture sync** from Google

---

## 🔧 Backend Setup

### 1. Get Google OAuth Credentials

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project (or select existing):**
   - Click on the project dropdown (top left)
   - Click "New Project"
   - Name it: `MFHelper` or your preferred name
   - Click "Create"

3. **Enable Google+ API:**
   - In the left sidebar, go to **APIs & Services** → **Library**
   - Search for "Google+ API"
   - Click on it and click **"Enable"**

4. **Create OAuth Consent Screen:**
   - Go to **APIs & Services** → **OAuth consent screen**
   - Select **External** (for public users)
   - Click **Create**
   - Fill in required fields:
     - **App name:** MFHelper
     - **User support email:** your-email@example.com
     - **Developer contact:** your-email@example.com
   - Click **Save and Continue**
   - **Scopes:** Add `email`, `profile`, `openid` (default scopes)
   - Click **Save and Continue**
   - **Test users:** Add your email for testing
   - Click **Save and Continue**

5. **Create OAuth Client ID:**
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - Application type: **Web application**
   - Name: `MFHelper Web Client`
   - **Authorized JavaScript origins:**
     ```
     http://localhost:8000
     https://yourdomain.com
     https://mfhelper-xxxxx.onrender.com
     ```
   - **Authorized redirect URIs:**
     ```
     http://localhost:8000/api/auth/google/callback
     https://yourdomain.com/api/auth/google/callback
     https://mfhelper-xxxxx.onrender.com/api/auth/google/callback
     ```
   - Click **Create**
   - **Copy the Client ID and Client Secret** (you'll need these)

---

### 2. Configure Backend Environment Variables

#### Local Development (.env file):

```bash
# Google OAuth Settings
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

#### Production (Render):

Using Render MCP:

```powershell
$RENDER_API_KEY = "your-render-api-key"
$serviceId = "srv-xxxxx"
$headers = @{ 
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}

# Get all current env vars
$envVarsResponse = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Headers $headers -Method Get

# Update env vars to include Google OAuth
$envVars = $envVarsResponse | ForEach-Object { 
    @{ 
        key = $_.envVar.key
        value = $_.envVar.value
    } 
}

# Add Google OAuth variables
$envVars += @{ key = "GOOGLE_CLIENT_ID"; value = "your-client-id.apps.googleusercontent.com" }
$envVars += @{ key = "GOOGLE_CLIENT_SECRET"; value = "your-client-secret" }
$envVars += @{ key = "GOOGLE_REDIRECT_URI"; value = "https://mfhelper-xxxxx.onrender.com/api/auth/google/callback" }

# Send update
$body = $envVars | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Headers $headers -Method Put -Body $body
```

Or via Render Dashboard:
1. Go to your service → **Environment** tab
2. Add these variables:
   - `GOOGLE_CLIENT_ID`: Your Google Client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google Client Secret
   - `GOOGLE_REDIRECT_URI`: Your callback URL

---

### 3. Update Database Schema

The User model has been updated with OAuth fields:
- `oauth_provider` - "google", "github", etc.
- `oauth_id` - Unique ID from OAuth provider
- `profile_picture_url` - User's profile picture
- `hashed_password` - Now nullable (OAuth users don't need password)

#### Create Migration:

```powershell
cd backend

# Create migration
alembic revision --autogenerate -m "Add OAuth fields to User model"

# Review the migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

#### Manual SQL (if not using Alembic):

```sql
ALTER TABLE users 
ADD COLUMN oauth_provider VARCHAR(50),
ADD COLUMN oauth_id VARCHAR(255),
ADD COLUMN profile_picture_url VARCHAR(500),
MODIFY COLUMN hashed_password VARCHAR(255) NULL;
```

---

### 4. Install Dependencies

```powershell
cd backend
pip install authlib
pip install -r requirements.txt
```

---

## 🎨 Frontend Setup

### Update Google Client ID in login.html

Open `frontend/login.html` and replace the placeholder:

```javascript
google.accounts.id.initialize({
    client_id: 'YOUR_GOOGLE_CLIENT_ID',  // ← Replace with your actual Client ID
    callback: handleGoogleSignIn,
    auto_select: false
});
```

With your actual Google Client ID:

```javascript
google.accounts.id.initialize({
    client_id: '123456789-abcdefg.apps.googleusercontent.com',  // ← Your Client ID
    callback: handleGoogleSignIn,
    auto_select: false
});
```

---

## 🧪 Testing

### 1. Local Testing

```powershell
# Start backend
cd backend
uvicorn app.main:app --reload --port 8000
```

Visit: http://localhost:8000/login.html

### 2. Test Google Sign-In

1. Click the **"Continue with Google"** button
2. Select your Google account
3. Authorize the app
4. You should be redirected to the dashboard with a valid token

### 3. Verify in Database

```sql
SELECT id, email, full_name, oauth_provider, oauth_id, profile_picture_url 
FROM users 
WHERE oauth_provider = 'google';
```

---

## 🔒 Security Considerations

### 1. Client ID Security
- ✅ **Client ID is public** - Safe to include in frontend code
- ⚠️ **Client Secret is private** - Never expose in frontend
- 🔒 Keep Client Secret in environment variables only

### 2. Token Validation
- All Google ID tokens are verified server-side
- Token audience is checked against your Client ID
- Expired tokens are rejected

### 3. User Data
- Only request necessary scopes (email, profile)
- Profile pictures are cached but not stored permanently
- OAuth IDs are unique per Google account

---

## 🚀 Production Deployment

### 1. Update Google OAuth Settings

In Google Cloud Console:
- Add your production domain to **Authorized JavaScript origins**
- Add your production callback URL to **Authorized redirect URIs**

### 2. Deploy to Render

```powershell
# Push to GitHub (triggers auto-deploy)
git add .
git commit -m "Add Google OAuth integration"
git push origin main

# Monitor deployment
# See docs/RENDER_MCP_USAGE.md for monitoring commands
```

### 3. Verify Production Setup

1. Visit your production URL: `https://mfhelper-xxxxx.onrender.com/login.html`
2. Test Google Sign-In
3. Check logs for any errors

---

## 📊 API Endpoints

### Backend OAuth  Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/google/login` | GET | Initiate Google OAuth flow (redirects to Google) |
| `/api/auth/google/callback` | GET | Handle Google OAuth callback |
| `/api/auth/google/verify` | POST | Verify Google ID token (for JS SDK) |
| `/api/auth/me` | GET | Get current user info |

### Example Usage (JavaScript Frontend):

```javascript
// After Google Sign-In callback
async function handleGoogleSignIn(response) {
    const result = await fetch('/api/auth/google/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: response.credential })
    });
    
    const data = await result.json();
    
    if (result.ok) {
        // Store token
        localStorage.setItem('authToken', data.access_token);
        localStorage.setItem('userInfo', JSON.stringify(data.user));
        
        // Redirect
        window.location.href = '/dashboard.html';
    }
}
```

---

## 🐛 Troubleshooting

### Issue: "Google OAuth is not configured" error
**Solution:** Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in environment variables.

### Issue: Redirect URI mismatch
**Solution:** 
- Check that the callback URL in Google Cloud Console exactly matches your backend URL
- Include protocol (http/https), domain, and path
- No trailing slashes

### Issue: "Invalid token audience" error
**Solution:** The Client ID in frontend JavaScript must match the one in backend environment variables.

### Issue: User sees blank screen after Google auth
**Solution:** 
- Check browser console for JavaScript errors
- Verify the token is being stored in localStorage
- Check dashboard.html exists and is accessible

### Issue: Database error "Column not found"
**Solution:** Run the database migration to add OAuth columns to the users table.

---

## 📚 Related Documentation

- [Render MCP Usage Guide](./RENDER_MCP_USAGE.md) - Manage deployment via Render API
- [Render Deployment Guide](../doc/RENDER_DEPLOYMENT.md) - Full deployment setup
- [Authentication Implementation](../doc/AUTH_IMPLEMENTATION.md) - Auth system overview

---

## 🎯 Next Steps

1. ✅ Set up Google OAuth credentials
2. ✅ Configure environment variables
3. ✅ Run database migration
4. ✅ Test locally
5. ✅ Deploy to production
6. 🚀 Monitor user signups via Google OAuth
7. 💡 Consider adding GitHub OAuth (similar process)

---

## 🆘 Support

If you encounter issues:
1. Check the logs: `alembic/versions/` and backend logs
2. Verify all environment variables are set correctly
3. Ensure Google OAuth consent screen is configured
4. Test with a fresh browser session (incognito mode)

Happy coding! 🚀
