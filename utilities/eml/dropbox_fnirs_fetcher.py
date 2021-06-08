import os
from pathlib import Path
import shutil
import sys 

# copy only the data required for fNIRS analysis to the ./data/unzipped folder
IN_DIR = Path("C:/Users/roso8920/Dropbox (Emotive Computing)/EyeMindLink/Data/") # your path to the Dropbox folder
OUT_DIR = Path("../../data/unzipped/")
os.chdir(os.path.dirname(sys.argv[0]))
current_dir = Path.cwd()
print(f"Current dir: {current_dir}")
fnroot = 'EML1_'
participants = range(128,130) # recall that range is exclusive in Python - it will do first : end-1

for p in participants:
    pID= fnroot + '{:03d}'.format(p)  
    print("Fetching pID: {0}".format(pID))
    if os.path.isdir(Path(f"{IN_DIR}/{pID}/fNIRS")):
        print("    Found fNIRS for pID: {0}".format(pID))
        # create pID directory in unzipped
        os.makedirs(Path(f"{OUT_DIR}/{pID}"),exist_ok=True)
       
        # copy fNIRS
        shutil.copytree(Path(f"{IN_DIR}/{pID}/fNIRS"), Path(f"{OUT_DIR}/{pID}"),dirs_exist_ok=True)

        # copy other useful data
        shutil.copy(Path(f"{IN_DIR}/{pID}/{pID}_Trials.txt") , Path(f"{OUT_DIR}/{pID}/{pID}_Trials.txt"))
        # TODO events.csv

    else: 
        print(" !! No fNIRS for pID: {0}".format(pID))


