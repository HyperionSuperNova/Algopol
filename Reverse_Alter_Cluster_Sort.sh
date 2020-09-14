#!/bin/bash

DATA=../data-timestamps


function rev_gun_sort_timestamp(){
    local ego=$(basename "../data-timestamps"/$1 .csv.gz)
    ( \
      (zcat "../data-timestamps"/$1 \
        | head -n 1)\
        && \
          (zcat "../data-timestamps"/$1 \
          | tail -n+2 \
          ) \
        | sort -r -t, -k3 \
      ) \
      | gzip -9 > /home/nabil/results/Alter-cluster-timestamp-reverse-sorted/$ego.csv.gz
}

function rev_gun_sort_all_ego(){
    for ego in $(ls "../data-timestamps")
    do
      rev_gun_sort_timestamp $(basename "$ego")
    done
}

sort_all() {
  export -f rev_gun_sort_timestamp
  export -f rev_gun_sort_all_ego	
  nohup bash -c rev_gun_sort_all_ego &
}

sort_all
