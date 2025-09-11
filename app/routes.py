from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.services import auth_service, task_service
from app.scheduler import scheduler, start_scheduler as start_scheduler_func, cancel_task, schedule_task, task_runner
from app import csrf, db
from app.models import Task
from datetime import datetime

bp = Blueprint("main", __name__)

# -------------------------------
# Startup: begin APScheduler
# -------------------------------
@bp.before_app_request
def start_scheduler():
    if not scheduler.running:
        start_scheduler_func(current_app)

# -------------------------------
# Home page
# -------------------------------
@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.tasks"))
    return render_template("index.html")

# -------------------------------
# Register
# -------------------------------
@bp.route("/register", methods=["GET", "POST"])
@csrf.exempt
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("⚠️ Username and password cannot be empty.", "danger")
            return redirect(url_for("main.register"))
        return auth_service.register_user(username, password)
    return render_template("register.html")

# -------------------------------
# Login
# -------------------------------
@bp.route("/login", methods=["GET", "POST"])
@csrf.exempt
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("⚠️ Username and password cannot be empty.", "danger")
            return redirect(url_for("main.login"))
        return auth_service.login_user_service(username, password)
    return render_template("login.html")

# -------------------------------
# Logout
# -------------------------------
@bp.route("/logout")
@login_required
def logout():
    return auth_service.logout_user_service()

# -------------------------------
# Task dashboard
# -------------------------------
@bp.route("/tasks", methods=["GET", "POST"])
@login_required
@csrf.exempt
def tasks():
    if request.method == "POST":
        title = request.form.get("title") or "Reminder"
        time = request.form.get("time") or "23:59"
        action = request.form.get("action") or ""
        notification_type = task_service.infer_task_type(action)

        # Add & schedule
        task = task_service.add_task(title, time, action, current_user, notification_type)
        schedule_task(task)

        flash("✅ Task added successfully!", "success")
        return redirect(url_for("main.tasks"))

    # GET: show tasks
    tasks_list = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("tasks.html", tasks=tasks_list)

# -------------------------------
# Edit a task
# -------------------------------
@bp.route("/tasks/edit/<int:task_id>", methods=["POST"])
@login_required
@csrf.exempt
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("⚠️ Task not found.", "danger")
        return redirect(url_for("main.tasks"))

    task.title = request.form.get("title") or "Reminder"
    task.time = request.form.get("time") or "23:59"
    task.action = request.form.get("action") or ""
    task.notification_type = task_service.infer_task_type(task.action)

    cancel_task(task.id)
    schedule_task(task)
    db.session.commit()

    flash("✏️ Task updated successfully!", "success")
    return redirect(url_for("main.tasks"))

# -------------------------------
# Delete a task
# -------------------------------
@bp.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
@csrf.exempt
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        cancel_task(task.id)
        db.session.delete(task)
        db.session.commit()
        flash("🗑️ Task deleted successfully!", "success")
    return redirect(url_for("main.tasks"))

# -------------------------------
# Clear all tasks
# -------------------------------
@bp.route("/clear_tasks", methods=["POST"])
@login_required
@csrf.exempt
def clear_tasks():
    tasks_list = Task.query.filter_by(user_id=current_user.id).all()
    for t in tasks_list:
        cancel_task(t.id)
        db.session.delete(t)
    db.session.commit()
    flash("🗑️ All tasks cleared!", "success")
    return redirect(url_for("main.tasks"))

# -------------------------------
# Run a task immediately (button)
# -------------------------------
@bp.route("/tasks/run_now/<int:task_id>", methods=["POST"])
@login_required
@csrf.exempt
def run_task_now(task_id):
    task_runner(task_id)  # safe, uses app context internally
    flash("▶️ Task executed immediately!", "success")
    return redirect(url_for("main.tasks"))

# -------------------------------
# Check notifications for browser
# -------------------------------
@bp.route("/check_notifications")
@login_required
def check_notifications():
    now = datetime.now().strftime("%H:%M")
    due_tasks = Task.query.filter_by(user_id=current_user.id, time=now).all()
    results = [{"title": t.title or "Reminder", "body": t.action or "You have a task!"} for t in due_tasks]
    return jsonify(results)
