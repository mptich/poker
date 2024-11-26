import glob
import collections
import random

import handle_zip_file

FILE_COUNT = 100

total_hand_count = 0
total_known_errors = collections.Counter()
# Asserts and errors would raise an exception

files = list(glob.glob("/mnt/Downloads/poker/NL100/*.zip"))
selected_files = random.sample(files, FILE_COUNT)

#JUSTATEMP
selected_files=["/mnt/Downloads/poker/NL100/2024-09-16_CO_NL100_FR_MFCXDHP23.zip"]
for fn in selected_files:
 hands, known_errors, _, _ =\
  handle_zip_file.ProcessZipFile(fn, "/home/misha/temp/temp",
   assert_reraise=True)

 total_hand_count += len(hands)
 total_known_errors.update(known_errors)
 print(f"Hand count {total_hand_count}")
 
for k,v in total_known_errors.items():
 print(f"{k}: {v}")

