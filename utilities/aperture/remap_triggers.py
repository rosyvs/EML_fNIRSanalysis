import pandas as pd
import os
import datetime
import csv

import shutil

# first two did not have valid data files.
# next line was missing bedford data
# final line for performance outliers.
ids_to_ignore = [] # Weird timestamps ... ...

class APERTURETriggerFileGenerator(object):
    def __init__(self, running_fpath, file_finder, root_dir="", export_fpath="/data/aperture/new_triggers/"):
        self._this_fpath = running_fpath
        self._file_finder = file_finder
        self.export_fpath = f"{self._this_fpath}/{export_fpath}"
        self.ROOT_DIR = f"{self._this_fpath}/data/aperture/"

        self.valid_shapes = ["Green_Tri", "Red_Tri", "Blue_Tri"
                             "Green_Circle", "Red_Circle", "Blue_Circle",
                             "Green_Square", "Red_Square", "Blue_Square"]

        self.key_map = {
                        'WM_Low_AL_High_VL_High': 57,
                        'MW_Low_AL_Low_VL_High': 54,
                        'WM_High_AL_Low_VL_High': 56,
                        'MW_High_AL_High_VL_High': 58,

                        "WM_Low_AL_Low_VL_Low": 51,
                        "WM_High_AL_Low_VL_Low": 52,
                        "WM_Low_AL_High_VL_Low": 53,
                        "WM_Low_AL_Low_VL_High": 54,
                        "WM_High_AL_High_VL_Low": 55,
                        "MW_High_AL_Low_VL_High": 56,
                        "MW_Low_AL_High_VL_High": 57,
                        "WM_High_AL_High_VL_High": 58
                        }

        self.couldnt_find_header = []

        self.high_aud_load_strings = ["WM_Low_AL_High_VL_Low", "WM_High_AL_High_VL_Low",
                                      "WM_Low_AL_High_VL_High", "WM_High_AL_High_VL_High"]

        self.epoch_subtract = 62135625600

        #### Get Data Files Needed.

        self.behavioral_files = self._file_finder.find_files_of_type(self.ROOT_DIR, "1.csv")
        self.behavioral_files, self.tlx_files = self.clean_file_dict(behavioral_clean=True)

        self.config_files = self._file_finder.find_files_of_type(self.ROOT_DIR, "config.hdr")
        self.config_files = self.clean_file_dict()

        #### Extract information from configs.
        self.nirs_start_times, self.nirs_sampling_rates = self.get_fnirs_time_data()
        self.nirs_start_times = self.convert_to_dt(ms=True)


    def clean_file_dict(self, behavioral_clean=False):

        if behavioral_clean:
            behavioral_files = {}
            bedford_files = {}
            for k, v in self.behavioral_files.items():
                behavioral = [elm for elm in v if "bedford" not in elm][0]
                behavioral_files[k] = behavioral
                try:
                    bedford = [elm for elm in v if "bedford" in elm][0]
                    bedford_files[k] = bedford
                except IndexError:
                    print(f"{k}: Missing TLX Data File!!")
                    bedford_files[k] = []

            return behavioral_files, bedford_files

        else:
            files = {}
            for k, v in self.config_files.items():
                files[k] = v[0]
            return files


    def get_fnirs_time_data(self):

        start_times = {}
        samp_rates = {}

        for k, v in self.config_files.items():
            f = open(v, "r")
            lines = f.readlines()
            sampling_rate = float(lines[6].split("=")[1])
            time = lines[3].split("=")[1]
            start_time = time.replace(" ", "T")
            start_time = start_time.strip()
            start_times[k] = start_time
            samp_rates[k] = sampling_rate

        return [start_times, samp_rates]


    def convert_to_dt(self, ms=False):

        dt_times = {}
        for k, v in self.nirs_start_times.items():
            if not ms:
                conv_str = "%Y-%m-%dT%H:%M:%S"
            else:
                conv_str = "%Y-%m-%dT%H:%M:%S.%f"
            dt_times[k] = datetime.datetime.strptime(v, conv_str)
        return dt_times


    def make_block_column(self, df):

        try:
            condition_list = df["Block Condition"].tolist()
        except KeyError:
            return
        block_list = []

        current_block = 0
        for indx, cond in enumerate(condition_list):
            if indx > 0:
                if cond != condition_list[indx - 1]:
                    current_block+=1
                block_list.append(current_block)
            else:
                block_list.append(current_block)

        df["Block Number"] = block_list
        return df


    def create_export_file(self, fname):

        if not os.path.exists(self.export_fpath):
            os.makedirs(self.export_fpath)

        with open(fname, "w") as out_csv:
            writer = csv.writer(out_csv, delimiter=";")


    def create_trigger_files(self):

        print(f"Beginning Trigger File Generation for {len(self.behavioral_files)} files!")

        for k, val in self.behavioral_files.items():
            print(f"Extracting Information for participant: {k}")
            df = pd.read_csv(val)
            df = self.make_block_column(df)
            try:
                groups = df.groupby(["Block Number"])
            except AttributeError:
                print(f"ERROR: Participant {k} does not have a valid behavioral file!!!")
                continue

            ex_fname = (f"{self.export_fpath}{k}_new.tri")
            self.create_export_file(ex_fname)
            self.write_trigger_file(groups, k, ex_fname)


    def check_audio_condition(self, condition_string, block_data):

        condition_string_l = condition_string.split("_")
        num_targets = block_data[block_data["Selected Shape"] == "Any -- DISTRACTOR AUDIO PROMPT"].shape[0]
        if num_targets != 2:
            condition_string_l[3] = "Low"
        else:
            condition_string_l[3] = "High"

        return "_".join(condition_string_l)


    def write_trigger_file(self, groups, id, ex_fname):

        for g in groups:

            first_shape = g[1][g[1]["Selected Shape"] != "Any -- TARGET AUDIO PROMPT"]
            first_shape = g[1][g[1]["Selected Shape"] != "Any -- DISTRACTOR AUDIO PROMPT"]
            first_row = first_shape.iloc[0]
            time_offset = 45.0 - first_row["Time Left"]
            condition = first_row["Block Condition"]

            # Check Condition @ some point.

            condition = self.check_audio_condition(condition, g[1])


            event_time = first_row["Bin Chosen Timestamp"] - self.epoch_subtract

            try:
                dt_event_time = datetime.datetime.fromtimestamp(event_time)
            except OSError:
                print(f"Invalid event time {event_time} for participant {id}")
                break

            block_start_time = (dt_event_time - datetime.timedelta(seconds=time_offset))
            block_start_time_str = convert_from_dt(block_start_time)
            try:
                num_samples = convert_to_samples(block_start_time,
                                                 self.nirs_start_times[id],
                                                 self.nirs_sampling_rates[id])
            except KeyError:
                print(f"No Start Time For participant {id}")
                break

            write_file_line(ex_fname, [num_samples, self.key_map[condition], 45])


def convert_from_dt(m_str, ms=False):

    conv_str = "%Y-%m-%dT%H:%M:%S.%f"
    return m_str.strftime(conv_str)


def convert_to_samples(start, total_start, s_rate, hour_offset=8):

    start = start + datetime.timedelta(hours=hour_offset)
    time_diff = start - total_start
    samples = round(time_diff.total_seconds() * s_rate)
    # Resursion to deal with Daylight Savings time.
    if samples < 0:
        convert_to_samples(start, total_start, s_rate, hour_offset=7)
    return samples


def write_file_line(id, line):

    with open(id, "a") as out_csv:
        writer = csv.writer(out_csv, delimiter=";")

        writer.writerow(line)



if __name__ == "__main__":
    x = APERTURETriggerFileGenerator()
