# run_prod.py

# 1️⃣ Monkey patch BEFORE anything else
import eventlet
eventlet.monkey_patch()

# 2️⃣ Now import your app and socketio
from app import create_app, socketio

# 3️⃣ Create Flask app
app = create_app()

# 4️⃣ Run socketio with Eventlet
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
