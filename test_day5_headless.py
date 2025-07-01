#!/usr/bin/env python3
"""
Test editing day 5 balance to $0 - Headless version
"""

import subprocess
import sys
import time
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8089

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
    print("\n🧪 Testing Day 5 Balance Edit to $0")
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
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"[Browser] {msg.text}"))
        
        try:
            # Navigate
            page.goto(f"http://localhost:{PORT}/index.html")
            print("✓ Page loaded")
            
            # Set parameters and run optimization
            page.fill("#startingBalance", "90.50")
            page.fill("#targetBalance", "490.50") 
            page.fill("#minimumBalance", "0")
            page.fill("#populationSize", "100")
            page.fill("#generations", "500")
            
            page.click("#optimizeBtn")
            
            # Wait for optimization to complete
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=30000
            )
            print("✓ Optimization complete")
            
            # Wait a bit for table to render
            page.wait_for_timeout(1000)
            
            # Get the balance cell for day 5
            balance_cell = page.query_selector('td[data-day="5"][data-field="balance"]')
            if not balance_cell:
                raise Exception("Could not find balance cell for day 5")
                
            original_text = balance_cell.text_content()
            original_balance = float(original_text.replace('$', '').replace(',', ''))
            print(f"✓ Original balance for day 5: ${original_balance:.2f}")
            
            # Click and edit the cell
            balance_cell.click()
            page.wait_for_timeout(100)
            
            # Clear and type new value
            page.keyboard.press("Control+a")
            page.keyboard.type("0")
            
            # Blur to trigger handleCellEdit
            page.keyboard.press("Tab")
            page.wait_for_timeout(500)
            
            print("✓ Edited balance to $0.00")
            
            # Check if edit was tracked
            edit_tracked = page.evaluate("() => window.editedCells && window.editedCells.has('5-balance')")
            if edit_tracked:
                print("✓ Edit was tracked in editedCells")
            else:
                print("❌ Edit was NOT tracked")
            
            # Click regenerate
            regenerate_visible = page.query_selector('#regenerateSection')
            if regenerate_visible and regenerate_visible.is_visible():
                print("✓ Regenerate section is visible")
                page.click('.regenerate-btn')
            else:
                print("❌ Regenerate section not visible, calling directly")
                page.evaluate("() => window.regenerateWithEdits()")
            
            # Wait for regeneration
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=30000
            )
            print("✓ Regeneration complete")
            
            # Wait for results to render
            page.wait_for_timeout(1000)
            
            # Check if day 5 appears and has correct balance
            day5_cell = page.query_selector('td[data-day="5"][data-field="balance"]')
            if not day5_cell:
                print("❌ Day 5 is missing from the schedule!")
            else:
                day5_balance = float(day5_cell.text_content().replace('$', ''))
                print(f"✓ Day 5 balance: ${day5_balance:.2f}")
                
                if abs(day5_balance) < 0.01:
                    print("✅ Day 5 balance correctly shows $0.00")
                else:
                    print(f"❌ Day 5 balance is incorrect: ${day5_balance:.2f}")
            
            # Check final balance
            rows = page.query_selector_all('.schedule-table tbody tr')
            if rows:
                last_row = rows[-1]
                final_balance_cell = last_row.query_selector('td[data-field="balance"]')
                final_balance = float(final_balance_cell.text_content().replace('$', ''))
                print(f"\n✓ Final balance (day 30): ${final_balance:.2f}")
                
                if abs(final_balance - 490.50) < 50:
                    print("✅ Final balance is close to target!")
                else:
                    print(f"❌ Final balance is far from target: ${abs(final_balance - 490.50):.2f} difference")
            
            # Count work days after day 5
            work_days_after_5 = 0
            for i in range(5, len(rows)):
                shifts_cell = rows[i].query_selector('td:nth-child(2)')
                if shifts_cell and shifts_cell.text_content().strip() != 'Off':
                    work_days_after_5 += 1
            
            print(f"\n✓ Work days after day 5: {work_days_after_5}")
            
            # Check for negative balances
            negative_days = []
            for i, row in enumerate(rows):
                balance_cell = row.query_selector('td[data-field="balance"]')
                if balance_cell:
                    balance = float(balance_cell.text_content().replace('$', ''))
                    if balance < 0:
                        negative_days.append(i + 1)
            
            if negative_days:
                print(f"⚠️  Days with negative balance: {negative_days}")
            else:
                print("✅ No negative balances")
                
            # Get debug info
            debug_info = page.evaluate("""() => {
                const info = {
                    editedCellsSize: window.editedCells ? window.editedCells.size : 0,
                    balanceEditDay: null,
                    newStartingBalance: null
                };
                if (window.editedCells) {
                    window.editedCells.forEach((value, key) => {
                        if (key === '5-balance') {
                            info.balanceEditValue = value.newValue;
                        }
                    });
                }
                return info;
            }""")
            
            print(f"\nDebug info: {debug_info}")
            
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