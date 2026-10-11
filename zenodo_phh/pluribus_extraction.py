# Pluribus is 10000 full hand recordings. Pluribus program playing with
# professional players

import zipfile
from pathlib import Path

ZIP_FILE = "/home/misha/temp/zenodo.zip"
OUT_FOLDER = "/home/misha/pluribus"

zip_path = Path(ZIP_FILE)
output_dir = Path(OUT_FOLDER)

wanted = {
    "folder/file1.csv",
    "folder/file2.csv",
    "notes/readme.txt",
}

with zipfile.ZipFile(zip_path, "r") as z:
    for name in z.namelist():
        print(name)
        continue
        if name in wanted:
            z.extract(name, output_dir)
            print("Extracted:", name)
