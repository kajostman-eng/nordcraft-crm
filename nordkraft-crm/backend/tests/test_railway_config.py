import json
from pathlib import Path
import unittest


class RailwayConfigTests(unittest.TestCase):
    def test_start_command_uses_platform_port_without_runtime_pip_install(self):
        railway = json.loads(
            (Path(__file__).resolve().parents[1] / "railway.json").read_text()
        )

        start_command = railway["deploy"]["startCommand"]

        self.assertIn("--port ${PORT:-8000}", start_command)
        self.assertNotIn("pip install", start_command)


if __name__ == "__main__":
    unittest.main()
