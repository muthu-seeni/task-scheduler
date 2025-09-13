import unittest
from app.services import task_service  # your helper functions module

class TestTaskParsing(unittest.TestCase):

    def test_parse_time_from_action(self):
        # Time parsing examples
        self.assertEqual(task_service.parse_time_from_action("Wake me at 7 am"), "07:00")
        self.assertEqual(task_service.parse_time_from_action("Wake me at 7:30 am"), "07:30")
        self.assertEqual(task_service.parse_time_from_action("Meeting at 12 pm"), "12:00")
        self.assertEqual(task_service.parse_time_from_action("Meeting at 12 am"), "00:00")
        self.assertEqual(task_service.parse_time_from_action("Check email at 9.15 pm"), "21:15")
        # No time mentioned
        self.assertIsNone(task_service.parse_time_from_action("No time mentioned"))

    def test_infer_task_type(self):
        # Task type inference examples
        self.assertEqual(task_service.infer_task_type("Wake me up at 7 am"), "alarm")
        self.assertEqual(task_service.infer_task_type("Remind me to call mom"), "alarm")
        self.assertEqual(task_service.infer_task_type("Check email"), "banner")
        self.assertEqual(task_service.infer_task_type("Meeting reminder"), "banner")
        self.assertEqual(task_service.infer_task_type("Random task"), "push")

    def test_parse_action_for_task(self):
        # Combined parsing: type + time
        n_type, time = task_service.parse_action_for_task("Wake me at 6 am")
        self.assertEqual(n_type, "alarm")
        self.assertEqual(time, "06:00")

        n_type, time = task_service.parse_action_for_task("Meeting at 2:30 pm")
        self.assertEqual(n_type, "banner")
        self.assertEqual(time, "14:30")

        n_type, time = task_service.parse_action_for_task("Random action")
        self.assertEqual(n_type, "push")
        self.assertIsNone(time)

if __name__ == "__main__":
    unittest.main()
