document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');

    // View switching
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (this.getAttribute('href') !== '/logout') {
                e.preventDefault();
                const viewName = this.dataset.view;

                navItems.forEach(nav => nav.classList.remove('active'));
                this.classList.add('active');

                views.forEach(view => view.classList.remove('active'));
                document.getElementById(viewName).classList.add('active');
            }
        });
    });

    // API calls
    const logContent = document.getElementById('log-content');
    const notificationList = document.getElementById('notification-list');

    async function fetchLogs() {
        try {
            const response = await fetch('/api/logs');
            if (response.ok) {
                logContent.textContent = await response.text();
            } else {
                logContent.textContent = 'Failed to load logs.';
            }
        } catch (error) {
            logContent.textContent = 'Error fetching logs.';
        }
    }

    async function fetchNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (response.ok) {
                const notifications = await response.json();
                notificationList.innerHTML = notifications.map(n => `
                    <div class="notification-card">
                        <h4>${n.subject}</h4>
                        <div class="summary">${n.summary || ''}</div>
                        <div class="message">${n.message}</div>
                    </div>
                `).join('');
            } else {
                notificationList.innerHTML = '<p>Failed to load notifications.</p>';
            }
        } catch (error) {
            notificationList.innerHTML = '<p>Error fetching notifications.</p>';
        }
    }

    // Initial data load and periodic refresh
    fetchLogs();
    fetchNotifications();
    setInterval(fetchLogs, 5000);
    setInterval(fetchNotifications, 10000);
});
