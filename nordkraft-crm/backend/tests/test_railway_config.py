import json
import unittest
from pathlib import Path


class RailwayConfigTests(unittest.TestCase):
    def test_start_command_runs_migrations_and_binds_to_railway_port(self):
        railway_config = json.loads(Path("railway.json").read_text())
        start_command = railway_config["deploy"]["startCommand"]

        self.assertIn("python -m alembic upgrade head", start_command)
        self.assertIn("--port ${PORT:-8000}", start_command)
        self.assertNotIn("pip install", start_command)


if __name__ == "__main__":
    unittest.main()
