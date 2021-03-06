from QuickPotato.configuration.settings import Boundaries, RegressionSettings
from QuickPotato.utilities.templates import default_test_case_name
from QuickPotato.statistics.hypothesis_tests import TTest
from QuickPotato.harness.results import Metrics
from QuickPotato.statistics.verification import *
from QuickPotato.database.actions import DatabaseActions
from QuickPotato.harness.reporting import TestReport
from QuickPotato.harness.results import RawData
from datetime import datetime
import string
import random


class UnitPerformanceTest(DatabaseActions, Boundaries, Metrics, RegressionSettings):

    def __init__(self):

        DatabaseActions.__init__(self)
        Boundaries.__init__(self)
        Metrics.__init__(self)
        RegressionSettings.__init__(self)

        self.current_test_id = None
        self.previous_test_id = None
        self.silence_warning_messages = False

        self._test_case_name = None
        self._monitoring_mode = True

    @property
    def benchmark_measurements(self):
        """
        All of the performance measurements that are collected by the benchmark.

        Returns
        -------
            A raw data object that contains all benchmark measurements.
        """
        return RawData(test_id=self.current_test_id, database_name=self._test_case_name)

    @property
    def baseline_measurements(self):
        """
        All of the performance measurements that are collected by the baseline.

        Returns
        -------
            A raw data object that contains all baseline measurements.
        """
        return RawData(test_id=self.previous_test_id, database_name=self._test_case_name)

    @property
    def test_case_name(self):
        """
        The test case name that has been defined in the unit load test.

        Raises
        -------
            AgentCannotFindTestCase If no test case is found
        """
        if self._monitoring_mode is False:
            return self._test_case_name

        else:
            self._create_and_populate_test_case_database(default_test_case_name)
            self.current_test_id = "collected_outside_unit_performance_test"
            return default_test_case_name

    @test_case_name.setter
    def test_case_name(self, value):
        """
        Will update the test case name with the provided value.

        When the test case name is changed by a performance unit test.
        The following automatic action will be performed:

            - Create the database schema and tables.
            - Find the previous test id
            - Create the current test id

        Parameters
        ----------
        value
            the new value of the test case name that will
            be defined by the developer.
        """
        self._create_and_populate_test_case_database(value)
        self._monitoring_mode = False

        # Refresh Test ID's
        self._reset_unit_performance_test(database_name=value)
        self._test_case_name = value

    @property
    def verify_benchmark_against_set_boundaries(self):
        results = self._check_breach_benchmark_defined_boundaries()
        self._save_results_to_test_report(boundaries_breached=results)
        return results

    @property
    def verify_benchmark_against_previous_baseline(self):
        results = self._check_difference_between_baseline_benchmark()
        self._save_results_to_test_report(regression_found=results)
        return results

    def _create_and_populate_test_case_database(self, database_name):
        """
        Will populate the database with the necessary tables.

        Parameters
        ----------
        database_name
            The name of the database_name also known as the test case name
        """
        self.spawn_results_database(database_name)
        self.spawn_time_spent_table(database_name)
        self.spawn_system_resources_table(database_name)
        self.spawn_test_report_table(database_name)
        self.spawn_boundaries_test_evidence_table(database_name)
        self.spawn_regression_test_evidence_table(database_name)
        self.enforce_test_result_retention_policy(database_name)

    def _reset_unit_performance_test(self, database_name):
        """
        The method will reset the unit load test class to it original state.

        Parameters
        ----------
        database_name
            The name of the database also known as the test case name
        """
        self.previous_test_id = str(self.select_previous_passed_test_id(database_name))
        self.current_test_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    def _inspect_benchmark_and_baseline(self):
        """
        Will verify if the benchmark and baseline result can be used in a validation.

        Returns
        -------
            Will return True if the test ids do not match and do not contain a None type.
            Will return False if the test ids do not match the above requirements.
        """
        if self.previous_test_id == "None" or self.current_test_id == "None":
            # No baseline
            return False

        elif self.current_test_id == self.previous_test_id:
            # Test Cases are the same
            raise NotImplemented

        else:
            # Two different test cases regression analysis can be done
            return True

    def _inspect_test_results(self, results):
        """
        Will verify the test results and will give an appropriate output
        and  warning message.

        Returns
        -------
            - True = Test Passed
            - False = Test Failed
            _ None = No test performed (throws an warning message)
        """
        if len(results) == 0:
            if self.silence_warning_messages is False:
                print("Warning no test have been executed against the benchmark")
            return True

        elif False in results:
            return False

        else:
            return True

    def _save_results_to_test_report(self, boundaries_breached=None, regression_found=None):
        """

        :return:
        """
        report = TestReport()
        report.test_id = self.current_test_id
        report.test_case_name = self._test_case_name
        report.epoch_timestamp = datetime.now().timestamp()
        report.human_timestamp = datetime.now()

        if boundaries_breached is not None:
            report.status = boundaries_breached
            report.boundaries_breached = boundaries_breached

        elif regression_found is not None:
            report.status = regression_found
            report.regression_found = regression_found

        else:
            raise NotImplemented

        return report.save()

    def _check_breach_benchmark_defined_boundaries(self):
        """
        This method will validate how well the benchmark will hold up to the
        set threshold in the service level agreement.

        Returns
        -------
            True if the test passes and False if it False
        """
        results = []
        self._collect_measurements(test_id=self.current_test_id, database_name=self._test_case_name)
        for boundary_key, measurements_key in zip(self.boundary_policy, self.threshold_measurements):
            if self.boundary_policy[boundary_key]["max"] is not None:
                results.append(
                    validate_max_boundary_of_measurements(
                        test_id=self.current_test_id,
                        test_case_name=self._test_case_name,
                        validation_name="validate_max_boundary_for_" + measurements_key,
                        boundary=self.boundary_policy[boundary_key]["max"],
                        value=self.threshold_measurements[measurements_key]())
                )
            if self.boundary_policy[boundary_key]["min"] is not None:
                results.append(
                    validate_min_boundary_of_measurements(
                        test_id=self.current_test_id,
                        test_case_name=self._test_case_name,
                        validation_name="validate_min_boundary_for_" + measurements_key,
                        boundary=self.boundary_policy[boundary_key]["min"],
                        value=self.threshold_measurements[measurements_key]())
                )
        return self._inspect_test_results(results)

    def _check_difference_between_baseline_benchmark(self):
        """
        Will test the benchmark against the baseline.
        The following statistical tests are performed in this method:

            - T test

        Returns
        -------
            True = Test Passed
            False = Test Failed
            None = No test performed
        """
        # Validate if there is a proper baseline and benchmark present
        if self._inspect_benchmark_and_baseline():
            results = []

            if self.run_t_test:
                t_test = TTest(
                    test_id=self.current_test_id,
                    test_case_name=self._test_case_name,
                    baseline_measurements=self.baseline_measurements.response_times(),
                    benchmark_measurements=self.benchmark_measurements.response_times()
                )
                results.append(t_test.results)

            return self._inspect_test_results(results)

        else:
            if self.silence_warning_messages is False:
                print("Warning no baseline found so no regression test performed")
            return True
