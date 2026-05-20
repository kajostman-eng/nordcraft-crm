import json
import unittest
from pathlib import Path


class RailwayConfigTest(unittest.TestCase):
    def test_start_command_uses_runtime_port(self):
        config_path = Path(__file__).resolve().parents[1] / "railway.json"
        config = json.loads(config_path.read_text())

        start_command = config["deploy"]["startCommand"]

        self.assertIn("uvicorn app.main:app", start_command)
        self.assertIn("--port ${PORT:-8000}", start_command)
        self.assertNotIn("--port 8000", start_command)
        self.assertNotIn("pip install", start_command)


if __name__ == "__main__":
    unittest.main()
