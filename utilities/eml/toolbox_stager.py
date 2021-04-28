import os
import shutil
import pandas as pd
from pathlib import Path

class ToolboxStager(object):
    def __init__(self, running_fpath, data_table_fpath):
        self._this_fpath = running_fpath
        self.data_table_fpath = data_table_fpath
        self.ROOT_DIR = Path(f"{self._this_fpath}/data/unzipped/")
        self.STAGING_DIR = Path(f"{self._this_fpath}/data/toolbox_staging/")


    def clean_df_of_sketchy_sessions(self, df):
        # TODO this does NOT generate a warning if there is no .tri file - only if triggers are missing in an existing .tri file.
        # Only move files whose triggers are all there for localizer.
        # Drop any row where a file is missing.
        df.dropna(inplace=True)
        # Drop any row where triggers are missing FOR LOCALIZER.
        try:
            df[["is_missing", "junk"]] = df["Trigger Notes"].str.split(":", expand=True)
            df = df[df["is_missing"] != "Missing"]
            df.drop(["is_missing", "junk"], axis=1, inplace=True)
        except ValueError:
            print("No files were found to be missing in this data set. Staging full dataset.")

        df.reset_index(inplace=True)

        return df


    def stage_files(self):

        df = pd.read_csv(self.data_table_fpath)
        df = self.clean_df_of_sketchy_sessions(df)

        staged_fpaths = []
        for row in df.iterrows():
            print(f"Moving NIRS files from: {row[1]['nirs_dir']}, to: {self.STAGING_DIR}/{row[1]['participant']}/")
            shutil.copytree(Path(row[1]["nirs_dir"][2:-2]), f"{self.STAGING_DIR}/{row[1]['participant']}/")
            staged_fpaths.append(f"{self.STAGING_DIR}/{row[1]['participant']}/")

        return staged_fpaths


if __name__ == "__main__":
    main()
