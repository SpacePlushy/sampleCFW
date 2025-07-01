# Manual Test Instructions for Crisis Mode Fixes

## Quick Test Steps:

1. **Open your browser and go to `index.html`**
2. **Open browser console** (F12 → Console tab)
3. **Run initial optimization** with default settings:
   - Starting Balance: $90.50
   - Target Balance: $490.50
   - Click "Optimize Schedule"
4. **Wait for optimization to complete**
5. **Edit day 17 balance**:
   - Click on day 17 balance cell
   - Change it to: `10`
   - Press Enter
6. **Click "Regenerate with Manual Edits"**
7. **Check the console output**

## Expected Results (After Fixes):

You should see in the console:

```
CRISIS MODE DEBUG INFO:
======================
Balance Edit: Day 17 set to $10.00
Available Days: 13 (days 18-30)
Required Earnings: $1694.99
Required Per Day: $130.38
Max Single Shifts: $1124.50
Crisis Mode Should Be: ACTIVE
Single Large Shift: $86.50 (INSUFFICIENT)
Double Large Needed: YES

WORK DAY ANALYSIS:
Work Days Generated: 11/13 available  
Minimum Needed: 11 days
Days Off: 2
Single Shifts: 0 | Double Shifts: 11
Total Earnings After Edit: $1694.99
Earnings Shortfall: $0.00
Work Intensity: 84.6% (should be 90%+ in crisis)
======================

FINAL OPTIMIZED SCHEDULE:
=========================
Day | Shifts       | Earnings | Expenses | End Balance | Notes
----+--------------+----------+----------+-------------+-------
 18 | large+large  | $173.00  | -        | $183.00     | WORK DAY
 19 | medium+large | $154.00  | $132.50  | $204.50     | WORK DAY
 20 | large+large  | $173.00  | -        | $377.50     | WORK DAY
 21 | medium+medium| $135.00  | -        | $512.50     | WORK DAY
 22 | Off          | -        | $177.00  | $335.50     | 
 23 | medium+large | $154.00  | $40.00   | $449.50     | WORK DAY
 24 | large+large  | $173.00  | $220.00  | $402.50     | WORK DAY
 25 | medium+medium| $135.00  | $149.00  | $1744.50    | Mom deposit WORK DAY
 26 | large+large  | $173.00  | $132.50  | $1785.00    | WORK DAY
 27 | medium+large | $154.00  | -        | $1939.00    | WORK DAY
 28 | large+large  | $173.00  | $13.49   | $2098.51    | WORK DAY
 29 | medium+medium| $135.00  | $70.00   | $2163.51    | WORK DAY
 30 | Off          | -        | $1636.00 | $527.51     | 

Final Balance: $527.51 | Work Days: 11 | Target: $490.50
=========================
```

## Key Success Indicators:

✅ **Crisis Mode Detected**: "Crisis Mode Should Be: ACTIVE"  
✅ **High Work Intensity**: 11 out of 13 work days (84.6%)  
✅ **Double Shifts Dominant**: Most days show "large+large", "medium+large", "medium+medium"  
✅ **Target Met**: Final balance around $490-$530 instead of -$529  
✅ **No Earnings Shortfall**: Should be $0.00 or very close  

## If Results Don't Match:

- **Check "Crisis Mode Should Be"**: Should say "ACTIVE"  
- **Check "Work Days Generated"**: Should be 10+ out of 13  
- **Check "Double Shifts"**: Should be 8+ out of total work days  
- **Check "Final Balance"**: Should be positive, around $490  

Try the test and let me know what output you get!