# Manual Test Instructions

## Test the Crisis Mode Fix

1. **Open your browser and navigate to the app**
2. **Open browser console** (F12 → Console tab)
3. **Run initial optimization** with default settings
4. **Edit day 17 balance to $10.00** 
5. **Click "Regenerate with Manual Edits"**
6. **Check console for these messages:**
   - `CRISIS MODE: Need $1694.99 in 13 days`
   - `CRISIS: Base work probability boosted to 0.95`
   - `CRISIS: Minimum work days needed: X out of 13 available`
   - `EXTREME DEFICIT MODE: Need 130.38 per day`

## Expected Results:

If crisis mode is working correctly, you should see:
- **11-13 work days** in the final schedule (days 18-30)
- **Many double shifts** (medium+medium, medium+large, etc.)
- **Final balance around $490-$500**
- **Crisis mode console messages**

## If Crisis Mode is NOT Working:

You'll see:
- **Only 5-6 work days** (like your current result)
- **Mostly single shifts or days off**
- **Final balance around -$500 to -$700**
- **No crisis mode console messages**

## Debug Steps:

1. If no crisis messages appear, the crisis detection isn't triggering
2. If crisis messages appear but results are still bad, chromosome generation isn't working
3. Clear browser cache (Ctrl+Shift+Delete) and try again
4. Try in an incognito window to ensure fresh JavaScript

Let me know what console messages you see!