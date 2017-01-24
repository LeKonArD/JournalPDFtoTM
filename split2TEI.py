import lxml
from lxml import etree
import re
import io
import os
import sys
from io import StringIO
from collections import Counter
import numpy as np
import math as math

def clean(text):
	## Routine zum Entfernen von Markup
	##start tags
	text = re.sub("<\s*([A-Za-z_]\w*)\s*([^\>]+)>","",text)
	##end tags
	text = re.sub("<\/(span|div)","",text)
	##Rest
	text = re.sub(">","",text)
	return text

def getmasterlayout(pagelayout):
	
	## Routine um Referenzwerte zom Layout zu erzeugen
	## hauptsächlich verwendete Schriftgröße auf Seite
	all_fontsize = list()
	for font in pagelayout:
		all_fontsize.append(font[2])
		
	masterfontsize = Counter(all_fontsize)
	masterfontsize = int(masterfontsize.most_common()[0][0])

	## Außensteg
	all_left = list()
	for left in pagelayout:
		all_left.append(int(left[0]))

	aussensteg = int(np.mean(all_left))
	

	## Zeilenabstand
	abstand = list()
	z = 0
	while len(pagelayout)-1 > z:
		a = z + 1
		abstand.append(int(pagelayout[a][1]) - int(pagelayout[z][1]))
		z = z + 1
	zeilenabstand = int(np.mean(abstand))

	masterlayout = list()
	masterlayout.append(masterfontsize)
	masterlayout.append(aussensteg)
	masterlayout.append(zeilenabstand)
		
	return(masterlayout)


def layout(line):
	## Routine zum extrahieren von Layout-Information

	## Einlsesen in lxml
	layout = list()
	tree = etree.parse(io.StringIO(line))
	divstyle = tree.xpath('/div/@style')

	left = re.findall("left:[0-9]*px",str(divstyle))
	left = re.sub("left:|px|\[|\]|'","",str(left))
	
	top = re.findall("top:[0-9]*px",str(divstyle))
	top = re.sub("top:|px|\[|\]|'","",str(top))
	
	layout.append(str(left))
	layout.append(str(top))

	spanscount = tree.xpath("count(/div/span)")
	z = 1
	while spanscount >= z:
		xpathspan = "/div/span["+str(z)+"]/@style"
		spanstyle = tree.xpath(xpathspan)
		
		fontsize = re.findall("font\-size:[0-9]+px",str(spanstyle))
		fontsize = re.sub("font\-size:|px|\[|\]|\'","",str(fontsize))
		
		align = re.findall("align\:[a-z]+;color",str(spanstyle))
		align = re.sub("align\:|;color|\[|\]|\'","",str(align))
		layout.append(str(fontsize))
		layout.append(str(align))
		
		z = z + 1
	
	return(layout) 

def meanlen(line):
	## zählt Zeichen pro Zeile um Absätze zu erkennen.
	lens.append(len(clean(line)))
	return(lens)		
		
files = list()
for dirpath, dirnames, filenames in os.walk("./"+"test"):
    for filename in [f for f in filenames if f.endswith(".html")]:
        files.append(os.path.join(dirpath, filename))
	## Erstellt eine Liste aller .html-Files in einem Ordner

## Sortierung der List mit Pfadangaben
files.sort()

