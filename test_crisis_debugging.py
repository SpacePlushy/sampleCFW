#!/usr/bin/env python3
"""
Test with enhanced crisis mode debugging
"""

import subprocess
import sys
import time
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8095

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
    print("\n🧪 Testing Crisis Mode with Enhanced Debugging")
    print("=" * 60)
    print("Testing: Day 17 balance = $10, enhanced crisis detection")
    
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
        context = browser.new_context()
        
        # Clear cache to ensure fresh JS
        context.clear_cookies()
        
        page = context.new_page()
        
        # Enable console logging
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[Browser] {msg.text}"))
        
        try:
            # Navigate with cache-busting
            page.goto(f"http://localhost:{PORT}/index.html?v={int(time.time())}")
            print("✓ Page loaded with cache-busting")
            
            # Set parameters and run optimization
            page.fill("#startingBalance", "90.50")
            page.fill("#targetBalance", "490.50") 
            page.fill("#minimumBalance", "0")
            page.fill("#populationSize", "200")
            page.fill("#generations", "500")
            
            page.click("#optimizeBtn")
            
            # Wait for optimization to complete
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=30000
            )
            print("✓ Initial optimization complete")
            
            # Edit day 17 balance to $10
            page.evaluate("""() => {
                const cell = document.querySelector('td[data-day="17"][data-field="balance"]');
                cell.textContent = '10';
                cell.dataset.original = cell.textContent.replace('$', '');
                window.handleCellEdit(cell);
                window.editedCells.set('17-balance', {
                    day: 17,
                    field: 'balance',
                    originalValue: parseFloat(cell.dataset.original),
                    newValue: 10
                });
                cell.textContent = '$10.00';
                cell.classList.add('edited');
                document.getElementById('regenerateSection').style.display = 'block';
            }""")
            
            print("✓ Set day 17 balance to $10.00")
            
            # Trigger regeneration
            page.evaluate("""() => {
                const manualConstraints = {};
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
                manualConstraints.balanceEditDay = 17;
                manualConstraints.newStartingBalance = 10;
                window.runOptimizationWithConstraints(manualConstraints, new Map());
            }""")
            
            # Wait for regeneration
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=60000
            )
            print("✓ Regeneration complete")
            
            # Analyze results
            rows = page.query_selector_all('.schedule-table tbody tr')
            work_days_after_17 = 0
            double_shifts = 0
            days_18_30_schedule = []
            
            for i in range(17, len(rows)):
                shifts_cell = rows[i].query_selector('td:nth-child(2)')
                balance_cell = rows[i].query_selector('td[data-field="balance"]')
                
                if shifts_cell and balance_cell:
                    shift_text = shifts_cell.text_content().strip()
                    balance_text = balance_cell.text_content().strip()
                    
                    day_info = f"Day {i+1}: {shift_text} -> {balance_text}"
                    days_18_30_schedule.append(day_info)
                    
                    if shift_text != 'Off':
                        work_days_after_17 += 1
                        if '+' in shift_text:
                            double_shifts += 1
            
            # Get final balance
            final_balance_cell = rows[-1].query_selector('td[data-field="balance"]')
            final_balance = float(final_balance_cell.text_content().replace('$', '').replace(',', ''))
            
            print(f"\n📊 RESULTS:")
            print(f"Work days after day 17: {work_days_after_17}/13 available")
            print(f"Double shift days: {double_shifts}")
            print(f"Final balance: ${final_balance:.2f}")
            print(f"Target: $490.50")
            print(f"Success: {abs(final_balance - 490.50) < 100}")
            
            print(f"\n📅 Days 18-30 Schedule:")
            for day_info in days_18_30_schedule:
                print(f"  {day_info}")
            
            # Print crisis mode console messages
            crisis_messages = [msg for msg in console_messages if "CRISIS" in msg or "EXTREME" in msg]
            if crisis_messages:
                print(f"\n🚨 Crisis Mode Messages:")
                for msg in crisis_messages[-10:]:  # Last 10 crisis messages
                    print(f"  {msg}")
            else:
                print(f"\n❌ No crisis mode messages found!")
                print(f"   Last 5 console messages:")
                for msg in console_messages[-5:]:
                    print(f"  {msg}")
                    
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