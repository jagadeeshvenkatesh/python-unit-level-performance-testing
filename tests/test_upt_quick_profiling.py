from QuickPotato.database.management import DatabaseManager
from QuickPotato.configuration.management import options
from sqlalchemy_utils import database_exists
from sqlalchemy import create_engine
from demo.example_code import *
import unittest

SAMPLE_SIZE = 10
UNIT_TEST_DATABASE_NAME = "upt_unit_tests_regression_detection_with_t_test"


class TestUsage(unittest.TestCase):

    def setUp(self):
        """

        """
        options.enable_intrusive_profiling = True

    def tearDown(self):
        """

        """
        options.enable_intrusive_profiling = False

    @staticmethod
    def clean_up_database():
        """

        """
        database_manager = DatabaseManager()
        database_manager.delete_result_database(UNIT_TEST_DATABASE_NAME)

    def test_profiling_outside_of_test_case(self):

        for _ in range(0, SAMPLE_SIZE):
            fast_method()

        # Checking if a database has been spawned
        database_manager = DatabaseManager()
        url = database_manager.validate_connection_url(UNIT_TEST_DATABASE_NAME)
        engine = create_engine(url, echo=True)

        self.assertTrue(database_exists(engine.url))