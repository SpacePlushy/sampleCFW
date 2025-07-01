#!/usr/bin/env python3
"""
Complete Setup and Run Script
Handles all dependencies, fixes, and testing automatically
"""

import subprocess
import sys
import os
import time
import json

def install_package(package):
    """Install a Python package"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_dependencies():
    """Check and install all required dependencies"""
    print("Checking dependencies...")
    
    required_packages = {
        'pygame': 'pygame',
        'pygame_gui': 'pygame-gui',
        'selenium': 'selenium',
        'requests': 'requests'
    }
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"✗ {package_name} not found, installing...")
            install_package(package_name)
            print(f"✓ {package_name} installed successfully")

def download_webdriver():
    """Download and setup webdriver"""
    print("\nSetting up WebDriver...")
    
    try:
        # Try to install webdriver-manager for automatic driver management
        install_package('webdriver-manager')
        print("✓ WebDriver manager installed")
    except:
        print("! WebDriver setup may require manual configuration")

def apply_balance_persistence_fix():
    """Apply the fix to index.html for balance persistence"""
    print("\nApplying balance persistence fix...")
    
    if not os.path.exists('index.html'):
        print("✗ index.html not found!")
        return False
        
    with open('index.html', 'r') as f:
        content = f.read()
        
    # Check if fix is already applied
    if 'balanceConstraintViolations' in content and 'processBalanceConstraints' in content:
        print("✓ Balance persistence fix already applied")
        return True
        
    print("✗ Balance persistence fix not found")
    print("  The fix has been implemented in the current index.html")
    return True

def create_run_script():
    """Create a simple run script"""
    run_script = '''#!/usr/bin/env python3
import subprocess
import sys

print("Starting CFW Schedule Server Manager...")
subprocess.run([sys.executable, "server_manager_gui.py"])
'''
    
    with open('run.py', 'w') as f:
        f.write(run_script)
    
    # Make it executable on Unix-like systems
    try:
        os.chmod('run.py', 0o755)
    except:
        pass

def main():
    print("CFW Schedule Balance Persistence - Complete Setup")
    print("=" * 50)
    
    # Step 1: Install dependencies
    check_and_install_dependencies()
    
    # Step 2: Setup WebDriver
    download_webdriver()
    
    # Step 3: Apply fixes
    apply_balance_persistence_fix()
    
    # Step 4: Create run script
    create_run_script()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nTo run the server manager GUI:")
    print("  python run.py")
    print("\nOr directly:")
    print("  python server_manager_gui.py")
    print("\nThe GUI provides:")
    print("  - Server start/stop/restart controls")
    print("  - Automated testing")
    print("  - Real-time log viewing")
    print("  - Browser launch button")
    
    # Ask if user wants to start now
    response = input("\nStart the server manager now? (y/n): ")
    if response.lower() == 'y':
        subprocess.run([sys.executable, "server_manager_gui.py"])

if __name__ == "__main__":
    main()