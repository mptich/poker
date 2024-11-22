import glob

import handle_zip_file

for fn in glob.glob("/mnt/Downloads/poker/NL100/*.zip"):
 handle_zip_file.ProcessZipFile(fn, "/home/misha/temp/temp", assert_reraise=True)
