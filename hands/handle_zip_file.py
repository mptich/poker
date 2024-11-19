import argparse
import os
import shutil
import glob

import utils

# Input folder is guaranteed to NOT be accessed by various processes 
# running in parallel

def ParseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help="Output folder to write to",
            required=True)
    parser.add_argument('-i', '--input_file', help="Input zip file",
            required=True)
    args = parser.parse_args()
    return args

args = ParseArgs()

temp_folder = os.path.join(args.folder, 'temp')
os.mkdir(temp_folder)

zip_file = os.path.join(temp_folder, 'my.zip')
shutil.copy(args.input_file, zip_file)

curr_folder = os.getcwd()
os.chdir(temp_folder)
os.system(f"unzip {zip_file}")
os.remove(zip_file)
os.chdir(curr_folder)

hands = []
for ind, fn in enumerate(glob.glob(os.path.join(temp_folder, "*"))):
 hands += utils.ProcessRecordFile(fn=fn, org_file=args.input_file)

print(f"{len(hands)} hands found in {args.input_file}")

shutil.rmtree(temp_folder)
