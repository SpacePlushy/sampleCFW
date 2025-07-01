#!/usr/bin/env python3
"""
Test editing day 17 balance to $10 - Manual style
"""

import subprocess
import sys
import time
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8092

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
    print("\n🧪 Manual Test: Day 17 Balance Edit to $10")
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
        # Launch browser
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
            
            # Manually set the balance to $10 using JavaScript
            page.evaluate("""() => {
                // Find the cell
                const cell = document.querySelector('td[data-day="17"][data-field="balance"]');
                
                // Simulate manual edit
                cell.textContent = '10';
                cell.dataset.original = cell.textContent.replace('$', '');
                
                // Call handleCellEdit
                window.handleCellEdit(cell);
                
                // Set the editedCells directly to ensure it's tracked
                window.editedCells.set('17-balance', {
                    day: 17,
                    field: 'balance',
                    originalValue: parseFloat(cell.dataset.original),
                    newValue: 10
                });
                
                // Update the cell display
                cell.textContent = '$10.00';
                cell.classList.add('edited');
                
                // Show regenerate section
                document.getElementById('regenerateSection').style.display = 'block';
            }""")
            
            print("✓ Manually set day 17 balance to $10.00")
            
            # Manually trigger regeneration with correct constraints
            page.evaluate("""() => {
                const manualConstraints = {};
                
                // Lock days 1-17
                const rows = document.querySelectorAll('.schedule-table tbody tr');
                for (let d = 1; d <= 17; d++) {
                    const row = rows[d - 1];
                    const earningsCell = row.querySelector(`td[data-field="earnings"]`);
                    const earnings = parseFloat(earningsCell.textContent.replace('$', '')) || 0;
                    
                    if (earnings > 0) {
                        const shiftsCell = row.querySelector('td:nth-child(2)');
                        const shiftType = shiftsCell.textContent.trim().toLowerCase();
                        if (shiftType !== 'off') {
                            manualConstraints[d] = { shifts: shiftType };
                        }
                    }
                }
                
                // Set balance constraint
                manualConstraints.balanceEditDay = 17;
                manualConstraints.newStartingBalance = 10;  // This is the key - $10, not $101264
                
                // Run optimization
                window.runOptimizationWithConstraints(manualConstraints, new Map());
            }""")
            
            # Wait for regeneration
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=60000
            )
            print("✓ Regeneration complete")
            
            # Wait for results to render
            page.wait_for_timeout(1000)
            
            # Check results
            rows = page.query_selector_all('.schedule-table tbody tr')
            
            # Count work days after day 17
            work_days_after_17 = 0
            for i in range(17, len(rows)):
                shifts_cell = rows[i].query_selector('td:nth-child(2)')
                if shifts_cell and shifts_cell.text_content().strip() != 'Off':
                    work_days_after_17 += 1
                    print(f"  Day {i+1}: {shifts_cell.text_content().strip()}")
            
            print(f"\n✓ Work days after day 17: {work_days_after_17}")
            
            # Check final balance
            if rows:
                last_row = rows[-1]
                final_balance_cell = last_row.query_selector('td[data-field="balance"]')
                final_balance = float(final_balance_cell.text_content().replace('$', ''))
                print(f"✓ Final balance (day 30): ${final_balance:.2f}")
                
                if abs(final_balance - 490.50) < 50:
                    print("✅ Final balance is close to target!")
                else:
                    print(f"❌ Final balance is far from target: ${abs(final_balance - 490.50):.2f} difference")
                    
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