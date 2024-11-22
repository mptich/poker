import argparse
import os
import shutil
import glob
import sys
import collections

import utils

# Input folder is guaranteed to NOT be accessed by various processes 
# running in parallel

def ParseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help="Output folder to write to",
     required=True)
    parser.add_argument('-i', '--input_file', help="Input zip file",
     required=True)
    parser.add_argument('-n', '--dont_erase',
     help="Do not erase temp folder (for debugging)", action='store_true')
    parser.add_argument('-a', '--assert_reraise',
     help="Reraise assertions (for debugging)", action='store_true')
    parser.add_argument('-o', '--other_dont_reraise',
     help="Do not reraise other errors", action='store_true')
    args = parser.parse_args()
    return args

def ProcessZipFile(input_file, folder, erase_temp=True, assert_reraise=False,
 other_reraise=True):
 temp_folder = os.path.join(folder, 'temp')
 os.mkdir(temp_folder)

 zip_file = os.path.join(temp_folder, 'my.zip')
 shutil.copy(input_file, zip_file)

 curr_folder = os.getcwd()
 os.chdir(temp_folder)
 os.system(f"unzip {zip_file}")
 os.remove(zip_file)
 os.chdir(curr_folder)

 hands = []
 total_known_errors = collections.Counter()
 assert_count = 0
 error_count = 0

 for ind, fn in enumerate(glob.glob(os.path.join(temp_folder, "*"))):
  new_hands, known_errors, new_asserts, new_errors = \
   utils.ProcessRecordFile(fn=fn, org_file=input_file,
    assert_reraise=assert_reraise, other_reraise=other_reraise)
  hands += new_hands
  total_known_errors.update(known_errors)
  assert_count += new_asserts
  error_count += new_errors

 if erase_temp:
  shutil.rmtree(temp_folder)
 return hands, total_known_errors, assert_count, error_count

if __name__ == '__main__':
 args = ParseArgs()
 hands, known_errors, assert_count, error_count = \
  ProcessZipFile(args.input_file, args.folder, erase_temp=not args.dont_erase,
  assert_reraise=args.assert_reraise,
  other_reraise=not args.other_dont_reraise)
 print(f"The following found in {args.input_file}")
 print(f"{len(hands)} hands, {assert_count} asserts, {error_count} "\
  f" errors\nKnown errors:")
 for k,v in known_errors.items():
  print(f"{k}: {v}")

