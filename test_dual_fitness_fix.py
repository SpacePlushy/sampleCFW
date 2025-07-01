#!/usr/bin/env python3
"""
Test the dual fitness function fix for the day 17 scenario
This should now generate 11+ work days instead of 5 work days
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re

def test_dual_fitness_crisis_mode():
    """Test that crisis mode now correctly selects high-work solutions"""
    
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load the page
        driver.get("file:///Users/spaceplushy/Desktop/sampleCFW/index.html")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
        
        print("=== DUAL FITNESS CRISIS MODE TEST ===")
        print("Testing Day 17 balance = $10 scenario...")
        
        # Click optimize with default settings first
        optimize_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Optimize Schedule')]")
        optimize_button.click()
        
        # Wait for initial optimization to complete
        wait.until(lambda driver: driver.find_element(By.CLASS_NAME, "results").is_displayed())
        time.sleep(2)  # Additional wait for completion
        
        print("✅ Initial optimization complete")
        
        # Find day 17 balance cell and edit it
        day_17_cell = driver.find_element(By.XPATH, "//tr[td[1][text()='17']]/td[5]")
        day_17_cell.click()
        
        # Clear and enter new value
        driver.execute_script("arguments[0].textContent = '10';", day_17_cell)
        
        # Press Enter to confirm edit
        driver.execute_script("""
            var event = new KeyboardEvent('keydown', {
                bubbles: true,
                cancelable: true,
                keyCode: 13
            });
            arguments[0].dispatchEvent(event);
        """, day_17_cell)
        
        print("✅ Day 17 balance edited to $10")
        
        # Click regenerate 
        regenerate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Regenerate')]")
        regenerate_button.click()
        
        # Wait for regeneration to complete
        time.sleep(5)  # Give time for genetic algorithm
        
        print("✅ Regeneration complete")
        
        # Get console logs to check for crisis mode and fitness debugging
        logs = driver.get_log('browser')
        console_output = [log['message'] for log in logs if log['level'] == 'INFO']
        
        # Check for crisis mode activation
        crisis_detected = any('CRISIS' in msg for msg in console_output)
        fitness_debug = [msg for msg in console_output if 'FITNESS BREAKDOWN - CRISIS MODE' in msg]
        
        print(f"\n=== CRISIS MODE DETECTION ===")
        print(f"Crisis mode detected: {'✅ YES' if crisis_detected else '❌ NO'}")
        print(f"Crisis fitness debug messages: {len(fitness_debug)}")
        
        # Count work days in final schedule (days 18-30)
        work_day_count = 0
        final_balance = None
        
        # Find all table rows and count work days from 18-30
        rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'schedule-table')]//tr[position()>1]")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 5:
                day_num = cells[0].text.strip()
                shifts = cells[1].text.strip()
                balance = cells[4].text.strip()
                
                try:
                    day = int(day_num)
                    if 18 <= day <= 30:  # Only count work days after balance edit
                        if shifts != "Off" and shifts != "-" and shifts != "":
                            work_day_count += 1
                            print(f"  Day {day}: {shifts}")
                    
                    if day == 30:  # Final balance
                        final_balance = balance
                        
                except ValueError:
                    continue
        
        print(f"\n=== RESULTS ANALYSIS ===")
        print(f"Work days (18-30): {work_day_count}/13 available")
        print(f"Final balance: {final_balance}")
        
        # Check for success criteria
        success_criteria = {
            "Crisis mode detected": crisis_detected,
            "High work count (≥10 days)": work_day_count >= 10,
            "Positive final balance": final_balance and '$' in final_balance and not '-' in final_balance
        }
        
        print(f"\n=== SUCCESS CRITERIA ===")
        all_passed = True
        for criterion, passed in success_criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{criterion}: {status}")
            if not passed:
                all_passed = False
        
        print(f"\n=== OVERALL RESULT ===")
        if all_passed:
            print("🎉 DUAL FITNESS FIX SUCCESSFUL!")
            print("Crisis mode now correctly selects high-work solutions!")
        else:
            print("⚠️  DUAL FITNESS FIX NEEDS FURTHER WORK")
            print("Crisis mode is not generating sufficient work days")
            
        # Print some recent console output for debugging
        print(f"\n=== RECENT CONSOLE OUTPUT ===")
        recent_logs = console_output[-10:] if console_output else []
        for log in recent_logs:
            print(f"  {log}")
            
        return all_passed, work_day_count, final_balance
        
    finally:
        driver.quit()

def test_normal_mode_still_works():
    """Test that normal mode (no balance edit) still minimizes work days"""
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("file:///Users/spaceplushy/Desktop/sampleCFW/index.html")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "button")))
        
        print("\n=== NORMAL MODE TEST ===")
        print("Testing default optimization (should minimize work days)...")
        
        # Click optimize with default settings
        optimize_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Optimize Schedule')]")
        optimize_button.click()
        
        # Wait for optimization to complete
        wait.until(lambda driver: driver.find_element(By.CLASS_NAME, "results").is_displayed())
        time.sleep(2)
        
        print("✅ Normal optimization complete")
        
        # Count total work days
        work_day_count = 0
        rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'schedule-table')]//tr[position()>1]")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                shifts = cells[1].text.strip()
                if shifts != "Off" and shifts != "-" and shifts != "":
                    work_day_count += 1
        
        print(f"Total work days in normal mode: {work_day_count}/30")
        
        # Normal mode should have fewer work days (efficient schedule)
        efficient = work_day_count <= 20  # Should be reasonably efficient
        
        print(f"Efficiency check: {'✅ PASS' if efficient else '❌ FAIL'} (≤20 work days)")
        
        return efficient, work_day_count
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing dual fitness function implementation...")
    
    # Test crisis mode
    crisis_success, crisis_work_days, crisis_balance = test_dual_fitness_crisis_mode()
    
    # Test normal mode
    normal_success, normal_work_days = test_normal_mode_still_works()
    
    print(f"\n" + "="*50)
    print(f"FINAL TEST RESULTS")
    print(f"="*50)
    print(f"Crisis Mode Test: {'✅ PASS' if crisis_success else '❌ FAIL'}")
    print(f"  - Work days: {crisis_work_days}/13 (after day 17 edit)")
    print(f"  - Final balance: {crisis_balance}")
    print(f"Normal Mode Test: {'✅ PASS' if normal_success else '❌ FAIL'}")
    print(f"  - Work days: {normal_work_days}/30 (full month)")
    
    if crisis_success and normal_success:
        print(f"\n🎉 ALL TESTS PASSED! Dual fitness implementation successful!")
    else:
        print(f"\n⚠️  Some tests failed. Implementation needs refinement.")