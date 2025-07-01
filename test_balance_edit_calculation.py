#!/usr/bin/env python3
"""
Test the balance edit calculation logic to see if it's correctly calculating required earnings
"""

def test_balance_edit_calculation():
    """Test the balance edit calculation from line 437-443"""
    
    # Simulate the balance edit scenario
    balance_edit_day = 17
    new_starting_balance = 10.00  # Day 17 balance set to $10
    target_ending_balance = 490.50
    
    # Expenses by day (from the code)
    expenses_by_day = [0] * 31  # Index 0 unused, days 1-30
    
    # Add the specific expenses mentioned in the request (days 18-30)
    expenses_by_day[22] = 177        # Cell Phone
    expenses_by_day[23] = 40         # Cat Food  
    expenses_by_day[24] = 220        # AI Subscription
    expenses_by_day[25] = 139 + 10   # Electric + Ring
    expenses_by_day[26] = 112.50 + 20 # Groceries + Weed
    expenses_by_day[28] = 13.49      # iPhone AppleCare
    expenses_by_day[29] = 30 + 40    # Internet + Cat Food
    expenses_by_day[30] = 1636       # Rent
    
    # Mom deposits by day
    deposits_by_day = [0] * 31
    deposits_by_day[25] = 1356  # Mom deposit on day 25
    
    # Calculate relevant expenses (from day AFTER balance edit to day 30)
    relevant_expenses = 0
    relevant_mom_income = 0
    
    for d in range(balance_edit_day + 1, 31):  # Days 18-30
        relevant_expenses += expenses_by_day[d]
        relevant_mom_income += deposits_by_day[d]
    
    print(f"Balance edit day: {balance_edit_day}")
    print(f"New starting balance: ${new_starting_balance}")
    print(f"Target ending balance: ${target_ending_balance}")
    print(f"Relevant expenses (days {balance_edit_day + 1}-30): ${relevant_expenses}")
    print(f"Relevant mom income (days {balance_edit_day + 1}-30): ${relevant_mom_income}")
    
    # This is the calculation from line 443
    required_flex_net = relevant_expenses + target_ending_balance - new_starting_balance - relevant_mom_income
    
    print(f"Required earnings calculation (line 443):")
    print(f"${relevant_expenses} + ${target_ending_balance} - ${new_starting_balance} - ${relevant_mom_income} = ${required_flex_net}")
    
    # Check crisis mode detection (line 606)
    available_days = 30 - balance_edit_day  # 13 days
    large_shift_net = 86.50
    crisis_threshold = available_days * large_shift_net
    
    print(f"\nCrisis mode detection:")
    print(f"Available days: {available_days}")
    print(f"Required earnings: ${required_flex_net}")
    print(f"Crisis threshold (single large per day): ${crisis_threshold}")
    print(f"In crisis mode: {'Yes' if required_flex_net > crisis_threshold else 'No'}")
    
    # Check earnings per day requirement
    earnings_per_day = required_flex_net / available_days
    print(f"Required earnings per day: ${earnings_per_day:.2f}")
    
    # Verify this matches our manual calculation
    manual_calculation = 1562.49  # From our previous test
    print(f"\nVerification:")
    print(f"Algorithm calculation: ${required_flex_net}")
    print(f"Manual calculation: ${manual_calculation}")
    print(f"Match: {'Yes' if abs(required_flex_net - manual_calculation) < 1 else 'No'}")
    
    return required_flex_net, crisis_threshold, earnings_per_day

if __name__ == "__main__":
    test_balance_edit_calculation()