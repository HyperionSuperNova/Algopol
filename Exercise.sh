#!/bin/bash

DATA=../data/timestamps

# Question a

function question_a (){
  echo "Question a"
  zcat "$DATA"//0014*.csv.gz \
  | wc -l
}
#Réponse: Le fichier a 1882 lignes.

# Question b (Résultat mis temporairement dans results car pas accés à home/data)

function gun_sort_timestamp(){
    local ego=$(basename "$DATA"/$1 .csv.gz)
    ( \
      (zcat "$DATA"/$1 \
        | head -n 1)\
        && \
          (zcat "$DATA"/$1 \
          | tail -n+2 \
          ) \
        | sort -t, -k3 \
      ) \
      | gzip -9 > ../results/sorted_$ego.csv.gz
}

function question_b (){
  echo "Question b"
  time gun_sort_timestamp 0014*.csv.gz
}

# Question c
#Réponse : Temps CPU : 0m0.038s, calculé par la commande time appliquée à la fonction gun_sort_timestamp

# Question d1

function nb_ego_prefixe (){
  pref="$1"
  ls -d "$DATA"/"$pref"*.csv.gz \
  | wc -l
}

function question_d1 (){
  echo "Question d1"
  nb_ego_prefixe 00
}

#Il y a 63 égo possédant un id commencant par 00.

#Question d2
function question_d2() {
  echo "Question d2"
  max=16
  for((i=0;i<max;i++))
  do
    x=$(printf "%x\n" $i)
    echo "Nombre d'égo commencant par $x"
    nb_ego_prefixe "$x"
  done
}

#Question e
function gun_sort_timestamp_filter_ego(){
    local pref="$1"
    local filename=""
    for ego in "$DATA"/"$pref"*.csv.gz
    do
      gun_sort_timestamp "$ego"
    done
}

function question_e (){
  echo "Question e"
  time (gun_sort_timestamp_filter_ego "00")
}
#Le temps pris par le cpu est 0m0.942s secondes

#Question f

function question_f() {
  export -f gun_sort_timestamp_filter_ego
  nohup bash -c gun_sort_timestamp_filter_ego "0" &
}
