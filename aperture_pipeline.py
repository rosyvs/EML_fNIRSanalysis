import os

from utilities.generic.recursive_unzip import RecursiveUnzipper
from utilities.generic.file_finder import FileFinder

from utilities.aperture.remap_triggers import APERTURETriggerFileGenerator
from utilities.aperture.trigger_pusher import APERTURETriggerPusher

def main():

    running_fpath = os.path.dirname(os.path.realpath(__file__))
    file_finder = FileFinder(par_id_pattern="[0-9][0-9][0-9][0-9]00") # This is used by a lot of the classes to find fpaths to data, so it's best if it's created here and passed to them.

    # unzipper = RecursiveUnzipper()
    # unzipper.set_root_dir(f"{running_fpath}/data/aperture/zipped/")
    # unzipper.set_unzipped_dir(f"{running_fpath}/data/aperture/unzipped/")
    # unzipper.extract_files()

    # t_file_generator = APERTURETriggerFileGenerator(running_fpath, file_finder)
    # t_file_generator.create_trigger_files()

    trigger_pusher = APERTURETriggerPusher(running_fpath, file_finder)
    trigger_pusher.push_triggers_to_nirs()





if __name__ == "__main__":
    main()
