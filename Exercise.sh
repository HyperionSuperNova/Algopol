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

ls -d ../data-timestamps/00* | wc -l

#Il y a 63 égo possédant un id commencant par 00.

#Question d2
echo "Question d2"
max=16
for((i=0;i<max;i++))
do
  x=$(printf "%x\n" $i)
  echo "Nombre d'égo commencant par $x"
  ls -d ../data-timestamps/$x* | wc -l
done

#Question e
echo "Question e"
function gun_sort_timestamp_filter_ego(){
    local filename=""
    for ego in $(ls -d ../data-timestamps/$1*)
    do 
      filename=$(basename $ego .csv.gz)
      ((zcat $ego | head -n 1) && (zcat $ego | tail -n+2) | sort -t, -k3) | gzip -9 > ../results/sorted_$filename.csv.gz
    done
}

time (gun_sort_timestamp_filter_ego "00")
#Le temps pris par le cpu est 0m0.942s secondes

#Question f

export -f gun_sort_timestamp_filter_ego

nohup bash -c gun_sort_timestamp_filter_ego "0" &


