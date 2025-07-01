# Dual Fitness Strategy Implementation Plan

## Problem Statement
The current fitness function has a fundamental conflict: it tries to minimize work days in normal mode while maximizing earnings in crisis mode, leading to a "tug of war" where crisis mode solutions are penalized for overshooting the target balance.

## Root Cause Analysis
- **Line 935**: `workDayPenalty = workDays * 30` (minimize work)
- **Line 916**: `workDayPenalty = earningsShortfall * 10` (only penalize insufficient earnings)
- **Line 946**: `finalBalanceDiff * 20` (penalizes both under AND overshoot equally)

**The Conflict**: A 13-work-day solution earning $2000+ gets penalized more heavily than a 5-work-day solution with -$500 balance because `Math.abs(2000-490) > Math.abs(-500-490)`.

## 10x Solution: Dual Fitness Functions

### Design Philosophy
- **Normal Mode**: Minimize work days, hit target exactly
- **Crisis Mode**: Guarantee survival, overshoot is acceptable
- **Zero Compromise**: Each mode optimizes for its actual objective

### Implementation Strategy

#### Phase 1: Extract Normal Mode Fitness
```javascript
calculateNormalFitness(chromosome, balance, workDays, violations, totalEarnings, minBalance) {
    // Focus: Efficiency and precision
    const finalBalanceDiff = Math.abs(balance - this.targetEndingBalance);
    const workDayPenalty = workDays * 30; // Minimize work
    const consecutivePenalty = this.calculateConsecutivePenalty(chromosome);
    
    return violations * 5000 +           // Safety first
           finalBalanceDiff * 20 +       // Hit target exactly  
           workDayPenalty +              // Minimize work
           consecutivePenalty;           // Avoid burnout
}
```

#### Phase 2: Extract Crisis Mode Fitness  
```javascript
calculateCrisisFitness(chromosome, balance, workDays, violations, totalEarnings, minBalance) {
    // Focus: Survival and meeting minimum requirements
    const belowTargetPenalty = balance < this.targetEndingBalance ? 
        (this.targetEndingBalance - balance) * 1000 : 0; // Heavy penalty for insufficient funds
    const aboveTargetPenalty = balance > this.targetEndingBalance ?
        (balance - this.targetEndingBalance) * 0.1 : 0;  // Tiny penalty for overshoot
    
    const earningsShortfall = Math.max(0, this.requiredFlexNet - totalEarnings);
    const workDayDeficit = this.calculateWorkDayDeficit(chromosome);
    
    return violations * 10000 +          // Safety critical
           belowTargetPenalty +          // Must meet minimum
           aboveTargetPenalty +          // Overshoot OK
           earningsShortfall * 100 +     // Must earn enough
           workDayDeficit * 1000;        // Must work enough
}
```

#### Phase 3: Context Switch
```javascript
// Replace lines 902-951 with:
const fitness = inCrisisMode ? 
    this.calculateCrisisFitness(chromosome, balance, workDays, violations, totalEarnings, minBalance) :
    this.calculateNormalFitness(chromosome, balance, workDays, violations, totalEarnings, minBalance);
```

## Implementation Checklist

- [x] **Phase 1**: Create `calculateNormalFitness()` method ✅
- [x] **Phase 2**: Create `calculateCrisisFitness()` method ✅ 
- [x] **Phase 3**: Replace main fitness logic with context switch ✅
- [x] **Phase 4**: Add context-aware debug output ✅
- [x] **Phase 5**: Test day 17 scenario (should generate 11+ work days) ✅
- [x] **Phase 6**: Test normal scenario (should minimize work days) ✅

**IMPLEMENTATION COMPLETE** - Ready for user testing!

## Expected Outcomes

### Before Fix (Current State)
```
Day 17 balance = $10 → Crisis mode triggered
- Generates 13-work-day chromosomes correctly
- Fitness function penalizes them: fitness = 103B 
- Selects 5-work-day solution: fitness = 24B
- Result: -$529 final balance ❌
```

### After Fix (Target State)  
```
Day 17 balance = $10 → Crisis mode triggered
- Generates 13-work-day chromosomes correctly
- Crisis fitness rewards them: fitness = low
- Rejects 5-work-day solutions: fitness = high  
- Result: +$500+ final balance ✅
```

## Success Criteria
1. ✅ Crisis mode selects high-work solutions (11+ work days)
2. ✅ Normal mode continues to minimize work days
3. ✅ No more mathematical conflicts in fitness function
4. ✅ Clean separation of optimization objectives
5. ✅ Final balance positive in crisis scenarios

## Technical Notes
- **No refactoring required**: Just extract existing logic into focused functions
- **Backward compatible**: Normal mode behavior unchanged
- **Maintainable**: Clear separation of concerns
- **Debuggable**: Context-specific penalty breakdowns

---
*This document will be updated as implementation progresses*