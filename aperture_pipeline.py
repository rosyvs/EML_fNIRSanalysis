import os

from utilities.generic.recursive_unzip import RecursiveUnzipper
from utilities.generic.file_finder import FileFinder

def main():

    running_fpath = os.path.dirname(os.path.realpath(__file__))
    file_finder = FileFinder() # This is used by a lot of the classes to find fpaths to data, so it's best if it's created here and passed to them.

    unzipper = RecursiveUnzipper()
    unzipper.set_root_dir(f"{running_fpath}/data/aperture/zipped/")
    unzipper.set_unzipped_dir(f"{running_fpath}/data/aperture/unzipped/")
    unzipper.extract_files()


if __name__ == "__main__":
    main()