firstsite = list()
titleout = "dummy"
output = ""
satzende = [".","!","?"]
absatzende = False
fussnotenref2 = 0
seitenummer = 0
fussnotenzeichenz = 0
fussnotenref = 0
for filepath in files:
	## initialisierung von steuerungsvariablen
	img = False
	zitatstart = False
	seitenummer = seitenummer + 1
	titleart = list()
	fussnotenstart = False	
	zeilenabstand = list()
	
	
	lens = list()
	## Iteration über alle Seiten
	site = open(filepath,"r",encoding="utf-8")
	pagelayout = list()
	for zeile in site:
	## Iteration über alle Zeilen einer Seite
		if zeile.startswith("<div"):
			pagelayout.append(layout(zeile))
			breite = meanlen(zeile)
			## pagelayout: top, left, fontsize, align(fontsize,align usw.)
		
		if re.match("<img.*",zeile):
			img = True
			continue
		if img == True and re.match("<div",zeile):
			top = re.search("top:[0-9]+px",zeile)
			top = re.sub("top:|px","",top.group(0))
			if 235 > int(top) > 108:
				if clean(zeile)[0].isupper() and clean(zeile)[1].islower() :
					
					titleart.append(clean(zeile))
					firstsite.append(filepath)
					img = False 
		img = False
	masterlayout = getmasterlayout(pagelayout)
	if filepath in firstsite:
		masterfirstsite = masterlayout
	breite = int(np.mean(breite))
	
	## masterlayout: fontsize, aussensteg, zeilenabstand

	layoutz = 0
	site = open(filepath,"r",encoding="utf-8")
	
	for line in site:
		
	## generating output
		if line.startswith("<img") and filepath not in firstsite:
			fussnotenstart = False
			output+= "<seite nr=\""+str(seitenummer)+"\"><text><p>"
			

		if line.startswith("<div"):
			
			if len(pagelayout) > layoutz:
				zeilenabstand.append(int(pagelayout[layoutz][1]) - int(pagelayout[(layoutz-1)][1]))
		#	if zitatstart == True and fussnotenstart == False and titlestmt == False and int(pagelayout[layoutz][2]) < masterlayout[0]:
		#		if int(math.fabs(int(pagelayout[layoutz][0]) - masterlayout[1])) > 15:
		#			output+= clean(line)
		#		else:
		#			output+="</zitat>"
		#			zitatstart = False
			
			print(int(math.fabs(int(pagelayout[layoutz][0]) - masterlayout[1])))
			if  fussnotenstart == False and int(math.fabs(int(pagelayout[layoutz][0]) - masterlayout[1])) < 15 and len(pagelayout[layoutz]) == 4:
				## Regel für einfache Zeilen ohne Eigenschaften
				output+=clean(line)
			
  			
			if int(pagelayout[layoutz][2]) > masterlayout[0] and filepath in firstsite:
				## Regel für Überschriften
				seitenummer = 1
				fussnotenzeichenz = 0
				fussnotenref = 0
				fussnotenref2 = 0
				output+="</TEI>"
				print(titleout)
				with io.FileIO("./"+titleout+".xml", "w") as file:
					file.write(output.encode("utf-8"))
				output = ""
				title = clean(line)
				titleout = title
				TEIheader="<teiHeader><fileDesc><titleStmt><title>"+title+"</title></titleStmt><publicationStmt><p>ToDo</p></publicationStmt><sourceDesc><p>ToDo</p></sourceDesc></fileDesc></teiHeader>"
				output+="<TEI xmlns=\"http://www.tei-c.org/ns/1.0\" xml:lang=\"de\">"+TEIheader+"<seite nr=\""+str(seitenummer)+"\"><text>"
				TEIheader="<teiHeader><fileDesc><titleStmt><title>"+title+"</title></titleStmt><publicationStmt><p></p></publicationStmt><sourceDesc></sourceDesc></fileDesc></teiHeader>"
				title = "<title level=\"a\" type=\"mean\">"+title+"</title>"
				output+=title
				titlestmt = True
				subtitle = True
				
			if subtitle == True and int(pagelayout[layoutz][2]) > masterlayout[0] and filepath in firstsite:
				output += "<subtitle>"+clean(line)+"</subtitle>"
				subtitle = False
				



			if re.match("Von\s+.+\(.+\)",clean(line)) and titlestmt == True:
				## Regeln für Autoren
				autor = re.sub("Von|\(.*\)","",clean(line))
				ort = re.search("\(.*\)",clean(line))
				output+="<author>"+autor+"</author>"+"<ort>"+ort.group(0)+"</ort><p>"
				titlestmt = False




			
		#	if fussnotenstart == False and int(math.fabs(int(pagelayout[layoutz][0]) - masterlayout[1])) > 15 and zitatstart == False and titlestmt == False and int(pagelayout[layoutz][2]) <= masterlayout[0]:
				## Regeln für Zitateanfänge
		#		zitatstart = "<zitat>"+clean(line)
		#		output+= zitatstart
		#		zitatstart == True 
			

			if zeilenabstand[layoutz-1] <= masterfirstsite[2] and zeilenabstand[layoutz] > masterfirstsite[2] + 2 and int(pagelayout[layoutz][2]) < masterfirstsite[0] and fussnotenstart == False and titlestmt == False and subtitle == False:
				## Regel für den Start der Fussnoten
				fussnotenstart = True
				if re.match("^[[1-9,\']{1,3}\)",clean(line)):
					footnote = "</p></text><fussnotenteil><note anchored=\"true\" targedEnd='"+str(fussnotenref2)+"'>"+clean(line)
					fussnotenref2 = fussnotenref2 + 1
				else:
					footnote = "</p></text><fussnotenteil><note anchored=\"true\" targedEnd='"+str(fussnotenref2-1)+"'>"+clean(line)	
				output+=footnote
				continue
			
			if fussnotenstart == True:
				## Regel für Fussnoten
				if re.match("^[[1-9,\']{1,3}\)",clean(line)):
					output+="</note>"
					output+="<note anchored=\"true\" targetEnd='"+str(fussnotenref2)+"'>"+clean(line)
					fussnotenref2 = fussnotenref2 + 1
				else:
					output+=clean(line)

			if fussnotenstart == False and len(pagelayout[layoutz]) > 4:
				## Regeln für Fussnotenzeichen
				tree = etree.parse(io.StringIO(line))
				spanstyle = tree.xpath('/div/span/@style')
				
				spanscount = tree.xpath("count(/div/span)")
				fussnotenzeichenz = 1
				while spanscount >= fussnotenzeichenz:
					xpathspan = "/div/span["+str(fussnotenzeichenz)+"]/@style"
					spanstyle = tree.xpath(xpathspan)
		
					fontsize = re.findall("font\-size:[0-9]+px",str(spanstyle))
					fontsize = re.sub("font\-size:|px|\[|\]|\'","",str(fontsize))
		
					align = re.findall("align\:[a-z]+;color",str(spanstyle))
					align = re.sub("align\:|;color|\[|\]|\'","",str(align))
					if align == "super" and int(fontsize) < masterlayout[0]:
						
						fussnotenzeichen = tree.xpath("/div/span["+str(fussnotenzeichenz)+"]")
						output+="<ref type=\"noteAnchor\" target='"+str(fussnotenref)+"'/>"
						fussnotenref = fussnotenref + 1
					fussnotenzeichenz = fussnotenzeichenz + 1
				output+=clean(line)



			if int(math.fabs(len(clean(line)) - breite)) > 10 and fussnotenstart == False and int(math.fabs(int(pagelayout[layoutz][0]) - masterlayout[1])) < 12 and clean(line)[(len(clean(line))-2)] in satzende:
				## Regel für Absätze
				absatzende = True
				output+="</p><p>" 
			layoutz = layoutz + 1
	if fussnotenstart == True:
		output+="</note></fussnotenteil></seite>"
	else:
		output+="</p></text></seite>"

with io.FileIO("./out.xml", "w") as file:
	file.write(output.encode("utf-8"))




