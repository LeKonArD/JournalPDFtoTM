import os
import sys
import io
import re


print(sys.argv[1])
files = list()
for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
    for filename in [f for f in filenames if f.endswith(".html")]:
        files.append(os.path.join(dirpath, filename))
print(files)
for filename in files:
	if re.match("[0-9]*\/index",filename):
		print("index")
	else:
		regex1=sys.argv[1]+"\/page"
		print(regex1)
		newname = re.sub("[0-9]*\/page","",filename)
		newname = re.sub("\.html","",newname)
		if len(newname) == 1:
			newname = "00"+newname
		if len(newname) == 2:
			newname = "0"+newname
		newname = sys.argv[1]+"/"+newname+".html"
		print(newname)
		print(filename)
		os.rename(filename,newname)
