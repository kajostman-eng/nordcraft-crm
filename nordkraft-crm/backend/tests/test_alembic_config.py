import os
import subprocess
import sys
import unittest
from pathlib import Path


class AlembicConfigTests(unittest.TestCase):
    def test_alembic_uses_asyncpg_driver_instead_of_missing_psycopg2(self):
        backend_dir = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env["DATABASE_URL"] = "postgresql+asyncpg://user:pass@127.0.0.1:1/nordkraft_crm"

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            cwd=backend_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout + result.stderr

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("psycopg2", output)
        self.assertNotIn("No module named", output)
        self.assertIn("Connect call failed", output)


if __name__ == "__main__":
    unittest.main()
