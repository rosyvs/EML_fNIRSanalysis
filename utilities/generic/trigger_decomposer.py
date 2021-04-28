import pandas as pd
import os

class TriggerDecomposer(object):
    def __init__(self, trigger_fpath, decompose_dict={}):
        self.trigger_fpath = trigger_fpath
        self.decompose_dict = decompose_dict
        self.load_trigger_data()


    def set_trigger_fpath(self, n_fpath):

        assert os.path.exists(n_fpath)
        self.trigger_fpath = n_path
        self.load_trigger_data()


    def set_decompose_dict(self, n_dict):

        self.decompose_dict = decompose_dict


    def load_trigger_data(self):

        self.trigger_df = pd.read_csv(self.trigger_fpath, sep=";", names=["t", "sampleIndx", "triggerVal"])


    def decompose_triggers(self):

        if not self.trigger_df:
            self.load_trigger_data()

        new_rows = []
        for row in self.trigger_df.itterrows():
            if row[1]["triggerVal"] in decompose_dict.keys():
                for value in decompose_dict[row[1]["triggerVal"]]:
                    new_rows.append([])
            else:
                new_rows.append(row[1])
