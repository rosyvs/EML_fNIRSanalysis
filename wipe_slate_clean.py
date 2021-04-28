import os
import shutil

def main():
    """
    Removes any and all files generated from eml_localizer_pipeline.py,
    resetting the repository back to it's native state w/r/t code and data.

    Will NOT get rid of your zipped data.
    WiLL get rid of your unzipped data. So, beware if you're working with a lot,
    and the extraction process is tedious.
    """

    paths = ["./data/unzipped/", "./data/toolbox_staging/",
             "./data/triggers_truncated_localizers",
             "./data/aperture/unzipped/"]

    for p in paths:
        if os.path.exists(p):
            shutil.rmtree(p)

if __name__ == "__main__":
    main()
