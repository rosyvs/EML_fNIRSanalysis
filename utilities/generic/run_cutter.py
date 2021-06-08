import pandas as pd

class RunCutter(object):
    def __init__(self):
        pass


    def cut_runs(self, truncate_indexes, nirs_f):
        """
        Cuts a single .nirs file into multiple runs, based on the len of
        truncate_indexes.

        Args:
            truncate_indexes(2 dim list): A list of start and stop samples at which to cut the nirs files.
            nirs_f(dict): A dictionary storing the original nirs files.

        Returns:
            runs(list): List of truncated 'run' files.
        """

        runs = []
        for start_stop in truncate_indexes:
            runs.append(self.truncate_nirs_file(nirs_f, start_stop[0], start_stop[1]))

        return runs


    def truncate_nirs_file(self, nirs_f, truncate_index, end_index):
        """Grabs a section of a .nirs file based on a start point and an end point.

        Args:
            nirs_f(dict): .nirs file object to be modulated.
            truncate_index(int): start point of new nirs data. (in samples)
            end_index(int): end point of new nirs data. (in samples)

        Returns:
            nirs_f (modulated): New nirs data with excess cut out based on cut points.
        """

        _mkeys = ['t', 'd', 's', 'aux']

        for k in _mkeys:
            nirs_f[k] = nirs_f[k][truncate_index:end_index]

        return nirs_f


if __name__ == "__main__":
    print("Under construction.")
