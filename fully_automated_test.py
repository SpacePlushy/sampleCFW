#!/usr/bin/env python3
"""
Fully Automated Balance Persistence Test
No user interaction required - runs everything automatically
"""

import os
import sys
import time
import json
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# Try different ports if one is in use
PORTS_TO_TRY = [8082, 8083, 8084, 8085, 8086]

class SilentHTTPHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress server logs

def find_available_port():
    """Find an available port"""
    import socket
    for port in PORTS_TO_TRY:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError("No available ports found")

def start_server(port):
    """Start HTTP server on given port"""
    handler = SilentHTTPHandler
    httpd = socketserver.TCPServer(("", port), handler)
    httpd.allow_reuse_address = True
    
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    
    return httpd

def run_playwright_test(port):
    """Run test using Playwright (lighter than Selenium)"""
    try:
        # Install playwright if needed
        try:
            import playwright
        except ImportError:
            print("Installing Playwright...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            
        from playwright.sync_api import sync_playwright
        
        print("\n🎭 Running automated test with Playwright...")
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to page
            page.goto(f"http://localhost:{port}/index.html")
            print("✓ Page loaded")
            
            # Set initial values
            page.fill("#startingBalance", "90.50")
            page.fill("#targetBalance", "490.50")
            page.fill("#minimumBalance", "0")
            page.fill("#populationSize", "100")
            page.fill("#generations", "200")
            print("✓ Parameters set")
            
            # Run optimization
            page.click("#optimizeBtn")
            page.wait_for_selector("#scheduleBody tr", timeout=30000)
            print("✓ Initial optimization complete")
            
            # Get original balance for day 10
            original_balance_text = page.text_content('td[data-day="10"][data-field="balance"]')
            original_balance = float(original_balance_text.replace('$', ''))
            print(f"✓ Original balance for day 10: ${original_balance:.2f}")
            
            # Edit the balance
            balance_cell = page.locator('td[data-day="10"][data-field="balance"]')
            balance_cell.click()
            # Triple-click to select all text
            balance_cell.click(click_count=3)
            page.keyboard.type("750")
            # Trigger blur event by clicking elsewhere
            page.locator('body').click()
            page.wait_for_timeout(500)
            print("✓ Balance edited to $750.00")
            
            # Check if edit was tracked
            edit_tracked = page.evaluate("() => window.editedCells && window.editedCells.has('10-balance')")
            if not edit_tracked:
                raise Exception("Balance edit was not tracked!")
            print("✓ Edit tracked in system")
            
            # Regenerate
            page.evaluate("() => window.regenerateWithEdits()")
            page.wait_for_function("() => document.getElementById('progress').style.display === 'none'", timeout=30000)
            print("✓ Regeneration complete")
            
            # Check regenerated balance
            regenerated_balance_text = page.text_content('td[data-day="10"][data-field="balance"]')
            regenerated_balance = float(regenerated_balance_text.replace('$', ''))
            print(f"✓ Regenerated balance: ${regenerated_balance:.2f}")
            
            # Verify persistence
            difference = abs(regenerated_balance - 750)
            success = difference < 0.01
            
            browser.close()
            
            return success, regenerated_balance
            
    except Exception as e:
        print(f"❌ Playwright test error: {e}")
        return False, 0

def run_requests_test(port):
    """Simple HTTP test to verify server is working"""
    try:
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
        
    try:
        response = requests.get(f"http://localhost:{port}/index.html", timeout=5)
        if response.status_code == 200 and "Monthly Financial Schedule" in response.text:
            print("✓ Server is serving files correctly")
            return True
    except:
        pass
    return False

def verify_fix_in_code():
    """Verify the fix is present in the code"""
    if not os.path.exists('index.html'):
        return False, "index.html not found"
        
    with open('index.html', 'r') as f:
        content = f.read()
        
    required_elements = {
        'balanceConstraintViolations': 'Balance constraint violations tracking',
        'processBalanceConstraints': 'Balance constraint processing method',
        'fixedBalance': 'Fixed balance constraint support',
        'recalculateBalanceFromDay': 'Balance cascade from specific day'
    }
    
    missing = []
    found = []
    
    for element, description in required_elements.items():
        if element in content:
            found.append(f"✓ {description}")
        else:
            missing.append(f"✗ {description} ({element})")
            
    return len(missing) == 0, found, missing

def main():
    print("\n🔧 CFW Schedule Balance Persistence - Automated Test")
    print("=" * 60)
    
    # Step 1: Verify code
    print("\n📝 Verifying balance persistence implementation...")
    code_ok, found, missing = verify_fix_in_code()
    
    if found:
        for item in found:
            print(f"  {item}")
            
    if not code_ok:
        print("\n❌ Missing required code elements:")
        for item in missing:
            print(f"  {item}")
        print("\n⚠️  The balance persistence fix may not be fully implemented.")
        return 1
    
    print("\n✅ All required code elements found!")
    
    # Step 2: Find available port
    try:
        port = find_available_port()
        print(f"\n🌐 Using port {port}")
    except RuntimeError:
        print("❌ No available ports found!")
        return 1
    
    # Step 3: Start server
    print(f"🚀 Starting server...")
    httpd = start_server(port)
    time.sleep(1)
    
    # Step 4: Verify server
    if run_requests_test(port):
        print("✅ Server is running correctly")
    else:
        print("❌ Server verification failed")
        httpd.shutdown()
        return 1
    
    # Step 5: Run automated test
    try:
        success, final_balance = run_playwright_test(port)
        
        print("\n" + "=" * 60)
        if success:
            print("✅ BALANCE PERSISTENCE TEST PASSED!")
            print(f"   The edited balance of $750.00 was preserved.")
            print(f"   Final balance: ${final_balance:.2f}")
            print("\n🎉 The fix is working correctly!")
            result = 0
        else:
            print("❌ BALANCE PERSISTENCE TEST FAILED!")
            print(f"   Expected: $750.00")
            print(f"   Got: ${final_balance:.2f}")
            print("\n⚠️  The balance did not persist after regeneration.")
            result = 1
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        result = 1
    
    # Cleanup
    httpd.shutdown()
    print("\n✓ Server stopped")
    
    return result

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)