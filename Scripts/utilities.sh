#!/bin/bash


#This function converts the timestamp on the third column of a .csv.gz to a DateTime format and outputs each row of the .csv.gz to stdout
function csv_timestamp_to_datetime(){
    gzcat $1 | gawk -F "," '{OFS=","; $3=strftime("%Y-%m-%d %H:%M:%S", $3); print $0}'
}

#csv_timestamp_to_datetime sample_data/0a1efab4976c1c7487da95d444e553fe.csv.gz