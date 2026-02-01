#!/usr/bin/env python3
"""
Ollama Setup Script for MFHelper
Downloads and configures Ollama + TinyLlama locally
"""
import os
import sys
import subprocess
import platform
import time
import requests

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_step(num, text):
    print(f"[{num}] {text}")

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_ollama_running():
    """Check if Ollama server is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        return response.status_code == 200
    except:
        return False

def install_ollama():
    """Install Ollama based on OS"""
    print_step(1, "Installing Ollama...")
    
    system = platform.system()
    
    if system == "Windows":
        print("  📥 Downloading Ollama for Windows...")
        print("  👉 Visit: https://ollama.ai/download")
        print("  👉 Or run: winget install Ollama.Ollama")
        input("\n  Press ENTER after installing Ollama...")
        
    elif system == "Darwin":  # macOS
        print("  📥 Installing via Homebrew...")
        os.system("brew install ollama")
        
    elif system == "Linux":
        print("  📥 Installing Ollama for Linux...")
        os.system("curl https://ollama.ai/install.sh | sh")
    
    # Verify installation
    if check_ollama_installed():
        print("  ✅ Ollama installed successfully!\n")
        return True
    else:
        print("  ❌ Ollama installation failed\n")
        return False

def start_ollama_server():
    """Start Ollama server in background"""
    print_step(2, "Starting Ollama server...")
    
    if check_ollama_running():
        print("  ✅ Ollama server already running at http://localhost:11434\n")
        return True
    
    print("  🚀 Starting Ollama server...")
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # On Windows, Ollama starts automatically
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        print("  ⏳ Waiting for server to start...")
        for i in range(30):
            time.sleep(1)
            if check_ollama_running():
                print("  ✅ Ollama server started!\n")
                return True
        
        print("  ❌ Ollama server failed to start\n")
        return False
        
    except Exception as e:
        print(f"  ❌ Error starting Ollama: {e}\n")
        return False

def download_tinyllama():
    """Download TinyLlama model"""
    print_step(3, "Downloading TinyLlama model (1.1GB)...")
    
    try:
        print("  📥 This will take 3-10 minutes depending on internet speed...")
        print("  ⏳ Downloading tinyllama model...\n")
        
        result = subprocess.run(
            ['ollama', 'pull', 'tinyllama'],
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n  ✅ TinyLlama downloaded successfully!\n")
            return True
        else:
            print("  ❌ Failed to download TinyLlama\n")
            return False
            
    except Exception as e:
        print(f"  ❌ Error downloading TinyLlama: {e}\n")
        return False

def test_ollama():
    """Test Ollama with a simple prompt"""
    print_step(4, "Testing Ollama setup...")
    
    try:
        print("  🧪 Testing with simple prompt...")
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'tinyllama',
                'prompt': 'What is mutual fund? (answer in one sentence)',
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()
            print(f"  ✅ TinyLlama Response: {answer}\n")
            return True
        else:
            print("  ❌ Failed to get response from TinyLlama\n")
            return False
            
    except Exception as e:
        print(f"  ❌ Test failed: {e}\n")
        return False

def create_env_file():
    """Create/update .env file for Ollama"""
    print_step(5, "Configuring MFHelper for Ollama...")
    
    env_path = os.path.join(os.path.dirname(__file__), '../.env')
    
    # Read existing .env if it exists
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Update/add Ollama configuration
    env_vars['AI_TYPE'] = 'ollama'
    env_vars['OLLAMA_BASE_URL'] = 'http://localhost:11434'
    env_vars['OLLAMA_MODEL'] = 'tinyllama'
    env_vars['AI_ENABLED'] = 'true'
    
    # Write back to .env
    try:
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"  ✅ Updated .env file with Ollama configuration\n")
        return True
    except Exception as e:
        print(f"  ❌ Failed to update .env: {e}\n")
        return False

def main():
    """Main setup flow"""
    print_header("🦙 MFHelper Ollama Setup")
    
    print("This script will:")
    print("  1. Install Ollama (if not already installed)")
    print("  2. Start Ollama server")
    print("  3. Download TinyLlama model (1.1GB)")
    print("  4. Test the setup")
    print("  5. Configure MFHelper\n")
    
    input("Press ENTER to start...")
    
    # Step 1: Check/Install Ollama
    if not check_ollama_installed():
        print_header("Step 1: Install Ollama")
        if not install_ollama():
            print("❌ Please install Ollama manually and run this script again")
            sys.exit(1)
    else:
        print("✅ Ollama already installed\n")
    
    # Step 2: Start Ollama
    print_header("Step 2: Start Ollama Server")
    if not start_ollama_server():
        print("⚠️  Could not start Ollama server automatically")
        print("👉 Please run 'ollama serve' in a separate terminal")
        input("Press ENTER once Ollama server is running...")
    
    # Verify server is running
    if not check_ollama_running():
        print("❌ Ollama server is not running")
        print("👉 Run: ollama serve")
        sys.exit(1)
    
    # Step 3: Download TinyLlama
    print_header("Step 3: Download TinyLlama Model")
    if not download_tinyllama():
        print("❌ Failed to download TinyLlama")
        sys.exit(1)
    
    # Step 4: Test Ollama
    print_header("Step 4: Test Ollama")
    if not test_ollama():
        print("⚠️  Test failed, but Ollama might still work")
        print("👉 Try restarting Ollama server")
    
    # Step 5: Configure MFHelper
    print_header("Step 5: Configure MFHelper")
    if not create_env_file():
        print("⚠️  Manual .env configuration needed")
        print("""
Add these to your .env file:
  AI_TYPE=ollama
  OLLAMA_BASE_URL=http://localhost:11434
  OLLAMA_MODEL=tinyllama
  AI_ENABLED=true
        """)
    
    # Success message
    print_header("✅ Setup Complete!")
    print("""
🎉 Ollama + TinyLlama is ready!

📝 Next Steps:
  1. Keep Ollama server running: ollama serve
  2. Start MFHelper backend: python -m uvicorn app.main:app
  3. Open http://localhost:8000

🚀 Your AI chatbot is now FREE and LOCAL!
   - No ChatGPT
   - No API costs
   - No internet needed
   - Completely private

💡 TinyLlama will handle:
   - General MF questions
   - Investment explanations
   - Strategy discussions

⚡ Rule-based system handles:
   - Portfolio analysis (instant!)
   - Cap ratios
   - Performance ranking
   - Rebalancing suggestions

Happy analyzing! 📊
    """)

if __name__ == '__main__':
    main()
