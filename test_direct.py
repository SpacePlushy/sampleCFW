#!/usr/bin/env python3
"""
Direct JavaScript Test for Balance Persistence
Tests the functions directly via page.evaluate
"""

import subprocess
import sys
import time
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8087

def start_server():
    handler = SimpleHTTPRequestHandler
    handler.log_message = lambda *args: None
    httpd = socketserver.TCPServer(("", PORT), handler)
    httpd.allow_reuse_address = True
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd

def main():
    print("\n🔬 Direct Balance Persistence Test")
    print("=" * 50)
    
    # Start server
    httpd = start_server()
    time.sleep(1)
    print(f"✓ Server started on port {PORT}")
    
    try:
        # Install playwright if needed
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("Installing Playwright...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Show browser for debugging
            page = browser.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: print(f"[Browser] {msg.text}"))
            
            # Navigate
            page.goto(f"http://localhost:{PORT}/index.html")
            print("✓ Page loaded")
            
            # Run optimization
            page.evaluate("""
                document.getElementById('startingBalance').value = '90.50';
                document.getElementById('targetBalance').value = '490.50';
                document.getElementById('minimumBalance').value = '0';
                document.getElementById('populationSize').value = '50';
                document.getElementById('generations').value = '100';
            """)
            
            page.click("#optimizeBtn")
            page.wait_for_selector("#scheduleBody tr", timeout=30000)
            print("✓ Optimization complete")
            
            # Get original balance
            original = page.evaluate("""
                const cell = document.querySelector('td[data-day="10"][data-field="balance"]');
                return parseFloat(cell.textContent.replace('$', ''));
            """)
            print(f"✓ Original balance: ${original:.2f}")
            
            # Directly call handleCellEdit
            page.evaluate("""
                const cell = document.querySelector('td[data-day="10"][data-field="balance"]');
                cell.textContent = '750';
                handleCellEdit(cell);
            """)
            print("✓ Called handleCellEdit directly")
            
            # Check if tracked
            tracked = page.evaluate("editedCells.has('10-balance')")
            if tracked:
                print("✓ Edit was tracked!")
                edit_info = page.evaluate("editedCells.get('10-balance')")
                print(f"  Original: ${edit_info['originalValue']:.2f}")
                print(f"  New: ${edit_info['newValue']:.2f}")
            else:
                print("❌ Edit NOT tracked")
                
            # Check cascading
            cascade_count = page.evaluate("""
                let count = 0;
                for (let day = 11; day <= 30; day++) {
                    const cell = document.querySelector(`td[data-day="${day}"][data-field="balance"]`);
                    if (cell && cell.classList.contains('edited')) count++;
                }
                return count;
            """)
            print(f"✓ {cascade_count} days cascaded")
            
            # Regenerate
            page.evaluate("regenerateWithEdits()")
            page.wait_for_function("document.getElementById('progress').style.display === 'none'", timeout=30000)
            print("✓ Regeneration complete")
            
            # Check final balance
            final = page.evaluate("""
                const cell = document.querySelector('td[data-day="10"][data-field="balance"]');
                return parseFloat(cell.textContent.replace('$', ''));
            """)
            print(f"✓ Final balance: ${final:.2f}")
            
            success = abs(final - 750) < 0.01
            
            if success:
                print("\n✅ TEST PASSED! Balance persisted correctly.")
            else:
                print(f"\n❌ TEST FAILED! Expected $750.00, got ${final:.2f}")
                
                # Debug info
                constraints = page.evaluate("""
                    const result = {};
                    editedCells.forEach((value, key) => {
                        result[key] = value;
                    });
                    return result;
                """)
                print("\nDebug - Edited cells:", constraints)
            
            # Keep browser open for inspection
            input("\nPress Enter to close browser...")
            browser.close()
            
    finally:
        httpd.shutdown()
        print("✓ Server stopped")

if __name__ == "__main__":
    main()