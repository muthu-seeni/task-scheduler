import unittest
from app import create_app, db, bcrypt
from app.models import User, Task

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        # Setup test DB
        with self.app.app_context():
            db.create_all()
            hashed_pw = bcrypt.generate_password_hash("testpass").decode("utf-8")
            self.user = User(username="testuser", password=hashed_pw)
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        return self.client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True
        )

    def test_login(self):
        response = self.login()
        self.assertIn(b"Welcome back, testuser!", response.data)

    def test_add_task(self):
        self.login()
        response = self.client.post(
            "/tasks",
            data={"title": "Test Task", "time": "12:00", "action": "Run Now"},
            follow_redirects=True
        )
        self.assertIn(b"Test Task", response.data)

    def test_edit_task(self):
        self.login()
        # Add task first
        self.client.post(
            "/tasks",
            data={"title": "Old Task", "time": "12:00", "action": "Run Now"},
            follow_redirects=True
        )
        with self.app.app_context():
            task = Task.query.first()
            self.assertIsNotNone(task)

        # Edit task
        response = self.client.post(
            f"/tasks/{task.id}",
            data={"title": "Updated Task", "time": "14:30", "action": "Run Now"},
            follow_redirects=True
        )
        self.assertIn(b"Updated Task", response.data)

    def test_run_now_route(self):
        self.login()
        # Add a task to trigger "run now"
        self.client.post(
            "/tasks",
            data={"title": "Run Now Task", "time": "12:00", "action": "Run Now"},
            follow_redirects=True
        )
        # Access run_now endpoint
        response = self.client.get("/run_now", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Run Now Task", response.data)

if __name__ == "__main__":
    unittest.main()
