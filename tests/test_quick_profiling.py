from QuickPotato.database.management import DatabaseManager
from sqlalchemy_utils import database_exists
from sqlalchemy import create_engine
from tests.stubs import *
import unittest


class TestUsage(unittest.TestCase):
    DEFAULT_SAMPLE_SIZE = 10
    DELETE_TEMPORARY_DATABASE_AFTER_USE = True
    TEMPORARY_UNIT_TEST_DATABASE_NAME = "quick_potato_default_database"

    def tearDown(self):
        if self.DELETE_TEMPORARY_DATABASE_AFTER_USE is True:
            database_manager = DatabaseManager()
            database_manager.delete_result_database(database_name=self.TEMPORARY_UNIT_TEST_DATABASE_NAME)

    def test_profiling_outside_of_test_case(self):

        for _ in range(0, self.DEFAULT_SAMPLE_SIZE):
            fast_method()

        # Checking if a database has been spawned
        database_manager = DatabaseManager()
        url = database_manager.validate_connection_url(database_name=self.TEMPORARY_UNIT_TEST_DATABASE_NAME)
        engine = create_engine(url, echo=True)

        self.assertTrue(database_exists(engine.url))