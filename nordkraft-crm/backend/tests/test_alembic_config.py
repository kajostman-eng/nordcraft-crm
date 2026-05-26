import unittest
from pathlib import Path


class AlembicConfigTests(unittest.TestCase):
    def test_online_migrations_use_asyncpg_driver_from_database_url(self):
        env_py = Path("migrations/env.py").read_text()

        self.assertIn("async_engine_from_config", env_py)
        self.assertIn("normalize_asyncpg_url(settings.DATABASE_URL)", env_py)
        self.assertIn('configuration["sqlalchemy.url"] = url', env_py)
        self.assertIn("**engine_kwargs", env_py)
        self.assertNotIn('replace("postgresql+asyncpg://", "postgresql://", 1)', env_py)
        self.assertNotIn("from sqlalchemy import engine_from_config", env_py)


if __name__ == "__main__":
    unittest.main()
