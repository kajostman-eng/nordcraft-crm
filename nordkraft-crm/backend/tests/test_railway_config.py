import json
import unittest
from pathlib import Path


class RailwayConfigTests(unittest.TestCase):
    def test_start_command_runs_migrations_and_binds_platform_port(self):
        config = json.loads(
            (Path(__file__).resolve().parents[1] / "railway.json").read_text()
        )

        start_command = config["deploy"]["startCommand"]
        self.assertIn("alembic upgrade head", start_command)
        self.assertIn("--port ${PORT:-8000}", start_command)


if __name__ == "__main__":
    unittest.main()
