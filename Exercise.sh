#!/bin/bash

# Question a

zcat ../data-timestamps/0014*.csv.gz | wc -l

# Question b (Résultat mis temporairement dans results car pas accés à home/data)

function gun_sort_timestamp(){
    local filename=$(basename ../data-timestamps/$1 .csv.gz)
    ((zcat ../data-timestamps/$1 | head -n 1) && (zcat ../data-timestamps/$1 | tail -n+2) | sort -t, -k3) | gzip -9 > ../results/sorted_$filename.csv.gz
}

# gun_sort_timestamp 0014*.csv.gz

# Question c
#Temps CPU : 0m0.038s, calculé par la commande time appliquée à la fonction gun_sort_timestamp

