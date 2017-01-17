#!/bin/sh
destination=49
for i in $(find ./DVJS -type f -name *.pdf);
   do echo $i;pdftohtml "$i" "$destination";sudo python order.py "$destination";python split.py "$destination";destination=$(($destination + 1))python delete_files.py; 
	
done
