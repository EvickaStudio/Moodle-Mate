# Moodle-Mate Web Interface

A modern, responsive web interface for monitoring and configuring Moodle-Mate using the Maybe design system.

## Features

### 🚀 Dashboard
- Real-time system status monitoring
- Notification history with live updates
- Quick actions for testing connections and sending notifications
- System health metrics and provider status

### ⚙️ Configuration Management
- Interactive forms for all settings
- Moodle connection configuration with testing
- AI-powered summary settings
- Notification provider setup
- Health monitoring configuration
- Notification filters and rules

### 📊 Monitoring & Analytics
- Notification history with search and filtering
- System health dashboard
- Activity logs and error tracking
- Performance metrics
- Service status monitoring

### 🎨 Modern UI/UX
- Built with TailwindCSS v4.x and Maybe design system
- Responsive design for mobile and desktop
- Dark/light theme support
- Accessible interface with semantic HTML
- Real-time updates with toast notifications

## Quick Start

### Prerequisites
- Python 3.8+
- Moodle-Mate backend configured
- Flask dependency installed

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Launch the web interface:
```bash
python web_launcher.py
```

3. Open your browser to:
```
http://localhost:5000
```

### Advanced Usage

#### Custom Host/Port
```bash
# Listen on all interfaces, port 8080
python web_launcher.py --host 0.0.0.0 --port 8080

# Production deployment
python web_launcher.py --host 0.0.0.0 --port 80
```

#### Debug Mode (Development)
```bash
# Enable auto-reload and detailed error pages
python web_launcher.py --debug
```

#### Custom Configuration
```bash
# Use different config file
python web_launcher.py --config /path/to/config.ini
```

## API Endpoints

The web interface provides RESTful API endpoints:

### Status & Health
- `GET /api/status` - System health status
- `POST /api/test-connection` - Test Moodle connection
- `POST /api/test-notification` - Send test notification

### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration

### Notifications
- `GET /api/notifications?limit=N` - Get recent notifications
- `GET /api/providers` - List notification providers

## Architecture

### Backend Integration
The web interface seamlessly integrates with the existing Moodle-Mate backend:

```python
# Service integration via ServiceLocator
from src.core.service_locator import ServiceLocator

locator = ServiceLocator()
config = locator.get("config", Config)
moodle_api = locator.get("moodle_api", MoodleAPI)
notification_processor = locator.get("notification_processor", NotificationProcessor)
```

### Design System
Built using the Maybe design system for consistent, beautiful UI:

```html
<!-- Using design system tokens -->
<div class="bg-container border border-primary rounded-lg shadow-sm">
  <button class="button-bg-primary hover:button-bg-primary-hover text-white">
    Primary Action
  </button>
</div>
```

### Real-time Updates
- Auto-refresh every 30 seconds for status updates
- Toast notifications for user feedback
- Live status indicators with color coding

## File Structure

```
src/ui/web/
├── app.py              # Main Flask application
├── templates/          # Jinja2 templates
│   ├── base.html      # Base template with navigation
│   ├── dashboard.html # Main dashboard
│   ├── config.html    # Configuration forms
│   ├── notifications.html # Notification history
│   └── health.html    # System health monitoring
└── README.md          # This file
```

## CSS and Assets Setup

### TailwindCSS Compilation

The web interface uses TailwindCSS v4.x with the Maybe design system. The CSS is compiled using npm:

```bash
cd src/ui/web

# Install dependencies
npm install

# For development (watches for changes)
npm run build-css

# For production (minified)
npm run build-css-prod
```

The compiled CSS is served from `static/css/output.css` and includes:
- TailwindCSS utilities
- Maybe design system tokens
- Geist font families
- Custom component styles

### Asset Structure

```
src/ui/web/static/
├── assets/           # Copied from src/assets/
│   ├── tailwind/    # Maybe design system CSS
│   ├── images/      # SVG icons and images
│   └── fonts/       # Geist font files
├── css/
│   ├── input.css    # TailwindCSS input file
│   └── output.css   # Compiled CSS (served to browser)
└── js/              # Future JavaScript files
```

## Development

### Adding New Pages

1. Create a new template in `templates/`:
```html
{% extends "base.html" %}
{% block page_title %}New Page{% endblock %}
{% block content %}
<!-- Your content here -->
{% endblock %}
```

2. Add route in `app.py`:
```python
@self.app.route("/new-page")
def new_page():
    return render_template("new_page.html")
```

### Styling Guidelines

- Use Maybe design system tokens (e.g., `bg-container`, `text-primary`)
- Follow component patterns from existing templates
- Ensure responsive design with TailwindCSS classes
- Test both light and dark themes

### JavaScript Patterns

```javascript
// Use the MoodleMateAPI class for backend calls
const result = await MoodleMateAPI.get('/status');

// Show user feedback with toast notifications
showToast('Success message', 'success');
showToast('Error message', 'error');
```

## Deployment

### Development
```bash
python web_launcher.py --debug
```

### Production

For production deployment, consider using:

- **Gunicorn** (recommended):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 src.ui.web.app:create_app()
```

- **uWSGI**:
```bash
pip install uwsgi
uwsgi --http :8000 --module src.ui.web.app:create_app()
```

- **Docker** (with provided Dockerfile):
```bash
docker build -t moodle-mate .
docker run -p 8000:8000 moodle-mate
```

### Environment Variables

- `MOODLE_MATE_CONFIG` - Path to configuration file
- `FLASK_ENV` - Set to `production` for production deployment

## Security Considerations

- The web interface runs on localhost by default
- For external access, ensure proper firewall configuration
- Consider using HTTPS in production (reverse proxy recommended)
- Regular security updates for Flask and dependencies

## Troubleshooting

### Common Issues

**Web interface won't start:**
- Check if port is already in use
- Verify Flask is installed: `pip install flask`
- Check configuration file path

**Backend services not connecting:**
- Ensure Moodle-Mate backend is properly configured
- Check `config.ini` file exists and is valid
- Verify Moodle credentials and URL

**Static assets not loading:**
- Ensure TailwindCSS files are built
- Check asset paths in templates
- Verify file permissions

### Logs and Debugging

Enable debug logging:
```bash
python web_launcher.py --log-level DEBUG --debug
```

Check browser developer tools for JavaScript errors and network issues.

## Contributing

When contributing to the web interface:

1. Follow the existing code style and patterns
2. Use the Maybe design system consistently
3. Test on both desktop and mobile viewports
4. Ensure accessibility standards are met
5. Update this documentation for new features

## License

Same as Moodle-Mate main project - see LICENSE.md in the project root. 