#!/usr/bin/env python3
"""
Test the Day 17 scenario to verify earnings calculations are correct
"""

def test_day17_scenario():
    """Test the specific Day 17 scenario mentioned in the request"""
    
    # Day 17 balance = $10
    day_17_balance = 10.00
    
    # Expenses from day 18-30
    expenses = {
        22: 177,        # Cell Phone
        23: 40,         # Cat Food  
        24: 220,        # AI Subscription
        25: 139 + 10,   # Electric + Ring
        26: 112.50 + 20, # Groceries + Weed
        28: 13.49,      # iPhone AppleCare
        29: 30 + 40,    # Internet + Cat Food
        30: 1636        # Rent
    }
    
    total_expenses = sum(expenses.values())
    print(f"Total expenses from day 18-30: ${total_expenses}")
    
    # Mom deposit on day 25
    mom_deposit = 1356
    
    # Target ending balance
    target_balance = 490.50
    
    # Required earnings calculation
    required_earnings = total_expenses + target_balance - day_17_balance - mom_deposit
    print(f"Required earnings: ${total_expenses} + ${target_balance} - ${day_17_balance} - ${mom_deposit} = ${required_earnings}")
    
    # Available days for work (18-30)
    available_days = 30 - 17  # 13 days
    print(f"Available days for work (18-30): {available_days} days")
    
    # Required earnings per day
    earnings_per_day = required_earnings / available_days
    print(f"Required earnings per day: ${earnings_per_day:.2f}")
    
    # Shift earnings from the code (lines 364-369)
    shifts = {
        'large': {'gross': 94.50, 'net': 86.50},
        'medium': {'gross': 75.50, 'net': 67.50},
        'small': {'gross': 64.00, 'net': 56.00}
    }
    
    print("\nShift net earnings (from lines 364-369):")
    for shift, data in shifts.items():
        print(f"{shift}: ${data['net']} net (${data['gross']} gross)")
    
    print("\nDouble shift combinations:")
    double_shifts = {
        'large+large': shifts['large']['net'] + shifts['large']['net'],
        'medium+large': shifts['medium']['net'] + shifts['large']['net'],
        'large+medium': shifts['large']['net'] + shifts['medium']['net'],
        'medium+medium': shifts['medium']['net'] + shifts['medium']['net'],
        'small+large': shifts['small']['net'] + shifts['large']['net'],
        'small+medium': shifts['small']['net'] + shifts['medium']['net'],
        'small+small': shifts['small']['net'] + shifts['small']['net']
    }
    
    for combo, earnings in double_shifts.items():
        meets_requirement = "✓" if earnings >= earnings_per_day else "✗"
        print(f"{combo}: ${earnings} {meets_requirement}")
    
    print(f"\nAnalysis:")
    print(f"To meet ${earnings_per_day:.2f} per day requirement:")
    print(f"- Single large shift (${shifts['large']['net']}) is insufficient ✗")
    print(f"- Need double shifts like medium+large (${double_shifts['medium+large']}) ✓")
    print(f"- Or large+large (${double_shifts['large+large']}) ✓")
    
    # Test crisis mode detection logic
    large_shift_net = shifts['large']['net']
    crisis_threshold = available_days * large_shift_net
    print(f"\nCrisis mode detection:")
    print(f"Required earnings: ${required_earnings}")
    print(f"Crisis threshold (13 days * ${large_shift_net}): ${crisis_threshold}")
    print(f"In crisis mode: {'Yes' if required_earnings > crisis_threshold else 'No'}")
    
    # Check if algorithm should favor double shifts
    if required_earnings > crisis_threshold:
        print("✓ Algorithm should be in crisis mode and generate mostly double shifts")
    else:
        print("✗ Algorithm thinks single shifts are sufficient")
        print("This is the BUG - algorithm should detect this as needing double shifts")
    
    return required_earnings, earnings_per_day, crisis_threshold

if __name__ == "__main__":
    test_day17_scenario()