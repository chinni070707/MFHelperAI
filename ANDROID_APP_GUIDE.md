# 📱 Generate Android App from MFHelper

## Overview

MFHelper uses **Capacitor** (by Ionic) to wrap the web app as a native Android app.

```
Web App (HTML/CSS/JS)
        ↓
   Capacitor
        ↓
Native Android APK
```

---

## Prerequisites

### 1. Install Node.js
Download and install from: https://nodejs.org/
- Recommended: LTS version (20.x)
- Verify installation: `node --version` and `npm --version`

### 2. Install Android Studio
Download from: https://developer.android.com/studio
- Install Android SDK (API 33+)
- Install Android SDK Build-Tools
- Install Android SDK Platform-Tools
- Set up an Android Virtual Device (AVD) for testing

### 3. Set Environment Variables
Add to System Environment Variables:
```
ANDROID_HOME = C:\Users\<username>\AppData\Local\Android\Sdk
PATH += %ANDROID_HOME%\platform-tools
PATH += %ANDROID_HOME%\tools
```

---

## Step-by-Step Guide

### Step 1: Initialize npm in frontend folder

```powershell
cd C:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\Sourcecode\MFHelper\frontend

npm init -y
```

### Step 2: Install Capacitor

```powershell
npm install @capacitor/core @capacitor/cli @capacitor/android
```

### Step 3: Initialize Capacitor

```powershell
npx cap init MFHelper com.mfhelper.app --web-dir .
```

This creates `capacitor.config.ts`:

```typescript
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.mfhelper.app',
  appName: 'MFHelper',
  webDir: '.',
  server: {
    // For development - connect to local server
    // url: 'http://192.168.1.100:8000',
    // cleartext: true
    
    // For production - use bundled assets
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#1E3A8A",
      showSpinner: false
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#1E3A8A'
    }
  },
  android: {
    allowMixedContent: true
  }
};

export default config;
```

### Step 4: Add Android Platform

```powershell
npx cap add android
```

This creates the `android/` folder with a full Android Studio project.

### Step 5: Copy Web Assets

```powershell
npx cap copy android
```

### Step 6: Open in Android Studio

```powershell
npx cap open android
```

This opens the project in Android Studio.

### Step 7: Build APK

In Android Studio:
1. **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**
2. Wait for build to complete
3. APK will be at: `android/app/build/outputs/apk/debug/app-debug.apk`

Or via command line:
```powershell
cd android
.\gradlew assembleDebug
```

### Step 8: Install on Device/Emulator

```powershell
# Install on connected device
adb install android/app/build/outputs/apk/debug/app-debug.apk

# Or run on emulator
npx cap run android
```

---

## Production Build (Signed APK/AAB)

### Step 1: Generate Keystore

```powershell
keytool -genkey -v -keystore mfhelper-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias mfhelper
```

### Step 2: Configure Signing in `android/app/build.gradle`

```groovy
android {
    signingConfigs {
        release {
            storeFile file('mfhelper-release-key.jks')
            storePassword 'your-store-password'
            keyAlias 'mfhelper'
            keyPassword 'your-key-password'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### Step 3: Build Release APK

```powershell
cd android
.\gradlew assembleRelease
```

### Step 4: Build AAB for Play Store

```powershell
cd android
.\gradlew bundleRelease
```

AAB file: `android/app/build/outputs/bundle/release/app-release.aab`

---

## App Icons & Splash Screen

### Replace Icons

Place your icons in these folders:
```
android/app/src/main/res/
├── mipmap-hdpi/ic_launcher.png      (72x72)
├── mipmap-mdpi/ic_launcher.png      (48x48)
├── mipmap-xhdpi/ic_launcher.png     (96x96)
├── mipmap-xxhdpi/ic_launcher.png    (144x144)
├── mipmap-xxxhdpi/ic_launcher.png   (192x192)
```

### Configure Splash Screen

Install plugin:
```powershell
npm install @capacitor/splash-screen
```

Add splash image:
```
android/app/src/main/res/drawable/splash.png
```

---

## Useful Capacitor Plugins

```powershell
# Status bar control
npm install @capacitor/status-bar

# Splash screen
npm install @capacitor/splash-screen

# Share functionality
npm install @capacitor/share

# Haptics (vibration)
npm install @capacitor/haptics

# Local notifications
npm install @capacitor/local-notifications

# App (background/foreground detection)
npm install @capacitor/app

# Network status
npm install @capacitor/network

# Preferences (localStorage alternative)
npm install @capacitor/preferences
```

---

## Update Capacitor App

After making changes to web code:

```powershell
# Copy updated web files
npx cap copy android

# Sync (copy + update plugins)
npx cap sync android

# Open in Android Studio
npx cap open android
```

---

## Development Workflow

### Option 1: Live Reload (Development)

Edit `capacitor.config.ts`:
```typescript
server: {
  url: 'http://YOUR_LOCAL_IP:8000',
  cleartext: true
}
```

Then:
```powershell
# Start backend server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run app on device (will connect to your local server)
npx cap run android
```

### Option 2: Bundled Assets (Production)

```powershell
# Copy web files to app
npx cap copy android

# Build and run
npx cap run android
```

---

## Troubleshooting

### "SDK location not found"

Create `android/local.properties`:
```
sdk.dir=C:\\Users\\<username>\\AppData\\Local\\Android\\Sdk
```

### "ANDROID_HOME is not set"

Add to PowerShell profile or System Environment Variables:
```powershell
$env:ANDROID_HOME = "C:\Users\<username>\AppData\Local\Android\Sdk"
```

### "Unable to find adb"

Ensure Android SDK platform-tools is in PATH:
```powershell
$env:PATH += ";$env:ANDROID_HOME\platform-tools"
```

### "App not connecting to backend"

1. Use your computer's local IP (not localhost)
2. Ensure `cleartext: true` in capacitor config for HTTP
3. Check firewall settings

---

## Quick Commands Reference

```powershell
# Initialize Capacitor
npx cap init MFHelper com.mfhelper.app --web-dir .

# Add Android platform
npx cap add android

# Copy web files to Android
npx cap copy android

# Sync (copy + update plugins)
npx cap sync android

# Open in Android Studio
npx cap open android

# Run on device/emulator
npx cap run android

# Build debug APK
cd android && .\gradlew assembleDebug

# Build release APK
cd android && .\gradlew assembleRelease

# Build AAB for Play Store
cd android && .\gradlew bundleRelease
```

---

## File Structure After Setup

```
MFHelper/
├── frontend/
│   ├── android/                    # ← Android Studio project
│   │   ├── app/
│   │   │   ├── src/main/
│   │   │   │   ├── java/          # Native code
│   │   │   │   ├── res/           # Icons, splash
│   │   │   │   └── assets/        # Web files (copied)
│   │   │   └── build.gradle
│   │   └── gradle/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── dashboard-pro.html
│   ├── capacitor.config.ts        # ← Capacitor config
│   ├── package.json
│   └── node_modules/
└── backend/
```

---

## Next Steps

1. **Install Node.js** from https://nodejs.org/
2. **Install Android Studio** from https://developer.android.com/studio
3. **Run the commands** in Step-by-Step Guide
4. **Test on emulator** first, then on real device
5. **Sign and publish** to Google Play Store

---

## Estimated Time

| Step | Time |
|------|------|
| Install prerequisites | 30-60 min |
| Setup Capacitor | 5 min |
| First build | 10 min |
| Testing & debugging | 30 min |
| **Total** | **~2 hours** |

---

*Last updated: January 31, 2026*
