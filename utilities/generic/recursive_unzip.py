import zipfile
import os

from pathlib import Path

class RecursiveUnzipper(object):
    """
    Methods that operate on an UNZIPPED root directory with ZIPPED directories inside.

    Args (Optional):
        root_dir: The UNZIPPED root directory in which the ZIPPED directories are located.
        unzipped_dir: The NEW root directory where all the ZIPPED directories are extracted to.
    """
    def __init__(self, root_dir="./data/zipped/", unzipped_dir="./data/unzipped/"):
        self.unzipped_dir = Path(unzipped_dir)
        self.root_dir = Path(root_dir)
        self.create_unzipped_dir()


    def set_unzipped_dir(self, new_dir):

        self.unzipped_dir = Path(new_dir)
        self.create_unzipped_dir()


    def set_root_dir(self, new_root):

        self.root_dir = Path(new_root)
        if not os.path.exists(self.root_dir):
            print("WARNING: root_dir is set to a path that does not exist... ...")


    def create_unzipped_dir(self):
        """
        Checks if current unzipped_dir is an actual path. If it isn't it creates it.
        NOTE: will also create any parent folders to the specified directory.

        Args:
            self.unzipped_dir(Path()): Path object to the new root.

        Returns:
            None. (Creates the parent folder).
        """
        if not os.path.exists(self.unzipped_dir):
            os.makedirs(self.unzipped_dir)


    def extract_files(self):
        """
        Extracts all the nested zip folders from the root dir and moves them to the new specified unzipped_dir.

        Args:
            root_dir: The UNZIPPED root directory in which the ZIPPED directories are located.
            unzipped_dir: The NEW root directory where all the ZIPPED directories are extracted to.

        Returns:
            unzipped_fpaths(dict): Keys are original directory names. Values are strings of filepaths.
        """

        unzipped_fpaths = {}
        for zipfname in os.listdir(self.root_dir):
            with zipfile.ZipFile(f"{self.root_dir}\{zipfname}", "r") as zip_r:
                print(f"Extracting {zipfname} to location: {self.unzipped_dir}\{zipfname[:-4]}")
                zip_r.extractall(f"{self.unzipped_dir}\{zipfname[:-4]}")
                unzipped_fpaths[zipfname[:-4]] = f"{self.unzipped_dir}\{zipfname[:-4]}"

        return unzipped_fpaths


if __name__ == "__main__":
    _mUnzipper = RecursiveUnzipper()
