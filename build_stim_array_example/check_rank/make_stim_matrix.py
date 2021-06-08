import pandas as pd
import numpy as np

from scipy.io import loadmat, savemat
import os

from pathlib import Path

def build_stim_channel(trigger_df, num_samples):
    """Builds an indivdiaul stimulus channel to be placed into the .nirs file.

    Args:
        trigger_df: a dataframe with trigger information.
        num_samples(int): the number of samples in each channel of data (n timepoints).

    Returns:
        m_channel(np.array): new stim channel dims = 1 X num_samples.
    """

    m_channel = np.zeros(num_samples) # make an array of len num_samples - set all values to zero.
    for row in trigger_df.iterrows(): # iterate through each onset.
        m_channel[int(row[1]["onset"])] = 1 # mark the onset sample to 1.
        for x in range(int(row[1]["duration"])): # for number of samples in duration.
            m_channel[(int(row[1]["onset"])) + x] = 1 # mark each sample (x [current interation] + onset) to 1.

    return m_channel

EXPORT_DIR = Path(f"{os.getcwd()}/out/")

nirs_f = loadmat(Path(f"{os.getcwd()}/EML1_055/EML1_055.nirs"))
num_samples = nirs_f["t"].shape[0]
trigger_file = pd.read_csv("./stim_info.csv")
by_trigger_groups = trigger_file.groupby("stimType") # will group into two sub dataframes where 1 is trigger, and 2 is trigger.

stim_matrix = [] # create an empty list to 'catch' stim channels through each loop.
for g in by_trigger_groups: # iterate through the groups
    stim_channel = build_stim_channel(g[1], num_samples) #g[1] is the subdataframe from the iteration.
    stim_matrix.append(stim_channel)

nirs_f["s"] = np.array(stim_matrix).transpose()
savemat(f"{EXPORT_DIR}/test_rank.nirs", nirs_f)

# print(np.array(stim_matrix).transpose()) # turn list of np.arrays in an np.array of arrays and flip the x,y dims of the array.
