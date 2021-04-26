import os

from utilities.generic.recursive_unzip import RecursiveUnzipper
from utilities.generic.file_finder import FileFinder

#for eml
from utilities.eml.data_state_table_generator import DataTableGenerator
from utilities.eml.toolbox_stager import ToolboxStager

#for localizers specifically.
from utilities.eml.localizers.trigger_file_modulator import TriggerModulator
from utilities.eml.localizers.trigger_pusher import TriggerPusher

def main():

    # Reference to current path that THIS script is being executed from.
    # This is used so that that ./data/unzipped/ folder is created in the
    # SAME folder that this script is run in.
    running_fpath = os.path.dirname(os.path.realpath(__file__))
    file_finder = FileFinder() # This is used by a lot of the classes to find fpaths to data, so it's best if it's created here and passed to them.

    unzipper = RecursiveUnzipper()
    table_generator = DataTableGenerator(running_fpath, file_finder) # Data table gen needs CURRENT fpath (script execution fpath) and file finder object.

    # Run the objects pipelines to create new copies of data.
    unzipped_fpaths = unzipper.extract_files()

    # Create a data state table. This should be both human readable as well as
    # used as input for the next steps in the process.
    table_fpath = table_generator.gen_data_table()

    # Makes a copy of JUST THE NIRS DATA AND RELEVANT FILES (triggers, configs, etc). This is done to ensure that you are working
    # off of a SEPARATE COPY OF THE DATA. That way, if you eff up, you can just call 'wipe_state_clean.py' and redo.
    stager = ToolboxStager(running_fpath, table_fpath)
    staged_fpaths = stager.stage_files()

    # Creates new trigger files for the localizers with better info about what events are happening when.
    # It also gives hooks for the next object to cut the nirs files at.
    trigger_modulator = TriggerModulator(running_fpath, file_finder, table_fpath)
    trigger_modulator.update_trigger_files()

    # Final Step after extracting all this information and making copies.
    # This does the work of PUSHING the new trigger data into the nirs files.
    # After this, the files can be loaded into the toolbox.
    trigger_pusher = TriggerPusher(running_fpath, file_finder)
    trigger_pusher.push_triggers_to_nirs()


if __name__ == "__main__":
    main()
