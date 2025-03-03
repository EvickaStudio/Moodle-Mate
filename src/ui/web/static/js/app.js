document.addEventListener('DOMContentLoaded', function() {
    // Configure marked.js options
    marked.setOptions({
        breaks: true,        // Add line breaks on single line breaks
        gfm: true,           // Use GitHub Flavored Markdown
        headerIds: true,     // Add IDs to headers
        mangle: false,       // Don't mangle header IDs
        sanitize: false,     // Don't sanitize HTML (handled by DOMPurify)
    });
    
    // Fetch notifications
    fetchNotifications();
    
    // Fetch timeline chart
    fetchTimelineChart();
    
    // Set up modal close button
    const modal = document.getElementById('notification-modal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }
    
    // Set up tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(`${tabId}-content`).classList.add('active');
        });
    });
});

async function fetchNotifications() {
    try {
        const response = await fetch('/api/notifications');
        const notifications = await response.json();
        
        // Update notification count
        document.getElementById('notification-count').textContent = `Total: ${notifications.length}`;
        
        // Clear loading message
        const notificationList = document.getElementById('notification-list');
        notificationList.innerHTML = '';
        
        // Display notifications
        if (notifications.length === 0) {
            notificationList.innerHTML = '<div class="no-data">No notifications found</div>';
            return;
        }
        
        notifications.forEach(notification => {
            const notificationItem = document.createElement('div');
            notificationItem.className = 'notification-item';
            notificationItem.setAttribute('data-id', notification.id);
            
            const date = new Date(notification.timestamp);
            const formattedDate = date.toLocaleString();
            
            notificationItem.innerHTML = `
                <h3>${notification.subject}</h3>
                <div class="notification-meta">
                    <span>${formattedDate}</span>
                </div>
                <div class="notification-preview">${getPreviewText(notification.markdown_content)}</div>
            `;
            
            notificationItem.addEventListener('click', () => showNotificationDetails(notification));
            notificationList.appendChild(notificationItem);
        });
    } catch (error) {
        console.error('Error fetching notifications:', error);
        document.getElementById('notification-list').innerHTML = 
            '<div class="error">Failed to load notifications</div>';
    }
}

async function fetchTimelineChart() {
    try {
        const response = await fetch('/api/charts/timeline');
        const chartData = await response.json();
        
        // Render the chart
        Plotly.newPlot('timeline-chart', JSON.parse(chartData));
    } catch (error) {
        console.error('Error fetching timeline chart:', error);
        document.getElementById('timeline-chart').innerHTML = 
            '<div class="error">Failed to load chart</div>';
    }
}

function showNotificationDetails(notification) {
    const modal = document.getElementById('notification-modal');
    
    // Set modal title
    document.getElementById('modal-title').textContent = notification.subject;
    
    // Set content for each tab
    document.getElementById('html-content').innerHTML = notification.html_content;
    
    // Use marked.js to render markdown with proper styling
    const markdownContent = document.getElementById('markdown-content');
    markdownContent.innerHTML = marked.parse(notification.markdown_content);
    markdownContent.classList.add('markdown-content');
    
    // Set summary content with markdown rendering if it contains markdown
    const summaryContent = document.getElementById('summary-content');
    if (notification.summary) {
        // Check if summary contains markdown-like content
        if (/[*#_`\[\]()]/.test(notification.summary)) {
            summaryContent.innerHTML = marked.parse(notification.summary);
            summaryContent.classList.add('markdown-content');
        } else {
            summaryContent.textContent = notification.summary;
        }
    } else {
        summaryContent.textContent = 'No AI summary available';
    }
    
    // Show the modal
    modal.style.display = 'block';
    
    // Reset to first tab
    document.querySelectorAll('.tab-btn')[0].click();
}

function getPreviewText(markdown) {
    // Strip markdown formatting for preview
    return markdown
        .replace(/[#*_~`]/g, '')  // Remove markdown symbols
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // Replace links with just the text
        .substring(0, 150) + '...';  // Limit length
} 