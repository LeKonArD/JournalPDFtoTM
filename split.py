import re
import io
import os
import sys

def clean(text):

	
	##start tags
	text = re.sub("<\s*([A-Za-z_]\w*)\s*([^\>]+)>","",text)
	##end tags
	text = re.sub("<\/(span|div)","",text)
	##Rest
	text = re.sub(">","",text)
	return text

files = list()
for dirpath, dirnames, filenames in os.walk("./"+sys.argv[1]):
    for filename in [f for f in filenames if f.endswith(".html")]:
        files.append(os.path.join(dirpath, filename))


files.sort()
print(files)


firstsite = list()

title = list()

for filepath in files:
	data = open(filepath,"r", encoding="utf-8")
	## get index
	img = False
	for line in data:
		
		if re.match("<img.*",line):
			img = True
			continue
		if img == True and re.match("<div",line):
			top = re.search("top:[0-9]+px",line)
			top = re.sub("top:|px","",top.group(0))
			if 235 > int(top) > 108:
				if clean(line)[0].isupper() and clean(line)[1].islower() :
					print(clean(line))
					title.append(clean(line))
					firstsite.append(filepath)
					img = False 
		img = False


## Initialwerte
article = "dummy"
titleN = "dummy"
notes = ""
print(firstsite)

a = 0
s = 0
print("-----------------------------------------------------")
for filepath in files:
	data = open(filepath,"r", encoding="utf-8")
	s = s + 1
	start = True
	Fussnoten = False
	
	## process lines
	for line in data:
		## get title
		done = False
		if filepath in firstsite and start == True:
			if not os.path.exists("out/"+sys.argv[1]):
				os.makedirs("out/"+sys.argv[1])

			with io.FileIO("./out/"+sys.argv[1]+"/"+titleN+".txt", "w") as file:
			    	file.write(article.encode("utf-8"))

			if not os.path.exists("out_notes/"+sys.argv[1]):
				os.makedirs("out_notes/"+sys.argv[1])

			with io.FileIO("./out_notes/"+sys.argv[1]+"/"+titleN+".txt", "w") as file:
			    	file.write(notes.encode("utf-8"))

			titleN = title[a]
			titleN = titleN[:-1]
			article = ""
			notes = ""
			article+=title[a]
			print(title[a])
			
			
			a = a + 1
			start = False
			print(s) 
					

		## get text
		if re.match("<div",line):
			top = re.search("top:[0-9]+px",line)
			top = re.sub("top:|px","",top.group(0))
			if 95 > int(top) > 70:
				 done = True
				 

		if re.match("<div.*font-size:8px",line):
			if re.match("^[ ]*(\"|\*|'|[0-9]+)[ ]*\)",clean(line)):
				Fussnoten = True

		if re.match("<div.*font-size:9px",line):
			if re.match("^[ ]*(\"|\*|'|[0-9]+)[ ]*\)",clean(line)):
				Fussnoten = True

		if re.match("<div.*font-size:9px",line) and Fussnoten == False and done == False and len(clean(line)) > 1:					
			article+=clean(line)
			done = True

		if re.match("<div.*font-size:8px",line) and Fussnoten == False and done == False and len(clean(line)) > 1:					
			article+=clean(line)
			done = True

		if re.match("<div.*font-size:9px",line) and Fussnoten == True and done == False and len(clean(line)) > 1:					
			notes+=clean(line)
			done = True

		if re.match("<div.*font-size:8px",line) and Fussnoten == True and done == False and len(clean(line)) > 1:					
			notes+=clean(line)
			done = True	
					
	start = True
	




