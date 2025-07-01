#!/usr/bin/env python3
"""
Test that natural evolution can solve day 17 balance = $10 scenario
WITHOUT aggressive chromosome seeding
"""

import subprocess
import sys
import time
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8093

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
    print("\n🧪 Testing Natural Evolution (No Aggressive Seeding)")
    print("=" * 60)
    print("Testing: Day 17 balance = $10, need $1695 in 13 days")
    print("Expected: Algorithm should naturally evolve high-work solutions")
    
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
            page.fill("#populationSize", "200")  # Larger population for better diversity
            page.fill("#generations", "750")     # More generations for evolution
            
            page.click("#optimizeBtn")
            
            # Wait for optimization to complete
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=45000
            )
            print("✓ Initial optimization complete")
            
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
                manualConstraints.newStartingBalance = 10;
                
                // Run optimization
                window.runOptimizationWithConstraints(manualConstraints, new Map());
            }""")
            
            # Wait for regeneration
            page.wait_for_function(
                "() => document.getElementById('progress').style.display === 'none'",
                timeout=90000  # Extra time for evolution to work
            )
            print("✓ Natural evolution regeneration complete")
            
            # Wait for results to render
            page.wait_for_timeout(1000)
            
            # Analyze results
            rows = page.query_selector_all('.schedule-table tbody tr')
            
            # Count work days after day 17
            work_days_after_17 = 0
            double_shifts = 0
            work_schedule = []
            
            for i in range(17, len(rows)):
                shifts_cell = rows[i].query_selector('td:nth-child(2)')
                if shifts_cell:
                    shift_text = shifts_cell.text_content().strip()
                    if shift_text != 'Off':
                        work_days_after_17 += 1
                        work_schedule.append(f"Day {i+1}: {shift_text}")
                        if '+' in shift_text:
                            double_shifts += 1
            
            print(f"\n📊 RESULTS:")
            print(f"Work days after day 17: {work_days_after_17}/13 available")
            print(f"Double shift days: {double_shifts}")
            print(f"Work intensity: {work_days_after_17/13*100:.1f}%")
            
            # Show work schedule
            if work_schedule:
                print(f"\nWork schedule:")
                for work_day in work_schedule:
                    print(f"  {work_day}")
            
            # Check final balance
            if rows:
                last_row = rows[-1]
                final_balance_cell = last_row.query_selector('td[data-field="balance"]')
                final_balance = float(final_balance_cell.text_content().replace('$', ''))
                target_balance = 490.50
                balance_diff = abs(final_balance - target_balance)
                
                print(f"\n💰 Final balance: ${final_balance:.2f}")
                print(f"Target balance: ${target_balance:.2f}")
                print(f"Difference: ${balance_diff:.2f}")
                
                # Evaluate success
                success_criteria = {
                    'work_days': work_days_after_17 >= 10,  # Need at least 10 work days
                    'double_shifts': double_shifts >= 5,    # Need several double shifts
                    'target_met': balance_diff < 50         # Within $50 of target
                }
                
                print(f"\n🎯 SUCCESS CRITERIA:")
                print(f"✓ Work days ≥ 10: {'✅' if success_criteria['work_days'] else '❌'} ({work_days_after_17})")
                print(f"✓ Double shifts ≥ 5: {'✅' if success_criteria['double_shifts'] else '❌'} ({double_shifts})")
                print(f"✓ Target met (±$50): {'✅' if success_criteria['target_met'] else '❌'} (${balance_diff:.2f})")
                
                if all(success_criteria.values()):
                    print(f"\n🎉 SUCCESS! Natural evolution solved the extreme scenario!")
                    print(f"   The fitness function redesign allows the GA to naturally")
                    print(f"   discover high-work solutions without aggressive seeding.")
                else:
                    print(f"\n❌ FAILURE! Natural evolution couldn't solve extreme scenario.")
                    failed_criteria = [k for k, v in success_criteria.items() if not v]
                    print(f"   Failed criteria: {', '.join(failed_criteria)}")
                    print(f"   The genetic algorithm still needs improvement.")
                    
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