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

def masterlayout(pagelayout):
	
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
	lenlist.append(len(clean(line)))
	return(lenlist)		
		
files = list()
for dirpath, dirnames, filenames in os.walk("./"+"test"):
    for filename in [f for f in filenames if f.endswith(".html")]:
        files.append(os.path.join(dirpath, filename))
	## Erstellt eine Liste aller .html-Files in einem Ordner

## Sortierung der List mit Pfadangaben
files.sort()

output = ""
for filepath in files:
	## initialisierung von steuerungsvariablen
	fussnotenstart = False	
	zeilenabstand = list()
	fussnotenzeichenz = 0
	fussnotenref = 0
	fussnotenref2 = 0
	lenlist = list()
	## Iteration über alle Seiten
	site = open(filepath,"r",encoding="utf-8")
	pagelayout = list()
	for zeile in site:
	## Iteration über alle Zeilen einer Seite
		if zeile.startswith("<div"):
			pagelayout.append(layout(zeile))
			breite = meanlen(zeile)
			## pagelayout: top, left, fontsize, align(fontsize,align usw.)

	masterlayout = masterlayout(pagelayout)
	breite = int(np.mean(breite))
	
	## masterlayout: fontsize, aussensteg, zeilenabstand

	layoutz = 0
	site = open(filepath,"r",encoding="utf-8")
	for line in site:
		if line.startswith("<div"):
			if len(pagelayout) > layoutz:
				zeilenabstand.append(int(pagelayout[layoutz][1]) - int(pagelayout[(layoutz-1)][1]))
			
			
			if  fussnotenstart == False and int(math.fabs(int(pagelayout[layoutz][0]) - masterlayout[1])) < 12 and len(pagelayout[layoutz]) == 4:
				## Regel für einfache Zeilen ohne Eigenschaften
				output+=clean(line)

  
			if int(pagelayout[layoutz][2]) > masterlayout[0]:
				## Regel für Überschriften
				title = clean(line)
				output+="<xml><article>"
				title = "<title>"+title+"</title><absatz>"
				output+=title

			
			if zeilenabstand[layoutz-1] == masterlayout[2] and zeilenabstand[layoutz] > masterlayout[2] + 2 and int(pagelayout[layoutz][2]) < masterlayout[0] and fussnotenstart == False:
				## Regel für den Start der Fussnoten
				fussnotenstart = True
				footnote = "<fussnotenteil><fussnote nr='"+str(fussnotenref2)+"'>"+clean(line)
				fussnotenref2 = fussnotenref2 + 1	
				output+=footnote
				continue
			if fussnotenstart == True:
				## Regel für Fussnoten
				if re.match("^[[1-9,\']{1,3}\)",clean(line)):
					output+="</fussnote>"
					output+="<fussnote nr='"+str(fussnotenref2)+"'>"+clean(line)
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
						output+="<fussnotenzeichen nr='"+str(fussnotenref)+"'>"+fussnotenzeichen[0].text+"</fussnotenzeichen>"
						fussnotenref = fussnotenref + 1
					fussnotenzeichenz = fussnotenzeichenz + 1
			if int(math.fabs(len(clean(line)) - breite)) > 10 and fussnotenstart == False and int(math.fabs(int(pagelayout[layoutz][0]) - masterlayout[1])) < 12:
				output+="</absatz><absatz>" 
			layoutz = layoutz + 1
	if fussnotenstart == True:
		output+="</fussnote></fussnotenteil></article></xml>"
	else:
		output+="<fussnotenteil/><article></xml>"

with io.FileIO("./out.xml", "w") as file:
	file.write(output.encode("utf-8"))




