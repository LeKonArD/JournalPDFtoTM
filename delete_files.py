import sys
import os
import re

files = list()
for dirpath, dirnames, filenames in os.walk("./out"):
    for filename in [f for f in filenames if f.endswith(".txt")]:
        files.append(os.path.join(dirpath, filename))

for filepath in files:
	if re.match(".*dummy|.*Eingesandte Bücher",filepath):
		os.remove(filepath)
		print("deleted "+filepath)
files = list()
for dirpath, dirnames, filenames in os.walk("./out_notes"):
    for filename in [f for f in filenames if f.endswith(".txt")]:
        files.append(os.path.join(dirpath, filename))

for filepath in files:
	if re.match(".*dummy.txt|.*Eingesandte Bücher",filepath):
		os.remove(filepath)	
		print("deleted "+filepath)
