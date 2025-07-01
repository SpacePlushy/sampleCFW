const puppeteer = require('puppeteer');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Configuration
const PORT = 8080;
const BASE_URL = `http://localhost:${PORT}`;
const TIMEOUT = 30000; // 30 seconds timeout for operations

// Simple HTTP server to serve static files
function createServer() {
  return http.createServer((req, res) => {
    let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
    
    // Determine content type
    const ext = path.extname(filePath);
    const contentType = {
      '.html': 'text/html',
      '.js': 'application/javascript',
      '.css': 'text/css',
      '.json': 'application/json'
    }[ext] || 'text/plain';

    fs.readFile(filePath, (err, content) => {
      if (err) {
        res.writeHead(404);
        res.end('File not found');
      } else {
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(content);
      }
    });
  });
}

async function runTest() {
  let server;
  let browser;
  let exitCode = 0;

  try {
    // Step 1: Start local HTTP server
    console.log('1. Starting local HTTP server...');
    server = createServer();
    await new Promise((resolve) => {
      server.listen(PORT, () => {
        console.log(`   ✓ Server running at ${BASE_URL}`);
        resolve();
      });
    });

    // Step 2: Launch Puppeteer and open the page
    console.log('\n2. Launching browser and opening page...');
    browser = await puppeteer.launch({
      headless: true, // Set to false if you want to see the browser
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Set up console logging from the page
    page.on('console', msg => {
      console.log('   [Page Log]:', msg.text());
    });
    
    page.on('error', err => {
      console.error('   [Page Error]:', err);
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
    console.log('   ✓ Page loaded successfully');

    // Step 3: Run the optimization
    console.log('\n3. Running optimization...');
    
    // Wait for the optimize button to be available
    await page.waitForSelector('#optimizeBtn', { timeout: TIMEOUT });
    
    // Click the optimize button
    await page.click('#optimizeBtn');
    
    // Wait for optimization to complete (wait for schedule to appear)
    await page.waitForSelector('#schedule table', { timeout: TIMEOUT });
    console.log('   ✓ Optimization completed');

    // Step 4: Edit a balance value
    console.log('\n4. Editing balance value...');
    
    // Get the initial balance value of the first payment
    const initialBalance = await page.evaluate(() => {
      const firstBalanceCell = document.querySelector('#schedule tbody tr td:nth-child(6)');
      return firstBalanceCell ? parseFloat(firstBalanceCell.textContent.replace(/[^0-9.-]/g, '')) : null;
    });
    
    if (initialBalance === null) {
      throw new Error('Could not find initial balance value');
    }
    
    console.log(`   - Initial balance: $${initialBalance.toFixed(2)}`);
    
    // Click on the first balance cell to edit it
    await page.click('#schedule tbody tr td:nth-child(6)');
    
    // Wait for the input field to appear
    await page.waitForSelector('#schedule tbody tr td:nth-child(6) input', { timeout: TIMEOUT });
    
    // Clear the input and type new value
    const newBalance = initialBalance + 1000;
    await page.evaluate(() => {
      const input = document.querySelector('#schedule tbody tr td:nth-child(6) input');
      input.value = '';
    });
    
    await page.type('#schedule tbody tr td:nth-child(6) input', newBalance.toString());
    
    // Press Enter to save
    await page.keyboard.press('Enter');
    
    // Wait a moment for the save to complete
    await page.waitForTimeout(500);
    
    console.log(`   ✓ Changed balance to: $${newBalance.toFixed(2)}`);

    // Step 5: Regenerate the schedule
    console.log('\n5. Regenerating schedule...');
    
    // Click the optimize button again
    await page.click('#optimizeBtn');
    
    // Wait for the schedule to regenerate
    await page.waitForTimeout(1000); // Give it time to process
    await page.waitForSelector('#schedule table', { timeout: TIMEOUT });
    console.log('   ✓ Schedule regenerated');

    // Step 6: Verify the balance persisted
    console.log('\n6. Verifying balance persistence...');
    
    // Get the balance value after regeneration
    const persistedBalance = await page.evaluate(() => {
      const firstBalanceCell = document.querySelector('#schedule tbody tr td:nth-child(6)');
      return firstBalanceCell ? parseFloat(firstBalanceCell.textContent.replace(/[^0-9.-]/g, '')) : null;
    });
    
    if (persistedBalance === null) {
      throw new Error('Could not find balance value after regeneration');
    }
    
    console.log(`   - Balance after regeneration: $${persistedBalance.toFixed(2)}`);
    
    // Check if the balance persisted correctly
    if (Math.abs(persistedBalance - newBalance) < 0.01) {
      console.log('   ✓ Balance persisted correctly!');
    } else {
      throw new Error(`Balance did not persist. Expected ${newBalance}, got ${persistedBalance}`);
    }

    // Additional verification: Check that other values were recalculated
    const scheduleData = await page.evaluate(() => {
      const rows = document.querySelectorAll('#schedule tbody tr');
      return Array.from(rows).slice(0, 3).map(row => {
        const cells = row.querySelectorAll('td');
        return {
          payment: cells[1]?.textContent,
          principal: cells[2]?.textContent,
          interest: cells[3]?.textContent,
          totalPayment: cells[4]?.textContent,
          balance: cells[5]?.textContent
        };
      });
    });
    
    console.log('\n7. Schedule sample (first 3 rows):');
    scheduleData.forEach((row, index) => {
      console.log(`   Row ${index + 1}: ${JSON.stringify(row)}`);
    });

    // Step 7: Report success
    console.log('\n✅ TEST PASSED: All operations completed successfully!');
    
  } catch (error) {
    console.error('\n❌ TEST FAILED:', error.message);
    console.error('Stack trace:', error.stack);
    exitCode = 1;
  } finally {
    // Cleanup
    console.log('\n8. Cleaning up...');
    
    if (browser) {
      await browser.close();
      console.log('   ✓ Browser closed');
    }
    
    if (server) {
      await new Promise((resolve) => {
        server.close(() => {
          console.log('   ✓ Server stopped');
          resolve();
        });
      });
    }
    
    // Exit with appropriate code
    console.log(`\nExiting with code: ${exitCode}`);
    process.exit(exitCode);
  }
}

// Check if required files exist
function checkRequiredFiles() {
  const requiredFiles = ['index.html'];
  const missingFiles = requiredFiles.filter(file => !fs.existsSync(path.join(__dirname, file)));
  
  if (missingFiles.length > 0) {
    console.error('❌ Missing required files:', missingFiles.join(', '));
    console.error('Please ensure all required files are in the same directory as this script.');
    process.exit(1);
  }
}

// Main execution
console.log('=== Automated Test for Loan Optimization Tool ===\n');

// Check for required files
checkRequiredFiles();

// Check if puppeteer is installed
try {
  require.resolve('puppeteer');
} catch (e) {
  console.error('❌ Puppeteer is not installed. Please run: npm install puppeteer');
  process.exit(1);
}

// Run the test
runTest().catch(error => {
  console.error('Unexpected error:', error);
  process.exit(1);
});