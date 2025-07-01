#!/usr/bin/env python3
"""
Test the loading state functionality - ensure table only shows final result
"""

import subprocess
import sys
import time
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8094

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
    print("\n🧪 Testing Loading State Display")
    print("=" * 40)
    print("Testing: Only final result shown, loading messages during processing")
    
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
        # Launch browser (non-headless to see the loading states)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate
            page.goto(f"http://localhost:{PORT}/index.html")
            print("✓ Page loaded")
            
            # Set quick parameters for faster testing
            page.fill("#startingBalance", "90.50")
            page.fill("#targetBalance", "490.50") 
            page.fill("#minimumBalance", "0")
            page.fill("#populationSize", "50")   # Smaller for faster testing
            page.fill("#generations", "100")     # Fewer generations
            
            print("✓ Starting optimization...")
            page.click("#optimizeBtn")
            
            # Check that results div is hidden during optimization
            results_visible = page.is_visible("#results")
            progress_visible = page.is_visible("#progress")
            
            print(f"  During optimization - Results visible: {results_visible}")
            print(f"  During optimization - Progress visible: {progress_visible}")
            
            # Wait for optimization to complete
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=30000
            )
            print("✓ Optimization complete")
            
            # Check loading message appears
            loading_message = page.text_content("#scheduleBody")
            if "Building optimized schedule" in loading_message:
                print("✓ Loading message shown correctly")
            else:
                print(f"❌ No loading message found. Table content: {loading_message[:100]}...")
            
            # Wait a moment for the final table to appear
            page.wait_for_timeout(200)
            
            # Check final result
            final_rows = page.query_selector_all('.schedule-table tbody tr')
            if len(final_rows) == 30:  # Should have 30 days
                print(f"✓ Final table has {len(final_rows)} rows (complete schedule)")
                
                # Check that we have actual data, not loading message
                first_row_text = final_rows[0].text_content()
                if "Building optimized schedule" not in first_row_text:
                    print("✓ Table shows actual schedule data")
                else:
                    print("❌ Table still shows loading message")
                    
            else:
                print(f"❌ Final table has {len(final_rows)} rows (expected 30)")
            
            # Now test regeneration loading
            print("\n🔄 Testing regeneration loading...")
            
            # Edit a balance
            balance_cell = page.query_selector('td[data-day="10"][data-field="balance"]')
            if balance_cell:
                balance_cell.click()
                page.keyboard.press("Control+a")
                page.keyboard.type("100")
                page.keyboard.press("Tab")
                page.wait_for_timeout(500)
                
                print("✓ Edited day 10 balance")
                
                # Click regenerate
                regenerate_btn = page.query_selector('.regenerate-btn')
                if regenerate_btn:
                    regenerate_btn.click()
                    
                    # Check for regeneration loading message
                    page.wait_for_timeout(100)
                    regeneration_loading = page.text_content("#scheduleBody")
                    if "Regenerating schedule with your edits" in regeneration_loading:
                        print("✓ Regeneration loading message shown")
                    else:
                        print(f"❌ No regeneration loading message. Content: {regeneration_loading[:100]}...")
                    
                    # Wait for regeneration to complete
                    page.wait_for_function(
                        "() => document.getElementById('progress').style.display === 'none'",
                        timeout=30000
                    )
                    print("✓ Regeneration complete")
                    
                else:
                    print("❌ Regenerate button not found")
            else:
                print("❌ Could not find balance cell to edit")
            
            print(f"\n✅ Loading state test completed!")
            print(f"   Check the browser window to verify loading states appeared correctly")
            
            # Keep browser open for manual inspection
            input("Press Enter to close the browser...")
                    
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            browser.close()
            httpd.shutdown()
            print("\n✓ Cleanup complete")

if __name__ == "__main__":
    main()