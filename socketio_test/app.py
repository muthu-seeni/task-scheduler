from flask import Flask, render_template
from flask_socketio import SocketIO
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "testsecret"

# Use threading backend instead of eventlet
socketio = SocketIO(app, async_mode="threading")

@app.route("/")
def index():
    return render_template("index.html")

def background_thread():
    while True:
        time.sleep(10)
        print("⏰ Timer fired! Sending test notification...")
        socketio.emit("test_notification", {
            "title": "Reminder",
            "body": "This is a test notification"
        })

if __name__ == "__main__":
    socketio.start_background_task(background_thread)
    socketio.run(app, debug=True)
