import glob
import collections

import handle_zip_file

FILE_COUNT = 100

total_hand_count = 0
total_known_errors = collections.Counter()
# Asserts and errors would raise an exception

for ind, fn in enumerate(glob.glob("/mnt/Downloads/poker/NL100/*.zip")):
 hands, known_errors, _, _ =\
  handle_zip_file.ProcessZipFile(fn, "/home/misha/temp/temp",
   assert_reraise=True)

 total_hand_count += len(hands)
 total_known_errors.update(known_errors)
 print(f"Hand count {total_hand_count}")
 
 if ind >= FILE_COUNT:
  break

for k,v in total_known_errors.items():
 print(f"{k}: {v}")

