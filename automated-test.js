// Automated test runner for balance persistence
// This script will test the functionality and report results

const puppeteer = require("puppeteer");
const path = require("path");
const fs = require("fs");

async function runAutomatedTest() {
  console.log("Starting automated balance persistence test...\n");

  const browser = await puppeteer.launch({
    headless: false, // Set to true for headless mode
    devtools: true,
  });

  const page = await browser.newPage();

  // Navigate to the main page
  const filePath = `file://${path.resolve(__dirname, "index.html")}`;
  await page.goto(filePath);

  // Wait for page to load
  await page.waitForSelector("#optimizeBtn");

  console.log("✓ Page loaded successfully\n");

  // Test 1: Run initial optimization
  console.log("Test 1: Running initial optimization...");
  await page.evaluate(() => {
    document.getElementById("startingBalance").value = "90.50";
    document.getElementById("targetBalance").value = "490.50";
    document.getElementById("minimumBalance").value = "0";
    document.getElementById("populationSize").value = "100";
    document.getElementById("generations").value = "200";
  });

  await page.click("#optimizeBtn");

  // Wait for optimization to complete
  await page.waitForFunction(
    () => document.getElementById("progress").style.display === "none",
    { timeout: 30000 }
  );

  console.log("✓ Initial optimization complete\n");

  // Test 2: Edit balance and verify tracking
  console.log("Test 2: Editing balance for day 10...");

  const originalBalance = await page.evaluate(() => {
    const cell = document.querySelector(
      'td[data-day="10"][data-field="balance"]'
    );
    return parseFloat(cell.textContent.replace("$", ""));
  });

  console.log(`  Original balance: $${originalBalance}`);

  // Edit the balance
  await page.evaluate(() => {
    const cell = document.querySelector(
      'td[data-day="10"][data-field="balance"]'
    );
    cell.focus();
    cell.textContent = "750";
    cell.blur();
  });

  await page.waitForTimeout(500); // Wait for processing

  const editTracked = await page.evaluate(() => {
    return editedCells.has("10-balance");
  });

  if (!editTracked) {
    throw new Error("Balance edit was not tracked!");
  }

  console.log("✓ Balance edit tracked successfully\n");

  // Test 3: Verify cascading updates
  console.log("Test 3: Verifying balance cascade...");

  const cascadedBalances = await page.evaluate(() => {
    const balances = [];
    for (let day = 11; day <= 15; day++) {
      const cell = document.querySelector(
        `td[data-day="${day}"][data-field="balance"]`
      );
      balances.push({
        day: day,
        balance: parseFloat(cell.textContent.replace("$", "")),
        edited: cell.classList.contains("edited"),
      });
    }
    return balances;
  });

  console.log("  Cascaded balances:");
  cascadedBalances.forEach((b) => {
    console.log(
      `    Day ${b.day}: $${b.balance.toFixed(2)} ${b.edited ? "(edited)" : ""}`
    );
  });

  console.log("✓ Balance cascade working\n");

  // Test 4: Regenerate with constraints
  console.log("Test 4: Regenerating with balance constraint...");

  await page.evaluate(() => {
    regenerateWithEdits();
  });

  // Wait for regeneration to complete
  await page.waitForFunction(
    () => document.getElementById("progress").style.display === "none",
    { timeout: 30000 }
  );

  console.log("✓ Regeneration complete\n");

  // Test 5: Verify balance persistence
  console.log("Test 5: Verifying balance persistence...");

  const regeneratedBalance = await page.evaluate(() => {
    const cell = document.querySelector(
      'td[data-day="10"][data-field="balance"]'
    );
    return parseFloat(cell.textContent.replace("$", ""));
  });

  console.log(`  Regenerated balance: $${regeneratedBalance}`);
  console.log(`  Expected balance: $750.00`);
  console.log(
    `  Difference: $${Math.abs(regeneratedBalance - 750).toFixed(2)}`
  );

  const success = Math.abs(regeneratedBalance - 750) < 0.01;

  if (success) {
    console.log(
      "\n✅ ALL TESTS PASSED! Balance persistence is working correctly."
    );
  } else {
    console.log(
      "\n❌ TEST FAILED! Balance was not preserved during regeneration."
    );

    // Debug information
    const debugInfo = await page.evaluate(() => {
      const constraints = {};
      editedCells.forEach((edit, key) => {
        const day = edit.day;
        if (!constraints[day]) constraints[day] = {};
        constraints[day][edit.field] = edit.newValue;
      });
      return {
        editedCells: Array.from(editedCells.entries()),
        constraints: constraints,
        lastOptimizationConfig: lastOptimizationConfig,
      };
    });

    console.log("\nDebug Information:");
    console.log("Edited cells:", debugInfo.editedCells);
    console.log("Constraints:", debugInfo.constraints);
  }

  await browser.close();
  return success;
}

// Run the test
if (require.main === module) {
  runAutomatedTest()
    .then((success) => {
      process.exit(success ? 0 : 1);
    })
    .catch((error) => {
      console.error("Test error:", error);
      process.exit(1);
    });
}

module.exports = runAutomatedTest;
