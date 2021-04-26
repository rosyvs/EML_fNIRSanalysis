import pandas as pd
import os
import re

from pathlib import Path

from utilities.generic.file_finder import FileFinder

def list_diff(li1, li2):
    """Returns the subset of lists that are present in li1 but absent in li2.

        Args:
            li1: The first list (a superset of li2).
            li2: The second list (a subset of li1)

        Returns:
            list: a list of the elements present in li1, but not li2."""
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

### NOTE THIS IS SPECIFIC TO EML STUDY CURRENTLY.

class DataTableGenerator(object):
    def __init__(self, running_fpath, file_finder, root_dir="", export_fpath=""):
        self._this_fpath = running_fpath
        self._file_finder = file_finder
        self.export_fpath = export_fpath

        if not root_dir:
            self.ROOT_DIR = Path(f"{self._this_fpath}/data/unzipped/")
        if not self.export_fpath:
            self.export_fpath = Path(f"{self.ROOT_DIR}/data_summaries/eml_summary_nirs.csv")
            if not os.path.exists(Path(f"{self.ROOT_DIR}/data_summaries")):
                os.makedirs(Path(f"{self.ROOT_DIR}/data_summaries"))


    def gen_data_table(self):

        # Get all the file paths needed in order to gather information about all of the sessions.
        self.nirs_fnames = self._file_finder.find_files_of_type(self.ROOT_DIR, ".nirs")
        self.trigger_fnames = self._file_finder.find_files_of_type(self.ROOT_DIR, ".tri")
        self.trial_sheet_fnames = self._file_finder.find_files_of_type(self.ROOT_DIR, "Trials.txt")
        self.nirs_dir_fpaths = self._file_finder.find_files_of_type(self.ROOT_DIR, ".nirs", return_parent=True)

        # Start getting info about the data.
        self.valid_triggers_dict = self.validate_triggers(self.trigger_fnames)
        self.localizer_order_dict = self.get_localizer_order(self.trial_sheet_fnames)
        self.reading_order_dict = self.get_reading_order(self.trial_sheet_fnames)

        # Generate dataframe to collate all of that information and write it to file.
        df = pd.DataFrame([self.nirs_fnames, self.trigger_fnames, self.nirs_dir_fpaths,
                           self.trial_sheet_fnames, self.valid_triggers_dict,
                           self.localizer_order_dict, self.reading_order_dict]).transpose()
        df.index.name = 'participant'

        df.columns = ["NIRS fPath", "Trigger fPath", "nirs_dir",
                      "Trial Sheet fPath", "Trigger Notes",
                      "Localizer Order", "Reading Order"]

        df.to_csv(self.export_fpath)
        return self.export_fpath


    def validate_triggers(self, trigger_fnames):
        """Reads the .lsl trigger file from each participant and makes a few judgements
        about the state of the triggers. These judgements are then written to the data state table later on.

            Args:
                trigger_fnames (dict): key is ID, val is filepath to lsl.tri file for that id.
            Returns:
                triggers_valid (dict): key is ID, val is string describing the state of the triggers.
        """

        localizer_triggers = [25, 27, 24, 22, 23, 26]

        triggers_valid = {}

        for k, val in trigger_fnames.items():
            df = pd.DataFrame()
            for v in val:
                df = df.append(pd.read_csv(v, sep=";", names=["t", "sample", "val"]), ignore_index=True)

            if df.shape[0] == 226:
                triggers_valid[k] = "LSL Triggers Look Good For Whole Study"
            elif df.shape[0] > 226:
                triggers_valid[k] = f"There are {df.shape[0] - 226} more triggers than expected."
            elif df[df["val"].isin(localizer_triggers)].shape[0] == 86:
                triggers_valid[k] = f"LSL Triggers Look Good for Localizer / Resting State, but are {226 - df.shape[0]} triggers short of whole study."
            else:
                triggers_valid[k] = f"Missing: {86 - df[df['val'].isin(localizer_triggers)].shape[0]} in the Localizer / Resting State Task."

        return triggers_valid


    def get_localizer_order(self, trial_fnames):
        """Reads the trial file for each participant and determines the order
        the localizer tasks were presented in.

        Args:
            trial_fnames (dict): key is ID, val is filepath to Trials.txt file for that ID.

        Returns:
            loc_order (dict): key is ID, val is a list with localizer strings as values.
        """

        loc_order = {}
        possible_vals = ["4_jabwords", "3_jabsent", "2_words", "1_sent"]

        for k, val in trial_fnames.items():
            df = pd.read_csv(val[0], skiprows=1, names=["time_info", "event", "val"], sep="\t")
            condition_list = df[df['val'] == 23]["event"].tolist()
            condition_list = [elm.split(" ")[-1] for elm in condition_list]

            missing = list_diff(possible_vals, condition_list)
            if len(missing) == 1:
                condition_list.insert(0, missing[0])
                loc_order[k] = condition_list
            else:
                loc_order[k] = []

        return loc_order


    def get_reading_order(self, trial_fnames):
        """Reads the trial file for each participant and determines the order
        the readings were presented in.

        Args:
            trial_fnames (dict): key is ID, val is filepath to Trials.txt file for that ID.

        Returns:
            loc_order (dict): key is ID, val is a list with reading strings as values.
        """


        read_order = {}

        for k, val in trial_fnames.items():
            df = pd.read_csv(val[0], skiprows=1, names=["time_info", "event", "val"], sep="\t")
            condition_list = df[df['val'] == 7]["event"].tolist()
            condition_list = [elm[:-1] for elm in condition_list]

            # Preserve the order and get rid of repeats
            _cond_list = []
            for elm in condition_list:
                if elm not in _cond_list:
                    _cond_list.append(elm)

            read_order[k] = _cond_list

        return read_order


if __name__ == "__main__":
    _mDataTableGen = DataTableGenerator()
