#!/bin/bash

# Question a

echo "Question a"
zcat ../data-timestamps/0014*.csv.gz | wc -l
#Réponse: Le fichier a 1882 lignes.

# Question b (Résultat mis temporairement dans results car pas accés à home/data)

echo "Question b"
function gun_sort_timestamp(){
    local filename=$(basename ../data-timestamps/$1 .csv.gz)
    ((zcat ../data-timestamps/$1 | head -n 1) && (zcat ../data-timestamps/$1 | tail -n+2) | sort -t, -k3) | gzip -9 > ../results/sorted_$filename.csv.gz
}
time gun_sort_timestamp 0014*.csv.gz

# Question c
#Réponse : Temps CPU : 0m0.038s, calculé par la commande time appliquée à la fonction gun_sort_timestamp

# Question d1

echo "Question d1"

zcat ../data-timestamps/0014*.csv.gz | awk -F , '{if ($1 ~ /^00/) print;}' | wc -l


#Il y a 1494 égo possédant un id commencant par 00.

#Question d2
echo "Question d2"
max=16
for((i=0;i<max;i++))
do
  x=$(printf "%x\n" $i)
  zcat ../data-timestamps/0014*.csv.gz | awk -F , -v var_awk="$x" '{if ($1 ~ ("^" var_awk)) print;}' | wc -l
done

#Question e
echo "Question e"
function gun_sort_timestamp_filter_ego(){
    local filename=$(basename ../data-timestamps/$1 .csv.gz)
    ((zcat ../data-timestamps/$1 | head -n 1) && (zcat ../data-timestamps/$1 | tail -n+2 | awk -F , -v var_awk="$2" '{if ($1 ~ ("^" var_awk)) print;}' | sort -t, -k3)) | gzip -9 > ../results/sorted_filtered$2_$filename.csv.gz
}

time (gun_sort_timestamp_filter_ego 0014*.csv.gz "00")
#Le temps pris par le cpu est 0m0.023 secondes

#Question f

time gun_sort_timestamp_filter_ego 0014*.csv.gz "0" 

#Le temps pris par le cpu est 0m0.031 secondes

