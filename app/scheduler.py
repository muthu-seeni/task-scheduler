from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime
from app.models import Task
import pyttsx3

scheduler = BackgroundScheduler(timezone=timezone("Asia/Kolkata"))
scheduler_started = False
_app = None
_socketio = None

# Keep track of already emitted tasks to prevent duplicates
_emitted_tasks = set()

def start_scheduler(app, socketio=None):
    global scheduler_started, _app, _socketio
    _app = app
    if not scheduler_started:
        scheduler.start()
        scheduler_started = True
        print("✅ Scheduler started")

    if socketio:
        _socketio = socketio

    # Schedule tasks from DB
    with _app.app_context():
        tasks = Task.query.filter_by(enabled=True).all()
        for task in tasks:
            schedule_task(task)
        print(f"📌 Scheduled {len(tasks)} task(s) from DB")

def task_runner(task_id):
    with _app.app_context():
        task = Task.query.get(task_id)
        if not task or task_id in _emitted_tasks:
            return

        _emitted_tasks.add(task_id)  # prevent duplicate notification

        title = task.title or "Reminder"
        body = task.action or "You have a task!"
        print(f"[{datetime.now()}] 🔔 {title}: {body}")

        # Emit to the specific user only
        if _socketio:
            try:
                _socketio.emit(
                    "task_notification",
                    {"id": task.id, "title": title, "body": body},
                    room=f"user_{task.user_id}"
                )
                print(f"📢 Emitted notification for task {task.id} (user {task.user_id})")
            except Exception as e:
                print(f"⚠️ SocketIO emit failed: {e}")

        # Optional voice alert
        try:
            engine = pyttsx3.init()
            engine.say(f"{title}. {body}")
            engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Voice alert failed: {e}")

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
        args=[task.id],
        id=job_id,
        replace_existing=True,
    )
    print(f"✅ Scheduled task {task.id}: {task.title} at {task.time}")

def cancel_task(task_id):
    job_id = f"task_{task_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        print(f"🗑️ Cancelled task {task_id}")
        # Also remove from emitted set to allow reschedule
        _emitted_tasks.discard(task_id)
