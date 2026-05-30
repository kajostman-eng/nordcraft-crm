import json
import unittest
from pathlib import Path


class RailwayConfigTests(unittest.TestCase):
    def test_start_command_runs_migrations_and_uses_runtime_port(self):
        railway_config = Path(__file__).resolve().parents[1] / "railway.json"
        config = json.loads(railway_config.read_text())

        command = config["deploy"]["startCommand"]
        self.assertIn("alembic upgrade head", command)
        self.assertIn("--port ${PORT:-8000}", command)
        self.assertNotIn("pip install", command)


if __name__ == "__main__":
    unittest.main()
