import json
import tempfile
import unittest
from pathlib import Path
from scripts.workflow import validate_config, prepare, preflight, fresh_cost


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "project_id": "test-001", "topic": "自媒体 AI 数字人口播",
            "provider": "manual", "platform": "douyin", "duration_seconds": 45,
            "creator": {"display_name": "test", "avatar_authorized": True, "voice_authorized": True},
            "paid_tools": {"renoise_opt_in": False, "require_confirmation": True, "max_estimated_credits": 0},
        }

    def test_manual_mode_no_renoise(self):
        self.assertEqual(validate_config(self.config), [])
        ok, _ = preflight(fresh_cost(self.config), 10, approved=True)
        self.assertFalse(ok)

    def test_paid_mode_needs_explicit_opt_in_and_budget(self):
        self.config["provider"] = "renoise"
        self.assertTrue(validate_config(self.config))
        self.config["paid_tools"].update(renoise_opt_in=True, max_estimated_credits=100)
        self.assertEqual(validate_config(self.config), [])

    def test_voice_rights_cannot_be_assumed(self):
        self.config["creator"]["voice_authorized"] = False
        self.assertTrue(any("voice_authorized" in error for error in validate_config(self.config)))

    def test_paid_mode_requires_approval_and_respects_budget(self):
        self.config["provider"] = "renoise"
        self.config["paid_tools"].update(renoise_opt_in=True, max_estimated_credits=100)
        cost = fresh_cost(self.config)
        self.assertFalse(preflight(cost, 50, approved=False)[0])
        self.assertTrue(preflight(cost, 50, approved=True)[0])
        cost["recorded_actual_credits"] = 70
        self.assertFalse(preflight(cost, 40, approved=True)[0])
        self.assertFalse(preflight(cost, -1, approved=True)[0])

    def test_generates_package(self):
        with tempfile.TemporaryDirectory() as temp:
            config_file = Path(temp) / "input.json"
            config_file.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")
            output = Path(temp) / "run"
            prepare(config_file, output)
            self.assertTrue((output / "plan.md").exists())
            self.assertTrue((output / "qa-checklist.md").exists())
            self.assertIn("尚未付费", (output / "plan.md").read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                prepare(config_file, output)

    def test_invalid_types_fail(self):
        self.config["duration_seconds"] = True
        self.assertTrue(validate_config(self.config))
        self.config["duration_seconds"] = 45
        self.config["paid_tools"]["require_confirmation"] = False
        self.assertTrue(validate_config(self.config))


if __name__ == "__main__":
    unittest.main()
