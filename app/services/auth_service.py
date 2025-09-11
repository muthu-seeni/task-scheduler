from flask import flash, redirect, url_for
from flask_login import login_user, logout_user
from app import db, bcrypt
from app.models import User

# -------------------------------
# Register a new user
# -------------------------------
def register_user(username, password):
    existing = User.query.filter_by(username=username).first()
    if existing:
        flash("⚠️ Username already exists.", "danger")
        return redirect(url_for("main.register"))

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    flash("✅ Account created! Please log in.", "success")
    return redirect(url_for("main.login"))

# -------------------------------
# Login user
# -------------------------------
def login_user_service(username, password):
    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        flash("❌ Invalid username or password.", "danger")
        return redirect(url_for("main.login"))

    login_user(user)
    flash(f"👋 Welcome back, {user.username}!", "success")
    return redirect(url_for("main.tasks"))

# -------------------------------
# Logout user
# -------------------------------
def logout_user_service():
    logout_user()
    flash("👋 You have been logged out.", "info")
    return redirect(url_for("main.index"))