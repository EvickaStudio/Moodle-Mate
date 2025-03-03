import json
import os

import pandas as pd
import plotly
import plotly.express as px
from flask import Flask, jsonify, render_template

from src.infrastructure.database.models import Notification, db

# Global app instance that can be shared
flask_app = None


def create_app(config_path=None):
    """Create and configure the Flask application."""
    global flask_app

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )

    # Configure the SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notifications.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register routes
    @app.route("/")
    def index():
        """Render the main dashboard page."""
        return render_template("index.html")

    @app.route("/api/notifications")
    def get_notifications():
        """API endpoint to get all notifications."""
        notifications = Notification.query.order_by(Notification.timestamp.desc()).all()
        return jsonify(
            [
                {
                    "id": n.id,
                    "moodle_id": n.moodle_id,
                    "subject": n.subject,
                    "html_content": n.html_content,
                    "markdown_content": n.markdown_content,
                    "summary": n.summary,
                    "timestamp": n.timestamp.isoformat(),
                    "user_id_from": n.user_id_from,
                }
                for n in notifications
            ]
        )

    @app.route("/api/charts/timeline")
    def notification_timeline():
        """API endpoint to get notification timeline data for visualization."""
        notifications = Notification.query.order_by(Notification.timestamp).all()

        if not notifications:
            return jsonify({"error": "No data available"})

        # Create a DataFrame for plotting
        df = pd.DataFrame([{"date": n.timestamp, "count": 1} for n in notifications])

        # Group by day and count
        df["date"] = pd.to_datetime(df["date"])
        daily_counts = df.groupby(df["date"].dt.date)["count"].sum().reset_index()

        # Create a timeline chart
        fig = px.line(
            daily_counts,
            x="date",
            y="count",
            title="Notifications per Day",
            labels={"date": "Date", "count": "Number of Notifications"},
        )

        # Update layout for dark theme
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(50, 50, 50, 0.8)",
            plot_bgcolor="rgba(50, 50, 50, 0.8)",
            font={"color": "#f2f2f2"},
        )

        # Convert the figure to JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return jsonify(graphJSON)

    # Store the app instance globally
    flask_app = app

    return app


def get_flask_app():
    """Get the Flask application instance."""
    global flask_app
    if flask_app is None:
        flask_app = create_app()
    return flask_app


def run_webui(host="0.0.0.0", port=5000, debug=False, app=None):
    """Run the web UI server."""
    if app is None:
        app = get_flask_app()
    app.run(host=host, port=port, debug=debug)
