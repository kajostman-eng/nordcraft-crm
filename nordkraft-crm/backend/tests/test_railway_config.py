import json
import unittest
from pathlib import Path


class RailwayConfigTest(unittest.TestCase):
    def test_start_command_runs_migrations_and_uses_dynamic_port(self):
        railway_config = json.loads((Path(__file__).parents[1] / "railway.json").read_text())
        command = railway_config["deploy"]["startCommand"]

        self.assertIn("alembic upgrade head", command)
        self.assertIn("--port ${PORT:-8000}", command)
        self.assertNotIn("pip install", command)


if __name__ == "__main__":
    unittest.main()
