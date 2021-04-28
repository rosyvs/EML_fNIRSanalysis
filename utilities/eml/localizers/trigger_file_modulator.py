import pandas as pd
import os

from scipy.io import loadmat, savemat
import numpy as np
from shutil import copytree

from pathlib import Path
import re

class TriggerModulator(object):
    """Class that will create a newer, better, faster trigger file: Specific for
    giving information about the localizer tasks.

    Args:
        running_fpath(str): filepath that the calling script is running from.
        file_finder(obj): an object that has some methods for ... ... finding files?
        summary_fpath(str): filepath to the dataset summary table generated via DataTableGenerator() class.
    Returns:
        None. Creates new trigger files in self.EXPORT_DIR.
    """
    def __init__(self, running_fpath, file_finder, summary_fpath):
        self._this_fpath = running_fpath
        self.file_finder = file_finder
        self.summary_fpath = summary_fpath

        self.LOC_DURACTION_SEC = 74
        self.TRUCATION_OFFSET_SEC = 30
        self.END_TUNCATION_OFFSET_SEC = 20
        self.ROOT_DIR = Path(f"{self._this_fpath}/data/toolbox_staging/")
        self.EXPORT_DIR = Path(f"{self._this_fpath}/data/toolbox_staging/triggers_trucated_localizers/")

        if not os.path.exists(self.EXPORT_DIR):
            os.makedirs(self.EXPORT_DIR)

        # remap events with this string to these trigger values, as the raw data uses 22 for all conditions 
        self.loc_map = {"1_sent": 51,
                       "2_words": 52,
                       "3_jabsent": 53,
                       "4_jabwords": 54}


        self.trigger_files = self.file_finder.find_files_of_type(self.ROOT_DIR, ".tri")
        self.header_files = self.file_finder.find_files_of_type(self.ROOT_DIR, ".hdr")



    def get_fnirs_time_data(self, fpath):
        """
        Reads the config file from the experimental session and returns both the
        start time of the recording and the sampling rate of the recording.

        Args:
            fpath(str): filepath to the config.hdr file for the particiular participant.
        Returns:
            start_time(str): string of datetime when recording session started.
            sampling_rate(float): sampling rate of the recording (in Hz).
        """

        f = open(fpath, "r")
        lines = f.readlines()
        sampling_rate = float(lines[6].split("=")[1])
        time = lines[3].split("=")[1]
        start_time = time.replace(" ", "T")
        start_time = start_time.strip()
        return [start_time, sampling_rate]


    def add_new_durations_col(self, df, loc_duration_samples):
        """Adds a new duration column to the existing trigger dataframe. If element
        is not a localizer, duration is 0.

        Args:
            df: The working trigger dataframe object.
            loc_duration_samples(int): The number of samples a localizaer block is.

        Returns:
            df: modulated dataframe with a new durations column.
        """

        durations = []
        for i, elm in enumerate(df["sample"].tolist()):
            if i + 1 == len(df["sample"].tolist()):
                print(elm)
                durations.append(0)
            else:
                durations.append(loc_duration_samples)

        df["duration"] = durations
        return df


    def add_localizer_condition_information(self, df, loc_order):
        """Updates the trigger df 'value' (condition) column to reflect the
        values provided by the Trials file.

        Args:
            df: The working trigger dataframe object.
            loc_order (list): A list of the actual conditions.
        Returns:
            df: modulated dataframe with new 'value' columns.
        """

        # One may ask why I am doing this. The trigger values in the lsl file
        # do not have any information about the TYPE of localizer.
        # This method puts that information into the new trigger file.

        new_val_list = []
        count = 0
        for elm in df["value"].tolist():
            if elm == 23:
                new_val_list.append(self.loc_map[loc_order[count]]) # Grab the int value for the trigger string.
                count += 1
            elif elm == 24:
                new_val_list.append(self.loc_map[loc_order[count]])
                count += 1
            else:
                new_val_list.append(elm)

        df["value"] = new_val_list
        return df


    def add_start_and_stop_triggers(self, df, start_sample, sampling_rate,
                                    loc_duration_samples):
        """Adds a first and last column to the trigger file that will be used to cut the
        DATA files at certain pinch points. These 'pinch points' are determined via
        the constants defined in the __init__ method.

        Args:
            df: The working trigger dataframe object.
            start_sample(int): the FIRST sample we want in the dataframe.
            sampling_rate(float): number of samples per second.
            loc_duration_samples(int): the number of samples each localizer block lasts.

        Returns:
            df2: a modulated df with a start and end sample denoted.
        """

        # You might be asking why I am doing THIS.
        # This is to cut the localizers off from the rest of the data.
        # The start and end triggers will be used by the next step to cut the
        # nirs files down to a more manageable size while still retaining as
        # adequate amount for baseline.

        # Also note --- This is INCREDIBLY SPECIFIC TO THE LOCALIZERS.

        loc_triggers = [27, 51, 52, 53, 54]
        df = df[df["sample"] > start_sample]
        df = df[df["value"].isin(loc_triggers)]
        df.reset_index(inplace=True)
        df2 = df.copy()
        df2.at[0, "sample"] = start_sample
        df2.at[0, "duration"] = 0
        df2.at[1, "duration"] = df2.at[1, "duration"] - 2 * sampling_rate

        end_sample_row = {"index": df2.at[4, "index"] + 1,
                          "t": df2.at[4, "t"],
                          "sample": df2.at[4, "sample"] + (loc_duration_samples + (self.END_TUNCATION_OFFSET_SEC + sampling_rate)),
                          "value": 28,
                          "duration": 0.0}

        df2 = df2.append(end_sample_row, ignore_index=True)
        return df2


    def update_trigger_files(self):
        """Main method for updating trigger files. Method loops through all valid trigger files.
        (i.e. files in the summary table that indicate that nothing is missing or wonkey), and
        creates a new trigger file specific to the localizers in the data.

        Args:
            None (takes params from __init__).
        Returns:
            None (exports new trigger files to self.EXPORT_DIR)"""

        notes_df = pd.read_csv(self.summary_fpath).set_index('participant')

        for k, val in self.trigger_files.items():
            # find matching header file (based on id).
            header = self.header_files[k][0]
            # Get sampling rate from header file.
            fnirs_start, sampling_rate = self.get_fnirs_time_data(header)
            loc_duration_samples = self.LOC_DURACTION_SEC * sampling_rate
            loc_order = notes_df.loc[k]['Localizer Order'][1:-1].replace("'", "").split(', ')

            # REMOVES ALL SENTENCE LEVEL TRIGGERS.
            df = pd.read_csv(val[0], sep=";", names=["t", "sample", "value"])
            df = df[df["value"] != 22]

            df = self.add_new_durations_col(df, loc_duration_samples)
            # REMOVES ALL TASK END TRIGGERS.
            df = df[df["value"] != 26]
            # Add new values based on localizer order.
            df = self.add_localizer_condition_information(df, loc_order)

            # Creates a trigger to indicate the beginning of this RUN.
            # Trigger is created by looking at end of resting state and subtracting
            # TRUNCATION_OFFSET_DURATION.
            rest_end_sample = df[df["value"] == 27]["sample"]
            start_sample = int(rest_end_sample - (self.TRUCATION_OFFSET_SEC * sampling_rate))

            df = self.add_start_and_stop_triggers(df, start_sample, sampling_rate, loc_duration_samples)

            df.to_csv(f"{self.EXPORT_DIR}/{k}_loc_trucated.tri", header=False, index=False)


if __name__ == "__main__":
    pass
