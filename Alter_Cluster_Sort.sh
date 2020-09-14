#!/bin/bash

DATA=../data-timestamps


function gun_sort_timestamp(){
    local ego=$(basename "../data-timestamps"/$1 .csv.gz)
    ( \
      (zcat "../data-timestamps"/$1 \
        | head -n 1)\
        && \
          (zcat "../data-timestamps"/$1 \
          | tail -n+2 \
          ) \
        | sort -t, -k3 \
      ) \
      | gzip -9 > /home/nabil/results/Alter-cluster-timestamp-sorted/$ego.csv.gz
}

function gun_sort_all_ego(){
    for ego in $(ls "../data-timestamps")
    do
      gun_sort_timestamp $(basename "$ego")
    done
}

sort_all() {
  export -f gun_sort_timestamp
  export -f gun_sort_all_ego	
  nohup bash -c gun_sort_all_ego &
}

sort_all
