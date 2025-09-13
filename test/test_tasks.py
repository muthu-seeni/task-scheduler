import unittest
from app import create_app, db
from app.models import Task, User
from unittest.mock import patch
import pyperclip

import app.scheduler as scheduler   # ✅ import scheduler module directly


class TaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.app.testing = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # ✅ Inject test app into scheduler
        scheduler._app = self.app

        # Create a test user
        user = User(username="testuser", password="password")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        scheduler._app = None  # cleanup after test

    def create_task(self, title="Test Task", time="08:00",
                    action="Do something", enabled=True):
        task = Task(title=title, time=time,
                    action=action, user_id=self.user_id,
                    enabled=enabled)
        db.session.add(task)
        db.session.commit()
        return db.session.get(Task, task.id)

    # ---------- Tests ----------

    def test_task_creation(self):
        task = self.create_task()
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.time, "08:00")
        self.assertEqual(task.action, "Do something")
        self.assertTrue(task.enabled)

    def test_notification_toggle(self):
        task = self.create_task(enabled=True)
        task.enabled = not task.enabled
        db.session.commit()
        db.session.refresh(task)
        self.assertFalse(task.enabled)

    def test_hybrid_notification(self):
        task1 = self.create_task(title="Task 1")
        self.create_task(title="Task 2", enabled=False)
        enabled_tasks = Task.query.filter_by(enabled=True).all()
        self.assertEqual(len(enabled_tasks), 1)
        self.assertEqual(enabled_tasks[0].title, "Task 1")

    def test_task_runner_prints(self):
        task = self.create_task(title="Notify Test", action="Check console")
        with patch("builtins.print") as mock_print:
            scheduler.task_runner(task.id)  # ✅ now works, _app injected

            mock_print.assert_called()
            args, _ = mock_print.call_args
            printed = args[0]

            self.assertIn("🔔 Reminder: Notify Test (Check console)", printed)
            self.assertIn("[", printed)

    @patch("pyperclip.copy")
    def test_whatsapp_clipboard(self, mock_copy):
        task = self.create_task(action="Send report")
        pyperclip.copy(task.action)
        mock_copy.assert_called_with("Send report")

    def test_task_action_wrap(self):
        long_action = "milk curd oil rice " * 5
        task = self.create_task(title="Prepare grocery list",
                                action=long_action)
        self.assertIn("milk", task.action)
        self.assertTrue(len(task.action) > 50)

    def test_grocery_task_edit_mode(self):
        action_text = "milk curd oil rice"
        task = self.create_task(title="Prepare grocery list",
                                action=action_text)
        fetched = db.session.get(Task, task.id)
        self.assertEqual(fetched.action, "milk curd oil rice")

    def test_task_type_distinction(self):
        grocery_task = self.create_task(title="Prepare grocery list",
                                        action="milk curd oil rice")
        normal_task = self.create_task(title="Finish report",
                                       action="Email manager")

        self.assertIn("grocery", grocery_task.title.lower())
        self.assertNotIn("grocery", normal_task.title.lower())


if __name__ == "__main__":
    unittest.main()
