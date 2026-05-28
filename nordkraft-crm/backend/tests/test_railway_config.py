import json
import unittest
from pathlib import Path


class RailwayConfigTests(unittest.TestCase):
    def test_start_command_runs_migrations_before_serving(self):
        config_path = Path(__file__).resolve().parents[1] / "railway.json"
        config = json.loads(config_path.read_text())

        start_command = config["deploy"]["startCommand"]
        self.assertIn("alembic upgrade head", start_command)
        self.assertLess(start_command.index("alembic upgrade head"), start_command.index("uvicorn"))
        self.assertIn("--port ${PORT:-8000}", start_command)


if __name__ == "__main__":
    unittest.main()
