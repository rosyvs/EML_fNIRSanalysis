# DotNIRSPythonTools
Preprocessing Objects and Methods meant to work on .nirs files obtained from
nirsSport2 devices from NIRx.

# Putting data into this repo.

Please make a folder called `./data/zipped/` and place all of the zip archives of data in there. I tried 17 times to make this easy, but the data for EML is just too large. Also, not storing data here means I can keep this repository public.

### Current State.
Currently, this code is for use purely for cleaning, extracting, and labeling the
localizer data from the EML study. The scripts are being actively modified to be more generic.
As this process happens things will be moved from the utilities.eml folder to the utilities.generic folder.

### How to run.
The idea is to include multiple pipelines that can be run simply over a large set of data to achieved the desired format.
The one pipeline is currently kept in root. It is heavily documented, but at a high level of abstraction. All of the details
should be well commented in the code. If there is confusion, ask, and I can write more comments, more through docstrings, etc.

Currently:

`./eml_localizer_pipeline.py` is the one stop shop. More pipelines (and code needed for these pipelines) will be added shortly over the next week.
This will currently work on the one datafile provided in this directory, located in `./data/zipped/`, but it is generic enough such that it should
operate on the entire EML fNIRS dataset.

### Warnings:

Some of the stuff used is specific to the localizer task. This is the MOST complicated pipeline possible, as it is relabeling
and discarding data not relevant to the localizers. If there is something that is confusing about why some operations are being performed, bear in mind
that it may be specific to this one case. These instances, I believe, are commented for the most part.

*Data is always COPIED, never MODIFIED* running this will almost certainly take a decent amount disk space. You can always undo the pipeline by running:
`./wipe_state_clean.py`.

*Only has been tested on Windows.* It should still run on mac and linux, however.

### Notes:
1. Data has been removed from the EML1_055.zip folder so that it could be stored in this repository.
2. Even still, this data needs to be stored using git-lfs. It may not properly download if you do not have git-lfs on your machine.
