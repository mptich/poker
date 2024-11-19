import argparse
import os
import shutil
import glob
import sys

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

def ProcessZipFile(input_file, folder):
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
 total_known_errors = 0
 total_bad_errors = 0

 for ind, fn in enumerate(glob.glob(os.path.join(temp_folder, "*"))):
  new_hands, known_error_count, bad_error_count = \
   utils.ProcessRecordFile(fn=fn, org_file=args.input_file)
  hands += new_hands
  total_known_errors += known_error_count
  total_bad_errors += bad_error_count

 shutil.rmtree(temp_folder)
 return hands, total_known_errors, total_bad_errors

if __name__ == '__main__':
 args = ParseArgs()
 hands, known_errors, bad_errors = ProcessZipFile(args.input_file, args.folder)
 print(f"{len(hands)} hands, {known_errors} known errors, "\
  f"{bad_errors} bad errors found in {args.input_file}")

