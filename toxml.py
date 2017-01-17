import re
import io
import math

data = open("prax_doc_topics.txt","r")
out_all = ""
start = "<xml><topics>"
end = "</topics></xml>"
for line in data:
	i = 0
	NR = re.search("^[0-9]+",line)
	YEAR = re.search("\/[0-9]+\/",line)
	YEAR = re.sub("\/","",YEAR.group(0))
	TOPIC = re.findall("([0-9]+\.[0-9]+((E\-)[0-9])*)",line)
	
	out = "<doc><docNR>"+NR.group(0)+"</docNR>"+"<year>"+YEAR+"</year>"

	for item in TOPIC:
		if item[1].startswith("E"):
			Zahl = re.sub("E\-[0-9]","",item[0])
			Enum = re.sub("E\-","",item[1])
			Zahl = float(Zahl)
			
			Enum = int(Zahl) * -1
			
			Zahl =Zahl * math.exp(Enum)
			
		else:
			Zahl=item[0]

		t="<topic id='"+str(i)+"'>"+str(Zahl)+"</topic>"
		out+=t
		i = i+1
	out+="</doc>"
		
	out_all+=out
	
final=start+out_all+end


with io.FileIO("doc_topics.xml", "w") as file:
	file.write(final.encode("utf-8"))		
