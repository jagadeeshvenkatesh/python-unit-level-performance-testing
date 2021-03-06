from QuickPotato.utilities.templates import default_test_case_name
from QuickPotato.database.actions import DatabaseActions
from datetime import datetime
import tempfile


class TimeSpentStatisticsExport(DatabaseActions):

    def __init__(
            self,
            test_case_name=default_test_case_name,
            test_id=None,
            uuid=None,
            delimiter=",",
            path=None,
            purge_database_after_export=False
    ):

        super(TimeSpentStatisticsExport, self).__init__()
        self.test_case_name = test_case_name
        self.uuid = uuid
        self.test_id = self.select_previous_test_id(test_case_name) if test_id is None else test_id
        self.delimiter = delimiter
        self.path = path
        self.purge_database_after_export = purge_database_after_export

    def fetch_call_stacks(self):
        """

        :return:
        """
        if self.uuid is not None:

            return self.select_call_stack(
                database_name=self.test_case_name,
                uuid=self.uuid
            )

        elif self.test_id is not None:

            return self.select_all_call_stacks(
                database_name=self.test_case_name,
                test_id=self.test_id
            )

        else:
            raise NotImplementedError

    def to_csv(self):
        """

        :return:
        """
        dataframe = self.fetch_call_stacks()
        if self.path is None:
            self.path = tempfile.gettempdir() + "\\" if '\\' in tempfile.gettempdir() else "/"
            print(f"Saving export to {self.path}")

        if len(dataframe) > 0:
            dataframe.to_csv(
                path_or_buf=f"{self.path}raw_export_of_{self.test_id}_{str(datetime.now().timestamp())}.csv",
                sep=self.delimiter,
                index=False
            )
            if self.purge_database_after_export is True:
                self.delete_result_database(database_name=self.test_case_name)

        else:
            raise NotImplementedError
