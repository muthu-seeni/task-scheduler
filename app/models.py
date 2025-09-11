# app/models.py
from datetime import datetime, date
from app import db
from flask_login import UserMixin

# -------------------------------
# User model
# -------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # One-to-many relationship: User → Tasks
    tasks = db.relationship("Task", backref="owner", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


# -------------------------------
# Task model
# -------------------------------
class Task(db.Model):
    """
    Task model extended to support:
    - time-based reminders (time field)
    - event triggers (email/whatsapp) using event_type + event_* fields
    - notification_type (alarm | push | banner)
    - channels (comma-separated list of channels e.g. "alarm,push")
    - repeat_rule (one-time / daily / weekly / custom string)
    - enabled flag (turn off without deleting)
    - created_at timestamp
    """

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    # Basic fields
    title = db.Column(db.String(200), nullable=False)
    # Keep time as "HH:MM" string for simple scheduling. Can be empty for purely event-based tasks.
    time = db.Column(db.String(10), nullable=True)

    # Free text / short action description (what to do)
    action = db.Column(db.String(500), nullable=True)

    # Notification & channel settings
    # notification_type: primary urgency / style (alarm | push | banner)
    notification_type = db.Column(db.String(20), nullable=False, default="alarm")
    # channels: CSV of channels the user selected (e.g. "alarm,push") - easier to store than JSON for SQLite
    channels = db.Column(db.String(200), nullable=True)

    # Event trigger fields (optional)
    # event_type: None or "email" or "whatsapp"
    event_type = db.Column(db.String(20), nullable=True)
    # For email triggers, event_sender holds the sender email (e.g. college@domain.com)
    event_sender = db.Column(db.String(320), nullable=True)
    # For WhatsApp triggers, event_contact holds contact id/name
    event_contact = db.Column(db.String(200), nullable=True)
    # Optional keyword filter for either email subject/body or WhatsApp message content
    event_keyword = db.Column(db.String(200), nullable=True)

    # Optional date window for event triggers (useful for "between 13th and 20th")
    # Stored as DATE so comparisons are straightforward
    date_window_start = db.Column(db.Date, nullable=True)
    date_window_end = db.Column(db.Date, nullable=True)

    # Recurrence rules
    # Examples: "one-time", "daily", "weekly", or a short custom string the scheduler understands
    repeat_rule = db.Column(db.String(50), nullable=False, default="one-time")

    # Flags & metadata
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # app/models.py (inside Task model) 
    notify_enabled = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        parts = [f"{self.title}"]
        if self.time:
            parts.append(f"@ {self.time}")
        if self.event_type:
            parts.append(f"(trigger: {self.event_type})")
        return f"<Task {' '.join(parts)}>"

    def channels_list(self):
        """Return channels as a Python list."""
        if not self.channels:
            return []
        return [c.strip() for c in self.channels.split(",") if c.strip()]

    def set_channels(self, channel_iterable):
        """Set channels from an iterable (list/tuple) and store as CSV string."""
        if channel_iterable:
            self.channels = ",".join([str(c).strip() for c in channel_iterable if c])
        else:
            self.channels = None

    def in_date_window(self, check_date: date):
        """Return True if check_date lies within the optional date window (inclusive)."""
        if not self.date_window_start and not self.date_window_end:
            return True
        if self.date_window_start and check_date < self.date_window_start:
            return False
        if self.date_window_end and check_date > self.date_window_end:
            return False
        return True

    def to_dict(self):
        """Lightweight dict for rendering in templates / APIs."""
        return {
            "id": self.id,
            "title": self.title,
            "time": self.time,
            "action": self.action,
            "notification_type": self.notification_type,
            "channels": self.channels_list(),
            "event_type": self.event_type,
            "event_sender": self.event_sender,
            "event_contact": self.event_contact,
            "event_keyword": self.event_keyword,
            "date_window_start": self.date_window_start.isoformat() if self.date_window_start else None,
            "date_window_end": self.date_window_end.isoformat() if self.date_window_end else None,
            "repeat_rule": self.repeat_rule,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
        }
