from app import db
from app.models import Task
from app.scheduler import schedule_task, cancel_task
from flask import flash, redirect, url_for
import re

# -------------------------------
# Add a task
# -------------------------------
def add_task(
    title=None,
    time=None,
    action=None,
    user=None,
    notification_type=None,
    channels=None,
    event_type=None,
    event_sender=None,
    event_contact=None,
    event_keyword=None,
    date_window_start=None,
    date_window_end=None,
    repeat_rule="one-time"
):
    """Create and schedule a new task."""

    if not action:
        action = "No action"

    # Infer type + time from action text
    inferred_type, inferred_time = parse_action_for_task(action)
    notification_type = notification_type or inferred_type
    time = time or inferred_time or "23:59"
    title = title or "Reminder"

    if channels is None:
        channels = []

    # Convert list → comma-separated string for DB
    channels_str = ",".join(channels) if isinstance(channels, list) else str(channels)

    task = Task(
        title=title,
        time=time,
        action=action,
        user_id=user.id,
        notification_type=notification_type,
        channels=channels_str,
        event_type=event_type,
        event_sender=event_sender,
        event_contact=event_contact,
        event_keyword=event_keyword,
        date_window_start=date_window_start,
        date_window_end=date_window_end,
        repeat_rule=repeat_rule,
        enabled=True
    )

    db.session.add(task)
    db.session.commit()

    flash("✅ Task added & scheduled!", "success")
    return task

# -------------------------------
# Delete one task
# -------------------------------
def delete_task(task_id, user):
    task = Task.query.filter_by(id=task_id, user_id=user.id).first()
    if task:
        cancel_task(task.id)
        db.session.delete(task)
        db.session.commit()
        flash("🗑️ Task deleted!", "info")
    return redirect(url_for("main.tasks"))

# -------------------------------
# Clear all tasks
# -------------------------------
def clear_tasks(user):
    tasks = Task.query.filter_by(user_id=user.id).all()
    for task in tasks:
        cancel_task(task.id)
        db.session.delete(task)
    db.session.commit()
    flash("🗑️ All tasks cleared!", "info")
    return redirect(url_for("main.tasks"))

# -------------------------------
# Helper functions
# -------------------------------
def infer_task_type(action_text):
    """Infer notification type from keywords."""
    action_lower = (action_text or "").lower()
    if any(word in action_lower for word in ["wake me", "alarm", "remind me"]):
        return "alarm"
    elif any(word in action_lower for word in ["check", "read", "email", "meeting"]):
        return "banner"
    return "push"  # default

def parse_action_for_task(action_text):
    """
    Return (notification_type, time) inferred from action_text.
    Example: "Wake me at 7:30 am" -> ("alarm", "07:30")
    """
    notification_type = infer_task_type(action_text or "")

    # Extract time if mentioned
    match = re.search(r"(\d{1,2})([:.]?)(\d{0,2})\s*(am|pm)?", (action_text or "").lower())
    if match:
        hour = int(match.group(1))
        minute = int(match.group(3) or 0)
        period = match.group(4)
        if period and period.lower() == "pm" and hour < 12:
            hour += 12
        if period and period.lower() == "am" and hour == 12:
            hour = 0
        time_str = f"{hour:02d}:{minute:02d}"
    else:
        time_str = None

    return notification_type, time_str
