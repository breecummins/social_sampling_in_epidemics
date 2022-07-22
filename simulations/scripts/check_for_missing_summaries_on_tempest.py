import os

# make sure you are in the correct directory with all of the TASK subfolders on Tempest
# folders that are printed failed during the run

folders = os.listdir()

for f in folders:
    contains = False
    for i in os.listdir(f):
        if i.startswith("summary"):
            contains = True
    if not contains:
        print(f)