import os
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError


class MigrationTests(unittest.TestCase):
    def _get_test_database_url(self) -> str:
        url = os.getenv("MIGRATION_TEST_DATABASE_URL")
        if not url:
            raise unittest.SkipTest(
                "Define MIGRATION_TEST_DATABASE_URL to run migration integration tests."
            )
        return url

    def _build_alembic_config(self, database_url: str) -> Config:
        backend_dir = Path(__file__).resolve().parents[1]
        alembic_ini = backend_dir / "alembic.ini"
        config = Config(str(alembic_ini))
        config.set_main_option("sqlalchemy.url", database_url)
        return config

    def test_upgrade_head_creates_v2_tables(self) -> None:
        database_url = self._get_test_database_url()
        config = self._build_alembic_config(database_url)

        engine = create_engine(database_url, future=True)
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise unittest.SkipTest(f"Database unavailable for migration tests: {exc}") from exc

        command.upgrade(config, "head")

        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        expected = {"ingredients", "dishes", "dish_ingredients", "stock_transactions"}
        missing = expected - table_names
        self.assertFalse(missing, f"Missing expected tables after upgrade: {sorted(missing)}")

    def test_downgrade_base_drops_v2_tables(self) -> None:
        database_url = self._get_test_database_url()
        config = self._build_alembic_config(database_url)

        command.upgrade(config, "head")
        command.downgrade(config, "base")

        engine = create_engine(database_url, future=True)
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())

        dropped = {"ingredients", "dishes", "dish_ingredients", "stock_transactions"}
        surviving = dropped & table_names
        self.assertFalse(surviving, f"Tables should not exist after downgrade: {sorted(surviving)}")


if __name__ == "__main__":
    unittest.main()
