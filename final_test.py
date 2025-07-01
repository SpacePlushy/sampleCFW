#!/usr/bin/env python3
"""
Final Balance Persistence Test
Complete working test with proper error handling
"""

import subprocess
import sys
import time
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8088

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
    print("\n🧪 Final Balance Persistence Test")
    print("=" * 50)
    
    # Start server
    httpd = start_server()
    time.sleep(1)
    print(f"✓ Server started on port {PORT}")
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Installing Playwright...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        # Launch browser (visible for debugging)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate
            page.goto(f"http://localhost:{PORT}/index.html")
            print("✓ Page loaded")
            
            # Set parameters and run optimization
            page.fill("#startingBalance", "90.50")
            page.fill("#targetBalance", "490.50") 
            page.fill("#minimumBalance", "0")
            page.fill("#populationSize", "50")
            page.fill("#generations", "100")
            
            page.click("#optimizeBtn")
            
            # Wait for optimization to complete
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=30000
            )
            print("✓ Optimization complete")
            
            # Wait a bit for table to render
            page.wait_for_timeout(1000)
            
            # Get the balance cell for day 10
            balance_cell = page.query_selector('td[data-day="10"][data-field="balance"]')
            if not balance_cell:
                raise Exception("Could not find balance cell for day 10")
                
            original_text = balance_cell.text_content()
            original_balance = float(original_text.replace('$', '').replace(',', ''))
            print(f"✓ Original balance for day 10: ${original_balance:.2f}")
            
            # Focus and edit the cell
            balance_cell.click()
            page.wait_for_timeout(100)
            
            # Clear and type new value
            page.keyboard.press("Control+a")
            page.keyboard.type("750")
            
            # Blur to trigger handleCellEdit
            page.keyboard.press("Tab")
            page.wait_for_timeout(500)
            
            print("✓ Edited balance to $750.00")
            
            # Verify edit was tracked
            edit_tracked = page.evaluate("() => window.editedCells && window.editedCells.has('10-balance')")
            
            if edit_tracked:
                print("✓ Edit was tracked in editedCells")
                
                # Check cascading
                cascade_count = 0
                for day in range(11, 31):
                    cell = page.query_selector(f'td[data-day="{day}"][data-field="balance"]')
                    if cell and "edited" in (cell.get_attribute("class") or ""):
                        cascade_count += 1
                        
                print(f"✓ {cascade_count} subsequent days cascaded")
            else:
                print("⚠️  Edit not tracked - trying direct method")
                
                # Try direct JavaScript call
                page.evaluate("""() => {
                    const cell = document.querySelector('td[data-day="10"][data-field="balance"]');
                    cell.textContent = '750';
                    window.handleCellEdit(cell);
                }""")
                
                edit_tracked = page.evaluate("() => window.editedCells.has('10-balance')")
                if not edit_tracked:
                    raise Exception("Edit still not tracked after direct call")
                    
            # Click regenerate button
            regenerate_visible = page.query_selector('#regenerateSection')
            if regenerate_visible and regenerate_visible.is_visible():
                print("✓ Regenerate section is visible")
                
                # Click regenerate
                page.click('.regenerate-btn')
                
                # Wait for regeneration
                page.wait_for_function(
                    "() => document.getElementById('progress').style.display === 'none'",
                    timeout=30000
                )
                print("✓ Regeneration complete")
            else:
                # Manually call regenerate
                print("⚠️  Regenerate button not visible, calling directly")
                page.evaluate("() => window.regenerateWithEdits()")
                page.wait_for_function(
                    "() => document.getElementById('progress').style.display === 'none'",
                    timeout=30000
                )
                
            # Check final balance
            page.wait_for_timeout(1000)
            final_cell = page.query_selector('td[data-day="10"][data-field="balance"]')
            final_text = final_cell.text_content()
            final_balance = float(final_text.replace('$', '').replace(',', ''))
            
            print(f"✓ Final balance for day 10: ${final_balance:.2f}")
            
            # Check if it persisted
            difference = abs(final_balance - 750)
            success = difference < 0.01
            
            print("\n" + "=" * 50)
            if success:
                print("✅ TEST PASSED!")
                print(f"   Balance persisted correctly at $750.00")
                print("   The fix is working properly!")
            else:
                print("❌ TEST FAILED!")
                print(f"   Expected: $750.00")
                print(f"   Got: ${final_balance:.2f}")
                print(f"   Difference: ${difference:.2f}")
                
                # Get debug info
                debug_info = page.evaluate("""() => {
                    const info = {
                        editedCellsSize: window.editedCells ? window.editedCells.size : 0,
                        hasBalanceConstraint: false
                    };
                    if (window.editedCells) {
                        window.editedCells.forEach((value, key) => {
                            if (key === '10-balance') {
                                info.hasBalanceConstraint = true;
                                info.constraintValue = value.newValue;
                            }
                        });
                    }
                    return info;
                }""")
                
                print(f"\nDebug info: {debug_info}")
                
            print("\nPress Enter to close browser...")
            input()
            
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            print("\nPress Enter to close browser...")
            input()
            
        finally:
            browser.close()
            httpd.shutdown()
            print("✓ Cleanup complete")

if __name__ == "__main__":
    main()