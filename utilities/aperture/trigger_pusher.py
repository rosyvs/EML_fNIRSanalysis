import pandas as pd
import os

from scipy.io import loadmat, savemat
import numpy as np
from shutil import copytree

from pathlib import Path
import re
import random

from utilities.generic.run_cutter import RunCutter


class APERTURETriggerPusher(object):
    """
    Pushes triggers from .lsl files into the .nirs files.
    """
    def __init__(self, running_fpath, file_finder, root_dir_suffix="/data/aperture/unzipped/",
                 export_dir_suffix="/data/aperture/new_nirs/",
                 trigger_dir_suffix="/data/aperture/new_triggers/",
                 truncate_triggers=[],
                 decompose_dict={}):
        self._this_fpath = running_fpath
        self.file_finder = file_finder
        self.truncate_triggers = truncate_triggers
        self.decompose_dict = decompose_dict

        if self.truncate_triggers:
            self.run_cutter = RunCutter()
        else:
            self.run_cutter = None

        self.ROOT_DIR = Path(f"{self._this_fpath}{root_dir_suffix}")
        self.EXPORT_DIR = Path(f"{self._this_fpath}{export_dir_suffix}")
        self.TRIGGER_DIR = Path(f"{self._this_fpath}{trigger_dir_suffix}")

        self.nirs_fpaths = self.file_finder.find_files_of_type(self.ROOT_DIR, ".nirs")
        # self.nirs_fpath_dict = {}
        # for k, val in self.nirs_fpaths.items():
        #     self.nirs_fpath_dict[k] = val[0]
        # self.nirs_fpaths = self.nirs_fpath_dict



    def build_stim_channel(self, trigger_df, ch_len):
        """Builds an indivdiaul stimulus channel to be placed into the .nirs file.

        Args:
            trigger_df: a dataframe with trigger information.
            ch_len(int): the number of samples in each channel of data (n timepoints).
            truncate_index(int): pointer in ch_len where the new stim channel should begin.

        Returns:
            m_channel(np.array): new stim channel dims = 1 X ch_len - (ch_len - truncate_index).
        """

        m_channel = np.zeros(ch_len)
        for row in trigger_df.iterrows():
            m_channel[int(row[1]["SampleIndx"])] = 1
        try:
            for x in range(int(row[1]["Duration"])):
                m_channel[int(row[1]["SampleIndx"]) + x] = 1
        except IndexError:
            print("Odd File")

        return m_channel


    def build_new_stim_array(self, trigger_file, ch_len, truncate_index=0):
        """Builds the new 's' attribute in the .nirs file.

        Args:
            trigger_file(str): file path to the trigger file. The trigger file should have attributes
            'onset', 'duraation', and 'value' (stim type).
            ch_len(int): Channel Length of the datafile. This should be the number of samples in the .nirs file.

        Returns:
            np.array() of dims trigger_file["values"].unique().count() X ch_len.
        """

        col_names = ["SampleIndx", "Trigger_Value", "Duration"]
        df = pd.read_csv(trigger_file, sep=";", names=col_names)
        groups = df.groupby(["Trigger_Value"])

        try:
            if df["SampleIndx"].tolist()[0] < 0:
                return np.array([])
            if df["SampleIndx"].tolist()[-1] > ch_len:
                return np.array([])
        except IndexError:
            return np.array([])

        stim_array = []
        # This is going to REWRITE BY TRIGGER VALUE. I.E. stim_channel1 is going to be
        # the lowest NUMBER lsl trigger.
        for g in groups:
            stim_channel = self.build_stim_channel(g[1], ch_len)
            stim_array.append(stim_channel)

        return np.array(stim_array).transpose()


    def save_new_nirs(self, nirs_file, nirs_path, root_export_dir, id):
        """Saves the new .nirs file to self.EXPORT_DIR.

        NOTE: This does not overwrite the original .nirs that was fed into the program.

        Args:
            nirs_file(dict): data to be written out to a matlab file.
            nirs_path(str): path where original datafile was stored.
            root_export_dir(str): directory where new nirs file will be stored.
            id(str): participant ID.
        Returns:
            None (saves out file).
        """

        copytree(f"{nirs_path}", f"{root_export_dir}/{id}")
        old_nirs_f = [fname for fname in os.listdir(f"{root_export_dir}/{id}") if ".nirs" in fname][0]
        os.remove(f"{root_export_dir}/{id}/{old_nirs_f}")
        savemat(f"{root_export_dir}/{id}/{id}.nirs", nirs_file)


    def find_matching_trigger(self, k, trigger_dir):
        """Finds and returns matching trigger file based on nirs file.

        Args:
            k(string): 'key' (aka, participant ID).
            trigger_dir(str): filepath to the directory where the trigger files are stored.

        Returns:
            list: potential matching trigger filees for that ID (usually 1).
        """

        try:
            trigger_fname = [elm for elm in os.listdir(trigger_dir) if k in elm][0]
        except IndexError:
            print("No trigger file found.")
            return None

        return trigger_fname


    def push_triggers_to_nirs(self):
        """Main method of object. Iterates through all of the times in the target directory
        (self.ROOT_DIR) and modulates the nirs files based on the trigger files. Pushes the stims
        from the triggers into be stim channels than the nirSport2 originally provides.

        Args:
            None (uses params from __init__).
        Returns:
            None (calls self.save_new_nirs()).
        """

        for k, val in self.nirs_fpaths.items():

            nirs_f = loadmat(val[0])
            root_folder = val[0].split("\\")[:-1]
            root_folder = ("\\").join(root_folder)
            root_folder = root_folder + "\\"
            trigger_f = self.find_matching_trigger(k, self.TRIGGER_DIR)

            if not trigger_f:
                continue

            col_names = ["SampleIndx", "Trigger_Value", "Duration"]
            df = pd.read_csv(f"{self.TRIGGER_DIR}/{trigger_f}", sep=";", names=col_names)
            df = df.reset_index()

            stim_ch_len = nirs_f["s"].shape[0]
            new_stim_data = self.build_new_stim_array(f"{self.TRIGGER_DIR}/{trigger_f}",
                                                      stim_ch_len)
            nirs_f["s"] = new_stim_data
            self.save_new_nirs(nirs_f, root_folder, self.EXPORT_DIR, k)


if __name__ == "__main__":
    main()
