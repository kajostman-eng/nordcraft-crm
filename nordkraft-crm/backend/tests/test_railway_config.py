import json
import unittest
from pathlib import Path


class RailwayConfigTest(unittest.TestCase):
    def test_start_command_runs_migrations_and_binds_assigned_port(self):
        config = json.loads(Path("railway.json").read_text())
        command = config["deploy"]["startCommand"]

        self.assertIn("alembic upgrade head &&", command)
        self.assertIn("--port ${PORT:-8000}", command)
        self.assertNotIn("--port 8000", command)


if __name__ == "__main__":
    unittest.main()
