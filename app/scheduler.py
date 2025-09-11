from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime
from app.models import Task
import pyttsx3

# -------------------------------
# Global scheduler & references
# -------------------------------
scheduler = BackgroundScheduler(timezone=timezone("Asia/Kolkata"))
scheduler_started = False
_app = None      # store Flask app instance
_socketio = None # store SocketIO reference

# -------------------------------
# Start scheduler
# -------------------------------
def start_scheduler(app, socketio=None):
    global scheduler_started, _app, _socketio
    _app = app
    if not scheduler_started:
        scheduler.start()
        scheduler_started = True
        print("✅ Scheduler started")

    if socketio:
        _socketio = socketio

    # Load tasks from DB and schedule
    with _app.app_context():
        tasks = Task.query.filter_by(enabled=True).all()
        for task in tasks:
            schedule_task(task)  # pass task_id automatically in schedule_task
        print(f"📌 Scheduled {len(tasks)} task(s) from DB")

# -------------------------------
# Task runner
# -------------------------------
def task_runner(task_id):
    with _app.app_context():
        task = Task.query.get(task_id)
        if not task:
            return

        message = f"🔔 Reminder: {task.title} ({task.action})"
        print(f"[{datetime.now()}] {message}")

        # SocketIO emit
        if _socketio:
            try:
                _socketio.emit(
                    "task_notification",
                    {"title": task.title, "body": task.action},
                    broadcast=True
                )
                print(f"📢 Emitted notification for task {task.id}")
            except Exception as e:
                print(f"⚠️ SocketIO emit failed: {e}")

        # Voice alert
        try:
            engine = pyttsx3.init()
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Voice alert failed: {e}")

# -------------------------------
# Schedule task
# -------------------------------
def schedule_task(task):
    try:
        hour, minute = map(int, task.time.split(":"))
    except Exception:
        print(f"⚠️ Invalid time format for task {task.id}: {task.time}")
        return

    job_id = f"task_{task.id}"
    cancel_task(task.id)

    scheduler.add_job(
        func=task_runner,
        trigger=CronTrigger(hour=hour, minute=minute),
        args=[task.id],   # ✅ pass task_id here!
        id=job_id,
        replace_existing=True,
    )
    print(f"✅ Scheduled task {task.id}: {task.title} at {task.time}")

# -------------------------------
# Cancel task
# -------------------------------
def cancel_task(task_id):
    job_id = f"task_{task_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        print(f"🗑️ Cancelled task {task_id}")
