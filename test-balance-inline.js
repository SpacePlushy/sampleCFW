// Test script to verify balance persistence
// Run this in the browser console after loading index.html

async function testBalancePersistence() {
    console.log('=== Balance Persistence Test ===');
    
    // First, run an initial optimization
    console.log('1. Running initial optimization...');
    document.getElementById('startingBalance').value = '90.50';
    document.getElementById('targetBalance').value = '490.50';
    document.getElementById('minimumBalance').value = '0';
    document.getElementById('populationSize').value = '50';
    document.getElementById('generations').value = '100';
    
    // Click optimize
    await runOptimization();
    
    // Wait for optimization to complete
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    console.log('2. Initial optimization complete');
    
    // Now edit a balance cell
    console.log('3. Editing balance for day 10...');
    const balanceCell = document.querySelector('td[data-day="10"][data-field="balance"]');
    const originalBalance = parseFloat(balanceCell.textContent.replace('$', ''));
    console.log(`   Original balance: $${originalBalance}`);
    
    // Edit the balance
    balanceCell.focus();
    balanceCell.textContent = '750';
    balanceCell.blur();
    
    // Wait for processing
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const newBalance = parseFloat(balanceCell.textContent.replace('$', ''));
    console.log(`   New balance: $${newBalance}`);
    
    // Check if edit was tracked
    console.log('4. Checking if edit was tracked...');
    console.log(`   Edited cells count: ${editedCells.size}`);
    const balanceEdit = editedCells.get('10-balance');
    if (balanceEdit) {
        console.log(`   ✓ Balance edit tracked: $${balanceEdit.originalValue} → $${balanceEdit.newValue}`);
    } else {
        console.log('   ✗ Balance edit NOT tracked!');
        return false;
    }
    
    // Now regenerate
    console.log('5. Regenerating with constraints...');
    await regenerateWithEdits();
    
    // Wait for regeneration to complete
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    console.log('6. Regeneration complete, checking results...');
    
    // Check if balance was preserved
    const regeneratedBalanceCell = document.querySelector('td[data-day="10"][data-field="balance"]');
    const regeneratedBalance = parseFloat(regeneratedBalanceCell.textContent.replace('$', ''));
    
    console.log(`   Regenerated balance: $${regeneratedBalance}`);
    console.log(`   Expected balance: $750.00`);
    
    if (Math.abs(regeneratedBalance - 750) < 0.01) {
        console.log('✅ TEST PASSED: Balance was preserved during regeneration!');
        return true;
    } else {
        console.log('❌ TEST FAILED: Balance was NOT preserved!');
        console.log(`   Difference: $${Math.abs(regeneratedBalance - 750).toFixed(2)}`);
        return false;
    }
}

// Run the test
console.log('To run the balance persistence test, call: testBalancePersistence()');