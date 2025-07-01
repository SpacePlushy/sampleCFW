# Manual Test Instructions for Balance Edit Issue

## Steps to Test:

1. Open http://localhost:8080/index.html in your browser
2. Click "Optimize Schedule" and wait for it to complete
3. Find Day 5 in the schedule
4. Click on the Balance cell for Day 5
5. Type `0` (just the number 0)
6. Click outside the cell or press Tab

## What to Check:

1. **Does the cell turn blue with a pencil icon?**
   - If NO: The edit tracking is broken
   - If YES: Continue to next step

2. **Does a floating panel appear saying "X cells edited"?**
   - If NO: The regenerate section isn't showing
   - If YES: Continue to next step

3. **Click "Regenerate with Manual Edits"**

4. **After regeneration, check:**
   - Is Day 5 still in the schedule?
   - Does Day 5 show balance $0.00?
   - Is Day 5 marked with "BALANCE EDIT"?
   - Are days 1-5 dimmed/unchanged?
   - Is the final balance close to $490.50?

## Console Debugging:

Open browser console (F12) and check:

```javascript
// After editing day 5 balance to 0:
window.editedCells

// Should show something like:
// Map(1) { '5-balance' => { day: 5, field: 'balance', originalValue: XX, newValue: 0 } }
```

## Report Back:

Please let me know:
1. At which step does it fail?
2. What do you see in the console?
3. Does the balance cell update visually when you type 0?