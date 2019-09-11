#!/bin/bash
echo "source: $1"
echo "year: $2"

s=$1
s=/opt/data/company_announcement_pdf/report/
dest=$2
dest=/opt/data/company_announcement_pdf/json/
y=$3
y=2019-01-02

for d in $s$y* ; do
	day_source="$d"
	day_dest="${d/$s/$dest}"    
	python pdf2json/pdf2json.py -s $day_source -d $day_dest -n 2
done
