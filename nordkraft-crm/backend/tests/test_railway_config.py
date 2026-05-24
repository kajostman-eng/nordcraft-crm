import json
import unittest
from pathlib import Path


class RailwayConfigTests(unittest.TestCase):
    def test_start_command_runs_migrations_and_binds_to_runtime_port(self):
        config_path = Path(__file__).resolve().parents[1] / "railway.json"
        config = json.loads(config_path.read_text())
        command = config["deploy"]["startCommand"]

        self.assertIn("alembic upgrade head", command)
        self.assertIn("--host 0.0.0.0", command)
        self.assertIn("--port ${PORT:-8000}", command)
        self.assertNotIn("--port 8000", command)
        self.assertNotIn("pip install", command)


if __name__ == "__main__":
    unittest.main()
