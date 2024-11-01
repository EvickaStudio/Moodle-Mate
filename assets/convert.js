const TurndownService = require('turndown');

// Create a new instance of TurndownService
const turndownService = new TurndownService();

// Read HTML content from stdin
let html = '';
process.stdin.on('readable', () => {
    let chunk;
    while ((chunk = process.stdin.read()) !== null) {
        html += chunk;
    }
});

// Convert HTML to Markdown when stdin finishes
process.stdin.on('end', () => {
    const markdown = turndownService.turndown(html);
    process.stdout.write(markdown);
});
